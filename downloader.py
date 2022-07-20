from threading import Thread
from time import sleep
from typing import Callable, List, Generator
from requests import get
import sys, os

_threads: List[Thread] = []

def make_thread(join: bool=True) -> Callable:
    def __decorator__(func: Callable) -> Callable:
        def __wrapper__(*args, **kwargs) -> None:
            daemon: Callable = lambda: True if not join else False
            thread: Thread = Thread(
                target=func,
                args=args,
                kwargs=kwargs,
                daemon=daemon()
            )
            thread.start()
            if join: thread.join()
            else: _threads.append(thread)
        return __wrapper__
    return __decorator__

@make_thread(join=False)
def downloader(url: str, limit_rate: float=0.01, block_size: int=8192) -> str:
    print(f"Download speed is {round(((1 / limit_rate) * block_size / 1000) / 1000, 3)} MB/s")
    try:
        local_filename = url.split('/')[-1].replace('%', '')
        print(f"{local_filename} is downloading ...")
        with get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=block_size):
                    f.write(chunk)
                    sleep(limit_rate)
        return local_filename
    except Exception: pass

def _reader(download_link_file: str) -> Generator:
    with open('./' + download_link_file, mode='r') as dlf:
        for link in dlf: yield link

def main(threads: int=4, time_out: int=2) -> None:
    download_link_file: str = ''
    for i, file in enumerate(os.listdir()):
        if file.endswith('.txt'):
            download_link_file = file
            break
        else:
            if not download_link_file and i == len(os.listdir()):
                raise FileNotFoundError('Download links should be on current path!')
    link: Generator = _reader(download_link_file)
    while True:
        try:
            for _ in range(threads): downloader(*next(link).split()); time_out(2)
            for t in _threads: t.join()
        except StopIteration: print('End!'); break

if __name__ == '__main__':
    try: main()
    except KeyboardInterrupt: sys.exit()
