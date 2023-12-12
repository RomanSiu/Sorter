import concurrent.futures
from pathlib import Path
from sys import argv
from threading import Thread
from os import mkdir, rename, listdir
from time import time
import shutil

timer = time()

CATEGORIES = {"Images": [".jpg", ".gif", ".png", ".svg"],
              "Audio": [".mp3", ".wav", ".flac", ".wma", ".ogg", ".amr"],
              "Documents": [".doc", ".docx", ".txt", ".rtf", ".pdf", ".epub", ".xls", ".xlsx", ".ppt", ".pptx"],
              "Video": [".avi", ".mp4", ".wmv", ".mov", ".mkv"],
              "Archives": [".zip", ".tar", ".gztar", ".bztar", ".xztar"]
              }

folder_lst = ["Images", "Audio", "Documents", "Video", "Archives", "Others"]
threads = []


def get_category(file):
    suf = file.suffix.lower()
    for cat, ext in CATEGORIES.items():
        if suf in ext:
            return cat
    return "Others"


def make_file_path(file, cat):
    file_path = str(main_path) + fr"\{cat}\\"
    if not Path(file_path).is_dir():
        mkdir(file_path)
    return file_path + file.name


def move_file(file, new_file_path):
    thread = Thread(target=rename, args=(file, new_file_path))
    thread.start()
    threads.append(thread)
    # rename(file, new_file_path)


def del_dirs(path):
    for directory in path.iterdir():
        if directory.is_dir() and directory.name in folder_lst:
            continue
        else:
            while True:
                dir_list = list(directory.iterdir())
                if len(dir_list) == 0:
                    directory.rmdir()
                    break


def same_file_check(file):
    num = 1
    while True:
        file_path = Path(file)
        if file_path.is_file():
            suf = file_path.suffix
            file_name = file_path.name[:-(len(suf))] if num <= 1 else file_path.name[:-(len(suf))-3]
            new_file_name = file_name + f"({num})" + suf
            file = file[:-(len(file_path.name))] + new_file_name
            num += 1
        else:
            break
    return file


def iter_dir(path):
    dirs = []
    for file in path.iterdir():
        if file.is_dir() and file.name not in folder_lst:
            res = iter_dir(file)
            if len(listdir(file)) == 0:
                file.rmdir()
                continue
            dirs.append(file)
            [dirs.append(r) for r in res]
            continue
        elif file.is_dir() and file.name in folder_lst:
            continue
    return dirs


def dir_handler(path):
    for file in path.iterdir():
        print(file)
        if file.is_dir():
            continue
        cat = get_category(file)
        new_path = make_file_path(file, cat)
        new_path = same_file_check(new_path)
        move_file(file, new_path)


def handler(path):
    dirs_lst = iter_dir(path)
    dirs_lst.append(path)

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=50)
    futures = [executor.submit(dir_handler, path) for path in dirs_lst]
    done, not_done = concurrent.futures.wait(futures, return_when=concurrent.futures.ALL_COMPLETED)
    print("complete")
        

if __name__ == "__main__":
    # try:
    #     arg = argv[1]
    # except IndexError:
    #     print("Use path as an argument")
    #     exit()
    # main_path = Path(" ".join(argv[1:]))
    main_path = Path(r"C:\Users\User\Desktop\garbage_test")
    handler(main_path)
    print(time() - timer)
