#!/bin/python3
import queue
import translateInstrConnor
import re

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
##############GLOBALS#########
#global register counter
regLabel = 0
labelDecls = {}
##############################


def transArith(instr, block, llvmInstrs):
   #instrs = []
   op = instr['operator']
   #resultReg = getNextRegLabel()

   lhsType = instr['lft']['exp']
   lrhsType = instr['rht']['exp']
   
   if lhsType == "num":
      lhs = instr['lft']['value']
   elif lhsType == "id":
      lhs = lookupLabelDecl(block, instr['lft']['id'])


   if rhsType == "num":
      rhs = instr['rht']['value']
   elif rhsType == "id":
      rhs = lookupLabelDecl(block, instr['rht']['id'])


   #lookupLabelDecl(label, leftOp)
   target = getNextRegLabel()
   if op == "+":
      llvmInstrs.append(f"%u{target} = add i32 {lhs}, {rhs}")

   elif op == "-":
      llvmInstrs.append(f"%u{target} = sub i32 {lhs}, {rhs}")

   elif op == "/":
      llvmInstrs.append(f"%u{target} = sdiv i32 {lhs}, {rhs}")

   elif op == "*":
      llvmInstrs.append(f"%u{target} = mul i32 {lhs}, {rhs}")

   return f"%u{target}" 

def transBool():
   return ""

def transCmp(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg):
   #instrs = []
   op = instr["operator"]
   
   if op == "==":
      cond = "eq"

   elif op == "!=":
      cond = "ne"

   elif op == "<":
      cond = "slt"

   elif op == "<=":
      cond = "sle"

   elif op == ">":
      cond = "sgt"

   elif op == ">=":
      cond = "sge"

#TODO Fix all lookupLabelDecls throughout program and update
#method calls to include current block for lookups

   lhsType = instr['lft']['exp']
   rhsType = instr['rht']['exp']
   
   if lhsType == "num":
      lhs = instr['lft']['value']
   elif lhsType == "id":
      #lhs = f"%u{lookupLabelDecl(block, instr['lft']['id'])}"
      lhs = lookupLabelDecl(block, instr['lft']['id'])
   else:
      #lhs = "###"
      #print(f"lhs of line: {instr['line']} not num or id. -> {instr}")
      lhs = translateInstr(instr['lft'], block, llvmInstrs, globals_and_locals, structTypes, cfg)


   if rhsType == "num":
      rhs = instr['rht']['value']
   elif rhsType == "id":
      #rhs = f"%u{lookupLabelDecl(block, instr['rht']['id'])}"
      rhs = lookupLabelDecl(block, instr['rht']['id'])
   else:
      #rhs = "###"
      #print(f"rhs of line: {instr['line']} not num or id. -> {instr}")
      rhs = translateInstr(instr['rht'], block, llvmInstrs, globals_and_locals, structTypes, cfg)

   target = getNextRegLabel()
   if type(lhs) == int and lhsType != "num":
      lhs = f"%u{lhs}"
   if type(rhs) == int and rhsType != "num":
      rhs = f"%u{rhs}"
   llvmInstrs.append(f"%u{target} = icmp {cond} i32 {lhs}, {rhs}")

   return f"%u{target}"

def transBr():
   return ""

def transLoad():
   return ""

def transStore():
   return ""

#recursive version with more abstraction
#if in paramRegs/imm is a string then its a register of it is an int then it is an imm
#params can only be arithmetic, nums, bools, invocations
def transInvoc(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg):
   paramRegs = [None] * len(instr['args'])

   for i in range(len(instr["args"])):
      if instr["args"][i] == "invocation":
         paramRegs[i] = transInvoc(instr["args"][i], block, llvmInstrs, globals_and_locals, structTypes, cfg)

      else:
         #paramRegs[i] = getNextRegLabel()
         paramRegs[i] = translateInstr(instr['args'][i], block, llvmInstrs, globals_and_locals, structTypes, cfg)

   paramStr = """"""
   for i in range(len(paramRegs)):
      if i != 0 and i != len(paramRegs):
         paramStr += ", "
      paramStr += f"i32 {paramRegs[i]}"
   resultReg = getNextRegLabel()
   llvmInstrs.append(f"%u{resultReg} = call @{instr['id']}({paramStr})")
   #TODO this might need to only return the register number so that formating 
   #stays consistent to other returns
   #return f"%u{resultReg}"
   return f"%u{resultReg}"

def transAlloc():
   return ""

def transMisc():
   return ""

