/*
  Copyright 2015 Google LLC All rights reserved.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at:

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

/*
   american fuzzy lop - LLVM-mode instrumentation pass
   ---------------------------------------------------

   Written by Laszlo Szekeres <lszekeres@google.com> and
              Michal Zalewski <lcamtuf@google.com>

   LLVM integration design comes from Laszlo Szekeres. C bits copied-and-pasted
   from afl-as.c are Michal's fault.

   This library is plugged into LLVM when invoking clang through afl-clang-fast.
   It tells the compiler to add code roughly equivalent to the bits discussed
   in ../afl-as.h.
*/

/*
   VmaxFuzz - LLVM-mode instrumentation pass, based on AFL
   ---------------------------------------------------

   Written by Cai Chunfang <caichunfang18@mails.ucas.ac.cn> 
  
   Seed Selection For Variables Indicating The Scale Of Memory Operation

*/

#define AFL_LLVM_PASS

#include "../config.h"
#include "../debug.h"

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include "llvm/ADT/Statistic.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/IR/Module.h"
#include "llvm/Support/Debug.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace {

  class AFLCoverage : public ModulePass {

    public:

      static char ID;
      AFLCoverage() : ModulePass(ID) { }

      bool runOnModule(Module &M) override;

      //VmaxFuzz
      bool doInitialization(Module &M) override;      

  };

}

char AFLCoverage::ID = 0;

//vmaxfuzz
struct Option{
  char arg_type; // 1 = integer, 2 = pointer,...
  char argn; // which arg is to be instrumented
  struct Option *next;
  Option(): arg_type(0), argn(0), next(nullptr){}
};

std::map<std::string, Option* > syscall_map;

bool AFLCoverage::doInitialization(Module &M){
  std::ifstream insyscall('r', "syscall.txt");
  if(insyscall.is_open()){
    std::string s;
    while(insyscall >> s){
      int tag_in, argn_in;
      std::cin >> tag_in >> argn_in;
      if(tag_in && argn_in){
        Option* op_in = new Option();
        op_in->arg_type = tag_in;
        op_in->argn = argn_in;
        syscall_map[s] = op_in;
      }
      else{
        syscall_map[s] = nullptr;
      }
    }
    OKF("map size: %d", syscall_map.size());
  }
	else{
    OKF("file syscalls.txt not open.");
  }
	return false;
}
// end vmaxfuzz

