from asyncio import Semaphore, gather, run, wait_for
import aiofiles
from aiohttp.client import ClientSession
from uuid import uuid4


# asynchronously downloads videos and thumbnail with given urls from a list
# returns a list with names of downloaded videos
async def download(video_urls):
    max_tasks = 50
    max_time = 999
    tasks = []
    sem = Semaphore(max_tasks)

    video_names = []

    async with ClientSession() as sess:
        for url in video_urls:
            # Create a different file name each iteration
            dest_file = str(uuid4()) + url[url.rfind('.'):]
            video_names.append(dest_file)
            tasks.append(
                # Wait max MAX_TIME seconds for each download
                wait_for(
                    download_one(url, sess, sem, dest_file),
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
