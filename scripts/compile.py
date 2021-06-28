
import os
import sys
import json


class CConfig:
    def __init__(self, dic_json, prog):
        self.dic_json = dic_json
        self.prog     = prog
        self.dir_src  = dic_json[0][prog][0] # mkdir/cp
        self.mk_ways  = dic_json[0][prog][1] # cmake/conf/make
        self.ad_flag  = dic_json[0][prog][2] # CFLAGS/CXXFLAGS
        self.tf_path  = dic_json[1]["tofuzz_path"][0]
        self.download_path = dic_json[1]["download_path"][0]
        self.PUT_path = dic_json[1]["PUT_path"][0]


def set_env(cconfig):
    '''
    step 1: set enviroment
    '''
    if(cconfig.t == "bb" or cconfig.t == "func" or cconfig.t == "loop"):
        os.environ["CC"]  = "%s/%s_metric/afl-clang-fast" % (cconfig.tf_path, cconfig.t)
        os.environ["CXX"] = "%s/%s_metric/afl-clang-fast++" % (cconfig.tf_path, cconfig.t)
        os.environ["CFLAGS"]  = cconfig.ad_flag
        os.environ["CXXFLAGS"]  = cconfig.ad_flag
        os.environ["LDFLAGS"]  = cconfig.ad_flag
    else:
        print("Unknown type")
        exit(-1)

def create_build_folder(cconfig):
    '''
    step 2: make target folder
    '''
    if(cconfig.dir_src == "mkdir"):
        # mkdir
        try:
            os.mkdir("./build_%s" % (cconfig.t))
        except:
            pass
    elif(cconfig.dir_src == "cp"):
        # copy
        os.system("cp -r %s build_%s" % (cconfig.download_path + prog, cconfig.t))
    else:
        print("Unknown cmd")
        exit()

def compile(cconfig):
    '''
    step 3: compiling
    '''
    basedir = os.path.abspath(os.path.dirname(__file__))
    install_path = "%s/bin_%s" % (basedir.rstrip("/build_%s" % cconfig.t), cconfig.t)
    if(cconfig.mk_ways == "cmake"):
        # cmake
        cmd0 = "cmake %s/ -DCMAKE_INSTALL_PREFIX=%s" % (cconfig.download_path + prog, install_path)
        os.system(cmd0)
        os.system("make")
        os.system("make install")
    elif(cconfig.mk_ways == "conf"):
        # configure
        if(cconfig.dir_src == "cp"):
            cmd0 = "./configure --prefix=%s" % (install_path)
        else:
            cmd0 = "%s/configure --prefix=%s" % (cconfig.download_path + prog, install_path)

        os.system(cmd0)
        os.system("make")
        os.system("make install")
    elif(cconfig.mk_ways == "make"):
        # directly make
        cmd1 = "make"
        print(cmd1)
        os.system(cmd1)
        os.makedirs("../bin_%s/bin" % (cconfig.t))
        os.system("cp gif2tga ../bin_%s/bin" % (cconfig.t))
    else:
        print("Unknown compiling method")
        exit()

def compile_main(dic_json, prog, t):
    cconfig = CConfig(dic_json, prog, t)
    if not os.path.exists(cconfig.download_path + prog) :
        print("%s not downloaded." % prog)
        return 
    if not os.path.exists(cconfig.PUT_path) :
        os.makedirs(cconfig.PUT_path)
    os.chdir(cconfig.PUT_path)
    if not os.path.exists(prog) :
        os.makedirs(prog)    
    os.chdir(prog)
    set_env(cconfig)
    create_build_folder(cconfig)
    os.chdir("build_%s" % (t))
    compile(cconfig)
    os.chdir(cconfig.tf_path)

if(__name__ == "__main__"):
    # compile.py X.json program 
    f = open(sys.argv[1], "r")
    prog = sys.argv[2]
    
    dic_json = json.loads(f.read())

    for t in type_list:
        compile_main(dic_json, prog)