#!/bin/python3

"""
Arithmetic:
   <result> = add <ty> <op1>, <op2>
   <result> = mul <ty> <op1>, <op2>
   <result> = sdiv <ty> <op1>, <op2>
   <result> = sub <ty> <op1>, <op2>

Boolean:
   <result> = and <ty> <op1>, <op2>
   <result> = or <ty> <op1>, <op2>
   <result> = xor <ty> <op1>, <op2>

Comparison and Branching:
   <result> = icmp <cond> <ty> <op1>, <op2> ; <cond> ie.  eq
   br i1 <cond>, label <ifTrue>, label <ifFalse>
   br label <dest>

Load and Stores:
   <result> = load <ty>* <pointer>
   store <ty> <value>, <ty>* <pointer>
   <result> getelementptr <ty>* <ptrval>, i1 0, i32 <index>

Invocation:
   <result> = call <ty> <fnptrval>(<function args>)
   ret void
   ret <ty> <value>

Allocation:
   <result> = alloca <ty>

Misc:
   <result> = bitcast <ty> <value> to <ty2>     ;cast type
   <result> = trunc <ty> <value> to <ty2>       ;truncate to ty2
   <result> = zext <ty> <value> to <ty2>        ;zero extend to ty2
   <result> = phi <ty> [<value 0>, <label 0>] [<value 1> <label 1>] ...

<ty>
   iN - integer with N bits
   void
   null - null pointer constant, must be of 'pointer type'
   boolean - 'true' and 'false' are constants of type 'i1'
   imm - integers can be used as constants / immediate values

<cond>
   eq - equal
   ne - not equal
   ugt - unsigned greater than
   uge - unsigned greater than or equal
   ult - unsigned less than
   ult - unsigned less than or equal
   sgt - signed greater than
   sge - signed greater than or equal
   slt - signed less than
   sle - signed less than or equal

<result>
   register to store returned result

<op>
   imm - #
   register - %<regName>
   *void
   *null

"""
#global register counter
regLabel = 0

def transArith():
   return ""
def transBool():
   return ""
def transCmp():
   return ""
def transBr():
   return ""
def transLoad():
   return ""
def transStore():
   return ""
def transInvoc():
   return ""
def transAlloc():
   return ""
def transMisc():
   return ""


def lookUpInstType(instr):
   #if arithmetic:
   #elif boolean:
   #elif comparison and branching
   #elif load and stores
   #elif invocation
   #elif allocation
   #elif misc
   return None


def translateInstr():
   #instrType = lookupInstrType(instr)

   #if instrType == "arithmetic":
   #elif instrType == "boolean":
   #elif instrType == "comparison":
   #elif instrType == "branching":
   #elif instrType == "load":
   #elif instrType == "store":
   #elif instrType == "invocation":
   #elif instrType == "allocation":
   #elif instrType == "misc":
   #else:
      #ERROR instrType doesn't exist
   return None

def translateInstrs(cfg):
   global regLabel
   instrs = []
   instrs.append(f"L{cfg.entry.label}:")
   
   for param in cfg.params:
      instrs.append(f"%_P_{param['id']} = alloca {lookupLlvmType(param['type']}")
   for param in cfg.params:
      llvmType = lookupLlvmType(param['type'])
      paramId = param['id']
      instrs.append(f"store {llvmType} %{paramId}, {llvmType}* %_P_{paramId}")

   #TODO finish translating rest of the blocks instructions and each successor block 

   return instrs

"""
programCfg
   types
   decls
   funcCfgs
      [cfg ...]
"""

def lookupLlvmType(llvmType):
   if llvmType == "int":
      return "i32"
   elif llvmType == "bool":
      return "i32"
   elif llvmType == "void":
      return "void"
   else:
      return "i32"

def lookupParamTypes(params):
   paramTable = {}
   
   for param in params:
      paramTable.add(param['id'], lookupLlvmType(param['type']))
   """
   paramStrs = []

   for param in params:
      paramStrs.append(f"{param['type']} %{param['id']}")

   formattedParamStr = ""
   for paramStr in paramStrs:
      formattedParamStr += paramStr + ","
   #remove trailing comma
   return formattedParamStr[:len(formattedParamStr) - 1]
   """

def translateProg(progCfg):
   #print(progCfg.funcCfgs)
   progFuncs = {}
   
   for cfg in progCfgs.funcCfgs:
      progFuncs.add(cfg.funcName, funcLlvm(cfg))

   return progFuncs

class funcLlvm:
   def __init__(self, cfg):
      #self.header = f"define {lookupLlvmType(retType)} @{funcId}({lookupParamTypes(params)})"
      self.funcId = cfg.funcName
      self.retType = lookupLlvmType(cfg.returnType)
      self.params = lookupParamTypes(cfg.params)
      #self.openBlock = "{"
      self.instrs = translateInstrs(cfg)
      #self.closeBlock = "}"
   """
   def __str__(self):
      print(self.header)
      print(self.openBlock)
      for instr in self.instrs:
         print(instr)
      print(self.closeBlock)
   """

