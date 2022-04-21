import asyncio
import aiofiles
from aiohttp.client import ClientSession
from uuid import uuid4

class Downloader:
    def __init__(self, max_tasks, max_time):
        self.max_tasks = max_tasks
        self.max_time = max_time


    # asynchronously downloads files with given urls from a list
    # returns a list with names of downloaded files
    def async_download(self, url_list):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        return asyncio.run(self.download_multiple(url_list))[1]


    async def download_multiple(self, url_list):
        tasks = []
        sem = asyncio.Semaphore(self.max_tasks)

        file_names = []

        async with ClientSession() as sess:
            for url in url_list:
                # Create a different file name each iteration
                dest_file = str(uuid4()) + url[url.rfind('.'):]
                file_names.append(dest_file)
                tasks.append(
                    # Wait max MAX_TIME seconds for each download
                    asyncio.wait_for(
                        self.download_one(url, sess, sem, dest_file),
                        timeout=self.max_time,
                    )
                )
            return await asyncio.gather(*tasks), file_names


    # async function being used in download_multiple()
    async def download_one(self, url, sess, sem, dest_file):
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