#TODO instruction may be dict({guard: instr})
def lookupInstrType(instr):

   if "guard" in instr:
      return "guard"

   instrType = instr.get('exp')
   """
   if instrType == None:
      instrType = instr.get('stmt')
   """
   if instr.get("stmt") == "return":
      return "return"


   if   instrType == "binary":
      if instr['operator'] in ["+","-","/","*"]:
         return "arithmetic"
      else:
         # > < >= <= != == 
         return "comparison"

   elif instrType == "boolean":
      return "boolean"

   elif instrType == "comparison" and "branching":
      return "comparison"

   elif instrType == "assign":
      return "store"
      #return "load"

   elif instrType == "invocation":
      return "invocation"

   elif instrType == "allocation":
      return "allocation"

   elif instrType == "num":
      return "num"

   elif instrType == "null":
      return "null"

   elif instrType == "misc":
      return None

"""
   connor
   -load
   -store
   -branching

   donnie
   -invocation
   -boolean
   -arithmetic
"""
#return list of instruction strings
#TODO change to take instr, cfg (blockNode), and a list of the current
#llvmInstrs to be filled from within the translation methods
def translateInstr(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg):
   instrType = lookupInstrType(instr)
   #instrType = instr.get('exp')

   if instrType == "arithmetic":
         return transArith(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg)

   elif instrType == "comparison":
      return transCmp(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg)

   elif instrType == "invocation":
      return transInvoc(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg)

   elif instrType == "num":
      return instr['value']

   elif instrType == "null":
      return "null"

   #elif instrType == "return":


   else:
      #pass the instruction to connors translation
      if  getLabelDeclTable(block.label) == None:
         print(f"ERROR: empty mapping:\n\tblock: {block.label}\ninstr:{instr}")
         print(f"block 0 decls : {getLabelDeclTable(0)}")
      translateInstrConnor.transInstr(
            instr, 
            llvmInstrs, 
            block,
            getLabelDeclTable(block.label),
            structTypes,
            globals_and_locals,
            cfg) #curBlock, #mapping, #types, #decls
   """
   elif instrType == "boolean":
      pass

   elif instrType == "branching":
      pass

   elif instrType == "load":
      pass

   elif instrType == "store":
      pass

   elif instrType == "allocation":
      pass


   elif instrType == "misc":
      pass
   
   else:
      print(f"ERROR instrType {instrType} doesn't exist: instr: {instr}")
   
   """

   return None

def getNextRegLabel():
   global regLabel
   retReg = regLabel
   regLabel += 1
   return retReg

#add decl to a given labels/blocks regTable
# label -> <id><reg>
def addLabelDecl(label, var, regName):
   global labelDecls
   if not labelDecls.get(label):
      labelDecls[label] = dict()
   if type(regName) == int:
      labelDecls[label][var] = f"%u{regName}"
   else:
      labelDecls[label][var] = "%" + regName 

def initVar(label, var):
   global labelDecls
   if not labelDecls.get(label):
      labelDecls[label] = dict()

   labelDecls[label][var] = None
   print(f"Added {var} to decls")


def getLabelDeclTable(label):
   global labelDecls

   return labelDecls.get(label)

#TODO
def handlePhi(label):
   global labelDecls
   for key in labelDecls[label]["incPhis"]:
      return None

#lookup registers from a given label/block
#TODO if the there are multiple predecessors phi 
#instr will need to be made and maintained in the decl dict
#both complete and incomplete phis will be there
#IDEA: keep incomplete and complete phis in the dict only.
#  in the llvmInstrs list insert a special tag at the top of each
#  blockLabel. When printing out the instrs when we see that tag
#  replace the tag with the completed phi instructions.

#TODO
#replace label with block in order to get predecessors etc.
"""
def lookupLabelDecl(label, varName): 
   global labelDecls
   if not labelDecls.get(label):
      return None
   return labelDecls[label].get(varName)
"""

#""" #replacement lookup
def lookupLabelDecl(block, varName, phiLabelLoc = None):
   global labelDecls
   if not labelDecls.get(block.label):
      return None
   reg = labelDecls[block.label].get(varName)

   if reg:
      if phiLabelLoc:
         phiLabelLoc[0] = block.label
      return reg

   elif len(block.preds) == 0:
      if phiLabelLoc:
         phiLabelLoc[0] = None
      return None

   elif len(block.preds) == 1:
      if phiLabelLoc:
         lookupLabelDecl(block.preds[0], varName, phiLabelLoc)
      else:
         lookupLabelDecl(block.preds[0], varName)

   else:
      phiReg = getNextRegLabel()
      labelDecls[block.label][varName] = phiReg 
      preds = block.preds
      if labelDecls.get('incPhis') == None:
         labelDecls['incPhis'] = dict()

      labelDecls['incPhis'][phiReg] = list()
      for pred in preds:
         if pred.visited:
            phiLabel = [None]
            lookupReg = lookupLabelDecl(pred, varName, phiLabel)
            labelDecls['incPhis'][phiReg].append({"reg": lookupReg, "label":phiLabel[0]})

         else:
            labelDecls['incPhis'][phiReg].append({"reg":None, "label": None})

      return phiReg
         
#"""

"""
def phiLookup():
"""


