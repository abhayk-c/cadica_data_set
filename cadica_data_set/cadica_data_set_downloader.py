import os
import asyncio
from kaggle.api.kaggle_api_extended import KaggleApi

class CadicaDataSetDownloader:

    def __init__(self, dir_path=None):
        self.dir_path = dir_path
        if self.dir_path is not None and not os.path.isdir(dir_path):
            raise FileNotFoundError("Please supply a valid directory path destination for the cadica set download.")

    async def download_data_set(self, callback):
        api = KaggleApi()
        dataset_name = "abhaycuram/cadica-data-set"
        result = await asyncio.to_thread(api.dataset_download_cli, dataset=dataset_name, path=self.dir_path, unzip=True)
        print("Continuing here?")
        callback(result)

    def download_complete_callback(status: bool):
        if status == True:
            print("download succeeded")
        else:
            print("download failed")

async def main():
    print("Starting the main program")
    cadica_downloader = CadicaDataSetDownloader()
    await cadica_downloader.download_data_set(CadicaDataSetDownloader.download_complete_callback)

asyncio.run(main())
print("Main thread execution continuing....")