bool AFLCoverage::runOnModule(Module &M) {

  LLVMContext &C = M.getContext();

  IntegerType *Int8Ty  = IntegerType::getInt8Ty(C);
  IntegerType *Int32Ty = IntegerType::getInt32Ty(C);

  /* Show a banner */

  char be_quiet = 0;

  if (isatty(2) && !getenv("AFL_QUIET")) {

    SAYF(cCYA "afl-llvm-pass " cBRI VERSION cRST " by <chunfang>\n");

  } else be_quiet = 1;

  /* Decide instrumentation ratio */

  char* inst_ratio_str = getenv("AFL_INST_RATIO");
  unsigned int inst_ratio = 100;

  if (inst_ratio_str) {

    if (sscanf(inst_ratio_str, "%u", &inst_ratio) != 1 || !inst_ratio ||
        inst_ratio > 100)
      FATAL("Bad value of AFL_INST_RATIO (must be between 1 and 100)");

  }

  //vmaxfuzz
  IRBuilder<> builder(C); 
  // Function state_inst_string()
  std::vector<Type*> argTypesInstString;
  argTypesMalloc.push_back(builder.getInt32Ty());
  argTypesMalloc.push_back(builder.getInt8PtrTy());
  ArrayRef<Type*> argTypesRefInstString(argTypesInstInt);
  llvm::FunctionType *funcInstStringType = FunctionType::get(builder.getVoidTy(),argTypesInstString,false);
  llvm::Function *funcInstString = Function::Create(funcInstMaxString, llvm::Function::ExternalLinkage, "state_inst_string", &M);

  // Function state_inst_int()
  std::vector<Type*> argTypesInstInt;
  argTypesMalloc.push_back(builder.getInt32Ty());
  argTypesMalloc.push_back(builder.getInt64Ty());
  ArrayRef<Type*> argTypesRefInstInt(argTypesInstInt);
  llvm::FunctionType *funcInstIntType = FunctionType::get(builder.getVoidTy(),argTypesInstInt,false);
  llvm::Function *funcInstInt = Function::Create(funcInstMaxType, llvm::Function::ExternalLinkage, "state_inst_int", &M);

  GlobalVariable *AFLVmaxPtr =
      new GlobalVariable(M, PointerType::get(Int64Ty, 0), false,
                         GlobalValue::ExternalLinkage, 0, "__vmax_ptr");

  //end vmaxfuzz

  /* Get globals for the SHM region and the previous location. Note that
     __afl_prev_loc is thread-local. */

  GlobalVariable *AFLMapPtr =
      new GlobalVariable(M, PointerType::get(Int8Ty, 0), false,
                         GlobalValue::ExternalLinkage, 0, "__afl_area_ptr");

  GlobalVariable *AFLPrevLoc = new GlobalVariable(
      M, Int32Ty, false, GlobalValue::ExternalLinkage, 0, "__afl_prev_loc",
      0, GlobalVariable::GeneralDynamicTLSModel, 0, false);

  /* Instrument all the things! */

  int inst_blocks = 0;

  for (auto &F : M)
    for (auto &BB : F) {

      BasicBlock::iterator IP = BB.getFirstInsertionPt();
      IRBuilder<> IRB(&(*IP));

      if (AFL_R(100) >= inst_ratio) continue;


      //vmaxfuzz

      int syscall_num = 0;

      for (auto Inst = BB.begin(); Inst != BB.end(); Inst++) {

        IRBuilder<> VmaxFuzzBuilder(&(*Inst)); 

        Instruction &inst = *Inst;

        if (inst->isVectorOp()){

          int opCode = inst->getOpcode();

          if(opCode == Instruction::Extractelement || Instruction::Insertelement){

            VectorOperator *bo = cast<VectorOperator>(inst);
            Value* tmpValue = bo->getOperand(2); 

            unsigned int instAddr = hash_inst(__FILE__, __LINE__);

            SmallVector<Value *, 2> functionArg;

            functionArg.push_back(instAddr);

            functionArg.push_back(tmpValue);

            VmaxFuzzBuilder.CreateCall(funcInstInt, functionArg);      

        }

        else if(CallInst* call_inst = dyn_cast<CallInst>(&inst)) {

          Function* fn = call_inst->getCalledFunction();

          if(fn == NULL){

            Value *v = call_inst->getCalledValue();
            fn = dyn_cast<Function>(v->stripPointerCasts());

            if(fn == NULL)
              continue;

          }

          std::string fn_name = fn->getName();

          if(fn_name.compare(0, 5, "llvm.") == 0)
            continue;
          
          std::map<string, Option*>::iterator map_iter = syscall_map.find(fn_name);

          if(map_iter != syscall_map.end()){

            syscall_num++;
            // outs() <<"syscall on line " << __LINE__ << fn_name << "\n";
            // outs() <<"syscall on line " << Inst.getDebugLoc().getLine() << fn_name << "\n";

            if(map_iter->second){
              if(inst->getNumOperands() >= map_iter->second->argn){

                unsigned int instAddr = hash_inst(__FILE__, __LINE__) + map_iter->second->argn;

                Value* tmpValue = inst->getOperand(map_iter->second->argn - 1);

                SmallVector<Value *, 2> functionArg;

                functionArg.push_back(instAddr);

                functionArg.push_back(tmpValue);

                switch(map_iter->second->tag){
                  case 1:{ 
                    VmaxFuzzBuilder.CreateCall(funcInstInt, functionArg);
                    break;
                  }
                  case 2:{
                    VmaxFuzzBuilder.CreateCall(funcInstString, functionArg);
                    break;
                  }
                  default: break;
                }                
              }
            }

          }
        }
      }

      //end vmaxfuzz

      /* Make up cur_loc */

      unsigned int cur_loc = AFL_R(MAP_SIZE);

      ConstantInt *CurLoc = ConstantInt::get(Int32Ty, cur_loc);

      /* Load prev_loc */

      LoadInst *PrevLoc = IRB.CreateLoad(AFLPrevLoc);
      PrevLoc->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
      Value *PrevLocCasted = IRB.CreateZExt(PrevLoc, IRB.getInt32Ty());

      /* Load SHM pointer */

      LoadInst *MapPtr = IRB.CreateLoad(AFLMapPtr);
      MapPtr->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
      Value *MapPtrIdx =
          IRB.CreateGEP(MapPtr, IRB.CreateXor(PrevLocCasted, CurLoc));

      /* Update bitmap */

      LoadInst *Counter = IRB.CreateLoad(MapPtrIdx);
      Counter->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
      Value *Incr = IRB.CreateAdd(Counter, ConstantInt::get(Int8Ty, 1));
      IRB.CreateStore(Incr, MapPtrIdx)
          ->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

      /* Set prev_loc to cur_loc >> 1 */

      StoreInst *Store =
          IRB.CreateStore(ConstantInt::get(Int32Ty, cur_loc >> 1), AFLPrevLoc);
      Store->setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

      inst_blocks++;

    }

  /* Say something nice. */

  if (!be_quiet) {

    if (!inst_blocks) WARNF("No instrumentation targets found.");
    else OKF("Instrumented %u locations (%s mode, ratio %u%%).",
             inst_blocks, getenv("AFL_HARDEN") ? "hardened" :
             ((getenv("AFL_USE_ASAN") || getenv("AFL_USE_MSAN")) ?
              "ASAN/MSAN" : "non-hardened"), inst_ratio);

  }

  return true;

}


static void registerAFLPass(const PassManagerBuilder &,
                            legacy::PassManagerBase &PM) {

  PM.add(new AFLCoverage());

}


static RegisterStandardPasses RegisterAFLPass(
    PassManagerBuilder::EP_ModuleOptimizerEarly, registerAFLPass);

static RegisterStandardPasses RegisterAFLPass0(
    PassManagerBuilder::EP_EnabledOnOptLevel0, registerAFLPass);
