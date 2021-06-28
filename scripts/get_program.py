
import os
import sys
import json
from urllib.request import urlretrieve


class CConfig:
    def __init__(self, dic_json, prog):
        self.dic_json = dic_json
        self.prog     = prog
        # self.t        = t
        self.prog_url  = dic_json[0][prog][0] 
        self.prog_version = dic_json[0][prog][1]
        self.prog_new_version = dic_json[0][prog][2]
        self.download_path  = dic_json[1]["download_path"][0]


def reporthook(a, b, c):
    """
    显示下载进度
    :param a: 已经下载的数据块
    :param b: 数据块的大小
    :param c: 远程文件大小
    :return: None
    """
    print("\rdownloading: %5.1f%%" % (a * b * 100.0 / c), end="")


def get_program(dic_json, prog):
    pconfig = CConfig(dic_json, prog)
    if not os.path.exists(pconfig.download_path):
        os.makedirs(pconfig.download_path)
    os.chdir(pconfig.download_path)
    save_path = os.path.join(pconfig.download_path, pconfig.prog)
    if not os.path.isfile(save_path):
        print('Downloading data from %s' % (pconfig.prog_url + pconfig.prog_version))
        urlretrieve(pconfig.prog_url + pconfig.prog_version, save_path, reporthook=reporthook)
        print('\nDownload finished!')
    else:
        print('File already exsits!')
    filesize = os.path.getsize(save_path)
    print('File size = %.2f Mb' % (filesize/1024/1024))



if(__name__ == "__main__"):

    # get program /XX.json prog
    f = open(sys.argv[1], "r")
    prog = sys.argv[2]
    
    dic_json = json.loads(f.read())
    # type_list = ["bb", "func", "loop"]

    get_program(dic_json, prog)