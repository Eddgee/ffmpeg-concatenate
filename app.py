from flask import Flask, request
import ffmpeg
import boto3
from botocore.exceptions import ClientError
import psycopg2

import asyncio
from asyncio import Semaphore, gather, run, wait_for
import aiofiles
from aiohttp.client import ClientSession

from datetime import datetime
import json
import os
from uuid import uuid4

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@app.route('/video/', methods=['POST'])
def video():
    # POST request body should contain JSON following this pattern:
    """
    body: {
    video_urls: string[] : required (minimum 2)
    width: int : required // width of output video
    height: int : required // height of output video
    fps: int : required // fps of output video
    """
    request_data = request.get_json()
    video_urls = request_data["video_urls"]
    width = request_data["width"]
    height = request_data["height"]
    fps = request_data["fps"]

    bucket = os.getenv("BUCKET")

    video_names = run(download(video_urls))[1]
    output_video = ffmpeg_process(video_names, width, height, fps)
    upload(output_video, bucket)
    sql(request_data, output_video)
    cleanup(video_names, output_video)

    return "Success!"


# asynchronously downloads videos and thumbnail with given urls from a list
# returns a list with names of downloaded videos called 'video_names'
async def download(pdf_list):
    max_tasks = 50
    max_time = 999
    tasks = []
    sem = Semaphore(max_tasks)

    video_names = []

    async with ClientSession() as sess:
        for pdf_url in pdf_list:
            # Create a different file name each iteration
            dest_file = str(uuid4()) + pdf_url[pdf_url.rfind('.'):]
            video_names.append(dest_file)
            tasks.append(
                # Wait max MAX_TIME seconds for each download
                wait_for(
                    download_one(pdf_url, sess, sem, dest_file),
                    timeout=max_time,
                )
            )
        return await gather(*tasks), video_names


# async function being used in download()
async def download_one(url, sess, sem, dest_file):
    async with sem:
        print(f"Downloading {url}")
        async with sess.get(url) as res:
            content = await res.read()

        # Check everything went well
        if res.status != 200:
            print(f"Download failed: {res.status}")
            return

        async with aiofiles.open(dest_file, "+wb") as f:
            await f.write(content)


# concatenates a list of videos into one with given width, height and fps
# name of the output video is uuid-generated
def ffmpeg_process(video_names, width, height, fps):
    videos = [ffmpeg.input(vid) for vid in video_names]
    data = [videos[i//2].video.filter('scale', w=width, h=height)
                .filter('setsar', sar=width/height).filter('fps', fps=fps)
            if i % 2 == 0 else videos[i // 2].audio for i in range(len(videos) * 2)]
    joined = ffmpeg.concat(*data, v=1, a=1).node
    v3 = joined[0]
    a3 = joined[1]

    out_filename = f"{uuid4()}.mp4"
    out = ffmpeg.output(v3, a3, out_filename)
    out.run()
    return out_filename


# uploads video to s3 bucket
def upload(output_video, bucket):
    s3 = boto3.client('s3')
    try:
        s3.upload_file(output_video, bucket, output_video, ExtraArgs={'ACL': 'public-read'})
    except ClientError as e:
        print("An error while working with boto3: ", e)


# creates a record in PostgreSQL events table
# name (varchar), description (varchar), meta (json), result (json), created_at (timestamp)
def sql(meta, output_video):
    try:
        connection = psycopg2.connect(
            host=os.getenv("HOST"),
            user=os.getenv("USER"),
            password=os.getenv("PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO events VALUES ('Video concatenation', '', '{json.dumps(meta)}', 
                '{json.dumps({"link": f"https://ffmpeg-video-examples.s3.amazonaws.com/{output_video}"})}', 
                '{datetime.now()}');"""
            )
    except Exception as e:
        print("An error while working with PostgreSQL: ", e)
    finally:
        if connection:
            connection.close()


def cleanup(video_names, output_video):
    for file in video_names:
        os.remove(file)
    os.remove(output_video)


if __name__ == '__main__':
    app.run(debug=True)