"""
def completePhis():
   global labelDecls

   for key in labelDecls.keys()
      incPhis = labelDecls[key].get('incPhis')
      if incPhis:
         
"""


def translateInstrs(cfg, globals_and_locals, structTypes):
   llvmInstrs = []
   llvmInstrs.append(f"L{cfg.entry.label}:")
   
   #inital allocations for function
   if cfg.returnType != "void":
      llvmInstrs.append(f"%_retval_ = alloca {lookupLlvmType(cfg.returnType)}")
      
   #allocates room on the stack for params
   for param in cfg.params:
      llvmInstrs.append(f"%_P_{param['id']} = alloca {lookupLlvmType(param['type'])}")
      addLabelDecl(cfg.entry.label, param['id'], param['id'])

   #Stores params in newly allocated memory
   for param in cfg.params:
      llvmType = lookupLlvmType(param['type'])
      paramId = param['id']
      llvmInstrs.append(f"store {llvmType} %{paramId}, {llvmType}* %_P_{paramId}")

   #TODO finish translating rest of the blocks instructions and each successor block 
   #iterate through all instructions

   #Get list of all blocks to iterate through
   blockList = getAllBlocks(cfg)

   #Iterate through blockList and translate instructions
   #for each block
   print(f"%%%%%%%%%%%%%%%GLOBALS_AND_LOCALS: {globals_and_locals}")
   for var in globals_and_locals:
      initVar(cfg.entry.label, var)
   for block in blockList:
      if block.label != cfg.entry.label:
         llvmInstrs.append(f"L{block.label}:")
      llvmInstrs.append("<PHI placeholder>")
      for instr in block.instrs:
         print(f"translating instruction: {instr}")
         translateInstr(
               instr, 
               block, 
               llvmInstrs, 
               globals_and_locals, 
               structTypes,
               cfg)
   """
   curBlock = cfg.entry
   for instr in curBlock.instrs:
      #llvmInstrs = translateInstr(instr, cfg)
      #for llvmInstr in llvmInstrs:
         #instrs.append(llvmInstr)
   """
   return llvmInstrs

def getAllBlocks(cfg):
   startBlock = cfg.entry
   endBlock = cfg.exit

   iterQue = queue.Queue()
   blockList = []

   iterQue.put(startBlock)
   blockList.append(startBlock)

   while not iterQue.empty():
      curBlock = iterQue.get()
      #curBlock.visited = True
      for block in curBlock.succrs:
         """
         if not block.visited:
            iterQue.put(block)
            blockList.append(block)
         """
         if block not in blockList:
            iterQue.put(block)
            blockList.append(block)
   """
   for block in blockList:
      block.visited = False
   """

   return blockList



"""
programCfg
   types
   decls
   funcCfgs
      [cfg ...]
"""

def lookupLlvmType(llvmType):
   #TODO add in type for structs
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
      paramTable[param['id']] = lookupLlvmType(param['type'])

   paramStrs = []

   for param in params:
      paramStrs.append(f"{param['type']} %{param['id']}")

   formattedParamStr = ""
   for paramStr in paramStrs:
      formattedParamStr += paramStr + ","
   #remove trailing comma
   return formattedParamStr[:len(formattedParamStr) - 1]


def translateProg(progCfg, globalSyms, structTypes):
   #print(progCfg.funcCfgs)
   progFuncs = {}
   
   for cfg in progCfg.funcCfgs:
      #progFuncs.add(cfg.funcName, funcLlvm(cfg))
      progFuncs[cfg.funcName] = funcLlvm(cfg, globalSyms, structTypes)

   return progFuncs

def combineDict(lhs, rhs):
   tmp = lhs.copy()
   tmp.update(rhs)
   return tmp

def declListToDict(someList):
   tmpDict = dict()
   for entry in someList:
      tmpDict[entry['id']] = entry

   return tmpDict

class funcLlvm:
   def __init__(self, cfg, globalSyms, structTypes):
      print("STARTING TO MAKE THE FUNCLLVM")
      #self.header = f"define {lookupLlvmType(retType)} @{funcId}({lookupParamTypes(params)})"
      self.funcId = cfg.funcName
      self.retType = lookupLlvmType(cfg.returnType)
      self.params = lookupParamTypes(cfg.params)
      #self.openBlock = "{"
      print(f"Global Syms Type: {type(globalSyms)}\tLocalDecls Type: {type(cfg.localDecls)}")
      print(f"GlobalSyms: \n{globalSyms}")
      print(f"localSyms: \n{cfg.localDecls}")
      self.instrs = translateInstrs(
            cfg, 
            combineDict(globalSyms, declListToDict(cfg.localDecls)), 
            structTypes)
      #self.closeBlock = "}"
   """
   def __str__(self):
      print(self.header)
      print(self.openBlock)
      for instr in self.instrs:
         print(instr)
      print(self.closeBlock)
   """

