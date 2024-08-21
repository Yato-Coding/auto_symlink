import os
import time

interval = 10

src_dir_single_file = './src/single_file'
src_dir_multi_file = './src/multi_file'

dst_dir_single_file = './dst/single_file'
dst_dir_multi_file = './dst/multi_file'

single_file_modification_index = {}
multi_file_modification_index = {}

def init_file_modification_indices(single_src_dir, multi_src_dir):
    for i in range(2):
        if i == 0:
            src_dir = single_src_dir
        else:
            src_dir = multi_src_dir

        for root, dirs, files in os.walk(src_dir):
            if root == src_dir:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                file_mod_time = os.path.getmtime(file_path)

                if i == 0:
                    single_file_modification_index[file_path] = file_mod_time
                else:
                    multi_file_modification_index[file_path] = file_mod_time


def find_new_files(src_dir, file_modification_index):
    new_files = set()
    for root, _, files in os.walk(src_dir):
        if root == src_dir:
            continue

        for file in files:
            try:
                file_path = os.path.join(root, file)
                file_mod_time = os.path.getmtime(file_path)

                if file_path not in file_modification_index:
                    file_modification_index[file_path] = file_mod_time
                    new_files.add(file_path)
            
                elif file_modification_index[file_path] != file_mod_time:
                    file_modification_index[file_path] = file_mod_time
                    new_files.add(file_path)

            except FileNotFoundError:
                print("File has been deleted: " + file_path)
                del file_modification_index[file_path]

    return new_files

def symlink_single_file(src_dir, dst_dir):
    # folder structure is as follows:
    # src_dir: ./src/placeholder_name/file_name
    # dst_dir: ./dst/file_name/file_name

    file_name = os.path.basename(src_dir)
    dst_folder_path = os.path.join(dst_dir, file_name)
    os.makedirs(dst_folder_path, exist_ok=True)

    dst_symlink_path = os.path.join(dst_folder_path, file_name)
    os.symlink(src_dir, dst_symlink_path)
    print("Symlink created: " + src_dir + " -> " + dst_symlink_path)

def symlink_multi_file(src_dir, dst_dir):
    # folder structure is as follows:
    # src_dir: ./src/placeholder_name/bunch of files
    # dst_dir: ./dst/placeholder_name/bunch of files
    # subdirs get copied as well 

    # gets the "placeholder_name" + any eventual suffix in case of subdirs, does NOT include the file name
    dst_dir_split = src_dir.split(os.path.sep) 
    dir_name = ""
    for i in range(3, len(dst_dir_split)-1):
        dir_name = os.path.join(dir_name, dst_dir_split[i])

    dst_folder_path = os.path.join(dst_dir, dir_name)
    os.makedirs(dst_folder_path, exist_ok=True)

    file_name = os.path.basename(src_dir)
    dir_symlink_name = os.path.join(dst_folder_path, file_name)
    os.symlink(src_dir, dir_symlink_name)
    print("Symlink created: " + src_dir + " -> " + dir_symlink_name)


def main():
    init_file_modification_indices(src_dir_single_file, src_dir_multi_file)
    while True:
        for file_path in find_new_files(src_dir_single_file, single_file_modification_index):
            symlink_single_file(file_path, dst_dir_single_file)

        for file_path in find_new_files(src_dir_multi_file, multi_file_modification_index):
            print("File: " + file_path)
            symlink_multi_file(file_path, dst_dir_multi_file)
        time.sleep(interval)

if __name__ == "__main__":
    main()
