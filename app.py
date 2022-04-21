from flask import Flask, request
import asyncio
import os
import s3
import downloader
import ffmpegprocess
import postgres

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

    video_names = asyncio.run(downloader.download(video_urls))[1]
    output_video = ffmpegprocess.concatenate(video_names, width, height, fps)
    s3.upload(output_video, bucket)
    postgres.create_record(request_data, output_video)
    cleanup(video_names, output_video)

    return "Success!"


def cleanup(video_names, output_video):
    for file in video_names:
        os.remove(file)
    os.remove(output_video)


if __name__ == '__main__':
    app.run(debug=True)
