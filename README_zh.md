# VmaxFuzz: 针对内存规模表征变量的种子度量方法

github:


## 1) 项目简介

内存越界缺陷是程序中危害性巨大的常见缺陷，是由软件没有限制或错误地限制资源的边界，使内存操作的索引或规模超过界限而导致的程序错误．大多数内存越界缺陷的触发不仅要求满足一定的控制流条件，还需要内存操作的操作规模超过内存边界或特定范围．而现有的灰盒模糊测试方法往往仅关注程序的控制流状态，监控指令是否执行或指令执行顺序，不能有效发现这类规模敏感型内存越界漏洞，因此对这类缺陷的检测仍然存在很大的挑战．为了提升灰盒模糊测试对这类缺陷的发现效率，我们引入了内存规模表征变量的概念，即程序中表征内存操作索引、指针或规模的变量，对程序中的内存规模表征变量进行逐个插桩，从而监控内存规模表征变量的取值变化；提出了一种针对内存规模表征变量的种子度量方法，将更新了内存规模表征变量实际取值范围的测试用例保留为种子，从而引导程序内存操作规模超过内存边界或特定范围，更快地触发该类内存越界缺陷；基于上述种子度量方法，在AFL的基础上，实现了灰盒模糊测试器VmaxFuzz．

## 使用说明


### 1) 环境和关键代码

    系统：ubuntu 16.04
    工具：llvm clang valgrind 等

    ./afl-fuzz.c    fuzzing循环逻辑
    ./llvm_mode/afl-llvm-pass.so.cc 插桩和静态分析代码
    ./llvm_mode/afl-llvm-rt.o.c     插桩代码
    ./scripts/      编译、分析、运行的脚本以及代码

### 2) 编译 vmaxfuzz 

    项目路径下
    ./
    $make
    $cd llvm_mode/
    $make

    编译成功获得afl-clang-fast  afl-clang-fast++  afl-fuzz可执行文件，以及一些llvm的运行时文件。
        afl-clang-fast  afl-clang-fast++    VmaxFuzz的编译程序，用它们来编译C/C++程序
        afl-fuzz                            模糊测试程序，运行它来进行模糊测试

### 3) 编译被测程序

    ./scripts/  下含有一些编译、分析、运行的脚本以及代码

    -获取被测程序
    $./scripts/get_program.py program_src.json exiv2

    -使用afl-clang-fast  afl-clang-fast++编译被测程序，可以使用python脚本
    $./scripts/compile.py ./scripts/compile_arg.json exiv2
    或运行一次性编译测试测试shell
    ./scripts/run_fuzzer.sh exiv2

### 4) 开始模糊测试

    $./scripts/run_fuzzer.py ./scripts/fuzz_arg.json exiv2
    

### 5) 分析测试结果

    输出crash_file
    使用valgrind和AS工具分析调用栈，与CVE信息比较
    $./scripts/get_cves.py exiv2    抓取exiv2 CVE的相关信息 

## 联系信息
蔡春芳
中国科学院软件研究所基础软件中心




