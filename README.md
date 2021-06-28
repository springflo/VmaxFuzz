# VmaxFuzz: Seed Selection For Variables Indicating The Scale Of Memory Operation

github:

Developed by Cai Chunfang .

## 1) Project 

Out-of-Bound is a kind of dangerous and common vulnerability in programs. The software does not restrict or incorrectly restricts operations within the boundaries of memory that is accessed using an index or pointer. In some complex cases, to trigger the out of bounds errors not only needs to satisfy control flow conditions, but also data conditions. In these cases, the scale of memory operation should exceed the memory boundary or specific range. However, detecting such vulnerability is challenging, as the state-of-the-art fuzzing techniques focus on code coverage but not memory operation and scale, failing to give additional energy to test cases which changed the memory scale. To achieve higher efficiency on detecting this kind of out-of-bound errors with grey-box fuzzing, we introduced memory scale indicating variable, shortly MemsVar, which is the variable that indicates the index, pointer or size of a memory operation in a program. The MemsVar were instrumented to monitor the change of memory operation scale. We then proposed a seed metric for MemsVar. With this metric, test cases which updated the actual range of MemsVar were kept as effective seeds, thus guiding the scale of memory operation to exceed the memory boundary or specific range and triggering memory out-of-bound errors quickly. Finally, based on the proposed seed metric, we designed a gray box fuzzer named Vmaxfuzz, implemented on the basis of AFL.

## Uage

### 1) Environment and Main Code 

    System：ubuntu 16.04
    tools：llvm clang valgrind etc.
    
    ./afl-fuzz.c    fuzzing Loop
    ./llvm_mode/afl-llvm-pass.so.cc Static analyze and Instrumentation
    ./llvm_mode/afl-llvm-rt.o.c      Instrumentation
    ./scripts/      compile,analyze,run scripts

### 2) Compile vmaxfuzz 

    ./
    $make
    $cd llvm_mode/
    $make

    Get executable files: afl-clang-fast,afl-clang-fast++,afl-fuzz, and some run-time files.
        afl-clang-fast  afl-clang-fast++    VmaxFuzz compiler
        afl-fuzz                            fuzzer

### 3) Compile programs

    -get programs
    $./scripts/get_program.py program_src.json exiv2

    -Comple programs with afl-clang-fast  afl-clang-fast++, with python
    $./scripts/compile.py ./scripts/compile_arg.json exiv2
    Or shell scripts
    ./scripts/run_fuzzer.sh exiv2

### 4) Start Fuzzing

    $./scripts/run_fuzzer.py ./scripts/fuzz_arg.json exiv2
    
### 5) Analyze Results

    out/crash_file
    Use valgrind,AS to reproduce the call stack，compare with CVE
    $./scripts/get_cves.py exiv2    crawl CVE informations

## 联系信息

蔡春芳
中国科学院软件研究所基础软件中心




