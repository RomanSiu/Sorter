from pathlib import Path
from sys import argv
from threading import Thread
from os import mkdir
from time import time
import shutil

timer = time()

CATEGORIES = {"Images": [".jpg", ".gif", ".png", ".svg"],
              "Audio": [".mp3", ".wav", ".flac", ".wma", ".ogg", ".amr"],
              "Documents": [".doc", ".docx", ".txt", ".rtf", ".pdf", ".epub", ".xls", ".xlsx", ".ppt", ".pptx"],
              "Video": [".avi", ".mp4", ".wmv", ".mov", ".mkv"],
              "Archives": [".zip", ".tar", ".gztar", ".bztar"]
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


def move_file(file, new_file_path, param=False):
    thread1 = Thread(target=shutil.move, args=(file, new_file_path))
    thread1.start()
    if param:
        threads.append(thread1)


def del_dirs(path):
    for directory in path.iterdir():
        if directory.is_dir() and directory.name in folder_lst:
            continue
        else:
            shutil.rmtree(directory)


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


def handler(path):
    for file in path.iterdir():
        if file.is_dir() and file.name not in folder_lst:
            handler(file)
            thread = Thread(target=dir_handler, args=(file, ))
            thread.start()
            threads.append(thread)
            continue
        elif file.is_dir() and file.name in folder_lst:
            continue


def dir_handler(path):
    lst = [i for i in path.iterdir()]
    n = 0
    for file in lst:
        if file.is_dir():
            continue
        cat = get_category(file)
        new_path = make_file_path(file, cat)
        new_path = same_file_check(new_path)
        n += 1
        if n == len(lst):
            move_file(file, new_path, param=True)
            continue
        move_file(file, new_path)


if __name__ == "__main__":
    try:
        arg = argv[1]
    except IndexError:
        print("Use path as an argument")
        exit()
    main_path = Path(" ".join(argv[1:]))
    main_thread = Thread(target=handler, args=(main_path,))
    main_thread.start()
    threads.append(main_thread)
    dir_handler(main_path)
    [dr.join() for dr in threads]
    del_dirs(main_path)
    print(time() - timer)
