from flask import Flask, request
import asyncio
import os

from downloader import Downloader
import ffmpegprocess
from s3 import S3
from postgres import Postgres

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)


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



    dl = Downloader(max_tasks = 50, max_time = 999)
    video_names = dl.async_download(video_urls)

    output_video = ffmpegprocess.concatenate(video_names, width, height, fps)

    s3 = S3(
        bucket = bucket,
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )
    s3.upload(output_video)

    postgres = Postgres(
        host = os.getenv("HOST"),
        user = os.getenv("USER"),
        password = os.getenv("PASSWORD"),
        database = os.getenv("DB_NAME")
    )
    name = "Video concatenation"
    description = ""
    result = f"https://{bucket}.s3.amazonaws.com/{output_video}"
    postgres.create_event_record(name, description, request_data, result)

    cleanup(video_names, output_video)
    return "Success!"


def cleanup(video_names, output_video):
    for file in video_names:
        os.remove(file)
    os.remove(output_video)


if __name__ == '__main__':
    app.run(debug=True)
