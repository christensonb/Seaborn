""" This module contains helper functions for manipulating files """
__author__ = 'Ben Christenson'
__date__ = "10/7/15"
import os
import shutil
import hashlib
import time
import inspect
import json

if os.name == 'posix':  # mac
    TRASH_PATH = '/'.join(os.getcwd().split('/')[:3] + ['.Trash'])
else:
    TRASH_PATH = '.'  # todo implement for other os


def mkdir(path):
    if os.path.exists(os.path.abspath(path)):
        return
    path_directories = os.path.abspath(path).replace('\\', '/').split('/')
    full_path = ''
    for directory in path_directories[1:]:
        full_path += '/' + directory
        if not os.path.exists(full_path):
            os.mkdir(full_path)


def mkdir_for_file(filename):
    mkdir(os.path.split(filename)[0])


def clear_path(path):
    """
        This will move a path to the Trash folder
    :param path: str of the path to remove
    :return:     None
    """
    from time import time
    if TRASH_PATH == '.':
        shutil.rmtree(path, ignore_errors=True)
    else:
        shutil.move(path,
                    '%s/%s_%s' % (TRASH_PATH, os.path.basename(path), time()))


def get_filename(filename, trash=False):
    if trash:
        filename = os.path.join(TRASH_PATH, filename)

    full_path = os.path.abspath(filename)
    if not os.path.exists(os.path.split(full_path)[0]):
        mkdir(os.path.split(full_path)[0])
    if os.path.exists(full_path):
        os.remove(full_path)
    return full_path


def find_folder(folder_name, path=None):
    frm = inspect.currentframe().f_back
    path = path or os.path.split(frm.f_code.co_filename)[0] or os.getcwd()
    for i in range(100):
        try:
            if os.path.exists(os.path.join(path, folder_name)):
                return os.path.join(path, folder_name)
            path = os.path.split(path)[0]
            if len(path) <= 1:
                break
        except Exception as e:
            return None
    if os.path.exists(os.path.join(path, folder_name)):
        return os.path.join(path, folder_name)

def find_file(file, path=None):
    frm = inspect.currentframe().f_back
    if frm.f_code.co_name == 'run_code':
        frm = frm.f_back
    path = path or os.path.split(frm.f_code.co_filename)[0] or os.getcwd()
    original_path = path
    for i in range(100):
        try:
            file_path = os.path.abspath(os.path.join(path, file))
            if os.path.exists(file_path):
                return file_path
            path = os.path.split(path)[0]
            if len(path) <= 1:
                break
        except Exception as e:
            break;
    if os.path.exists(os.path.join(path, file)):
        return os.path.join(path, file)
    raise Exception("Failed to find file: %s in the folder hierachy: %s"%(file,original_path))

def sync_folder(source_folder, destination_folder, soft_link='folder',
                only_files=False):
    clear_path(destination_folder)
    if os.name == 'posix' and soft_link == 'folder':
        mkdir_for_file(destination_folder)
        os.system('ln -s "%s" "%s"' % (source_folder, destination_folder))
        return

    for root, subs, files in os.walk(source_folder):
        for file in files:
            file = os.path.join(root, file)
            copy_file(file, file.replace(source_folder, destination_folder),
                      soft_link=bool(soft_link))
        if only_files:
            break
        for sub in subs:
            mkdir(sub.replace(source_folder, destination_folder))


def _md5_of_file(context, sub_string):
    """
        This will return the md5 of the file in sub_string
    :param context:
    :param sub_string: str of the path or relative path to a file
    :return: str
    """
    md5 = hashlib.md5()
    file_path = sub_string
    if not os.path.exists(file_path):
        file_path = os.path.join(os.environ['CAFE_DATA_DIR_PATH'], file_path)
    if not os.path.exists(file_path):
        file_path = file_path.replace(' ', '_')
    assert (os.path.exists(file_path)), "File %s doesn't exist" % file_path
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def read_local_file(filename):
    """
        This will read a file in the same directory as the calling function
    :param filename: str of the basename of the file
    :return: str of the content of the file
    """
    frm = inspect.currentframe().f_back
    if frm.f_code.co_name == 'run_code':
        frm = frm.f_back
    path = os.path.split(frm.f_code.co_filename)[0]
    return read_file(os.path.join(path, filename))


def relative_path(*args):
    """
        This will return the file relative to this python script
    :param args: str of the relative path
    :return: str of the full path
    """
    frm = inspect.currentframe().f_back
    if frm.f_code.co_name == 'run_code':
        frm = frm.f_back
    path = os.path.split(frm.f_code.co_filename)[0]
    return os.path.abspath(os.path.join(path, *args))


def mdate(filename):
    """
    :param filname: str of the file
    :return: float of the modified date of the file
    """
    return os.stat(filename).st_mtime


def read_file(full_path):
    assert os.path.exists(full_path), "File '%s' doesn't exist" % full_path

    ret = open(full_path, 'r').read()
    if full_path.endswith('.json'):
        try:
            json.loads(ret)
        except Exception as e:
            raise Exception("%s is not valid JSON" % full_path)
    return ret


def copy_file(source_file, destination_file, soft_link=False):
    """
    :param source_file: str of the full path to the source file
    :param destination_file: str of the full path to the destination file
    :param soft_link: bool if True will soft link if possible
    :return: None
    """
    if not os.path.exists(source_file):
        raise IOError("No such file: %s" % source_file)
    mkdir_for_file(destination_file)
    if os.path.exists(destination_file):
        os.remove(destination_file)

    if os.name == 'posix' and soft_link:
        try:
            os.symlink(source_file, destination_file)
        except:
            shutil.copy(source_file, destination_file)
    else:
        try:
            shutil.copy(source_file, destination_file)
        except Exception as e:
            raise


def read_folder(folder, ext='*', uppercase=False, replace_dot='.', parent=''):
    """
        This will read all of the files in the folder with the extention equal
        to ext
    :param folder: str of the folder name
    :param ext: str of the extention
    :param uppercase: bool if True will uppercase all the file names
    :param replace_dot: str will replace "." in the filename
    :param parent: str of the parent folder
    :return: dict of basename with the value of the text in the file
    """
    ret = {}
    if os.path.exists(folder):
        for file in os.listdir(folder):
            if os.path.isdir(os.path.join(folder, file)):
                child = read_folder(os.path.join(folder, file),
                                    ext, uppercase, replace_dot,
                                    parent=parent + file + '/')
                ret.update(child)
            else:
                if ext == '*' or file.endswith(ext):
                    key = file.replace('.', replace_dot)
                    key = uppercase and key.upper() or key
                    ret[parent + key] = read_file(os.path.join(folder, file))
    return ret


class print_file():
    def write(self, text):
        print(text)
    def flush(self):
        pass


def smoke_test():
    mkdir('%s/file_smoke_test/test1' % TRASH_PATH)
    assert os.path.exists('%s/file_smoke_test/test1' % TRASH_PATH)
    os.rmdir('%s/file_smoke_test/test1' % TRASH_PATH)
    os.rmdir('%s/file_smoke_test' % TRASH_PATH)


if __name__ == '__main__':
    smoke_test()
