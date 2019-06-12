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
#current function being looked at
curFunc = None

#global type of printing (stack / ssa)
printType = "stack"

#global register counter
regLabel = 0

#global dictionaries
labelDecls = {}
funcTable = {}
funcSymTable = {}

visitedBlocks = set()


#global accessor methods
def getFuncTable():
   global funcTable
   return funcTable

def visited(label):
   global visitedBlocks
   return label in visitedBlocks

def getFuncSymType(funcId, varId, globalSym = False):
   global funcSymTable
   if globalSym == True:
      if funcSymTable["__global__"].get(varId):
         return funcSymTable["__global__"][varId].get('type')
   if funcSymTable[funcId].get(varId):
      return funcSymTable[funcId][varId].get('type')
   elif funcSymTable['__global__'].get(varId):
      return funcSymTable['__global__'][varId].get('type')
      #return None
   return None

def isGlobal(varId):
   global funcSymTable
   if funcSymTable[getCurFunc()].get(varId):
      return False
   elif funcSymTable['__global__'].get(varId):
      return True
   else:
      return False


def getPrintType():
   global printType
   return printType

def getCurFunc():
   global curFunc
   return curFunc


#global mutator methods
def addVisited(label):
   global visitedBlocks
   visitedBlocks.add(label)

def addfunSymTable(funcId, syms):
   global funcSymTable
   funcSymTable[funcId] = syms

def addFuncSymEntry(funcId, symName, sym, globalSym = False):
   global funcSymTable
   if globalSym == True:
      if not funcSymTable.get("__global__"):
         funcSymTable["__global__"] = dict()
      funcSymTable["__global__"][symName] = sym
      return
   if not funcSymTable.get(funcId):
      funcSymTable[funcId] = dict()
   funcSymTable[funcId][symName] = sym
   return

def setPrintType(pType):
   global printType
   printType = pType

def setCurFunc(funcName):
   global curFunc
   curFunc = funcName

##############################

def storeVar(funcId, varName, llvmInstrs):
   pass

def loadVar(funcId, varName, llvmInstrs):
   loadReg = getNextRegLabel()

   loadType = lookupLlvmType(getFuncSymType(funcId, varName))
   
   """
   if loadType:
      llvmInstrs.append(f"%u{loadReg} = load {loadType}* %{varName}")
   else:
      loadType = lookupLlvmType(getFuncSymType(funcId, varName, globalSym = True))
      llvmInstrs.append(f"%u{loadReg} = load {loadType}* @{varName}")
   """

   if not isGlobal(varName):
      llvmInstrs.append(f"%u{loadReg} = load {loadType}* %{varName}")
   else:
      loadType = lookupLlvmType(getFuncSymType(funcId, varName, globalSym = True))
      llvmInstrs.append(f"%u{loadReg} = load {loadType}* @{varName}")


   return f"%u{loadReg}"


def transArith(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg):
   
   printType = getPrintType()

   op = instr['operator']
   #resultReg = getNextRegLabel()

   lhsType = instr['lft']['exp']
   rhsType = instr['rht']['exp']
   print(f"\tlhsType: {lhsType}\nrhsType: {rhsType}")
   
   if lhsType == "num":
      lhs = instr['lft']['value']
   elif lhsType == "id":
      if printType == "stack":
         lhs = loadVar(getCurFunc(), instr['lft']['id'], llvmInstrs)
      else:
         lhs = lookupLabelDecl(block, instr['lft']['id'], instrType = "i32")
   elif lhsType == "unary":
      lhsInstr = instr['lft']
      negation = False
      if lhsInstr['operator'] == "-":
         while lhsInstr.get("exp") == "unary":
            lhsInstr = lhsInstr.get("operand")
            negation = not negation
      if lhsInstr.get('exp') == "num":
         lhs = lhsInstr['value']
      elif lhsInstr.get('exp') == "id":
         if printType == "stack":
            lhs = loadVar(getCurFunc(), lhsInstr['id'], llvmInstrs)
         else:
            lhs = lookupLabelDecl(block, lhsInstr['id'], instrType = "i32")
      if negation:
         lhs = "-" + lhs
   elif lhsType == "invocation":
      lhs = translateInstr(instr['lft'], block, llvmInstrs, globals_and_locals, structTypes, cfg)
         


   if rhsType == "num":
      rhs = instr['rht']['value']
   elif rhsType == "id":
      if printType == "stack":
         rhs = loadVar(getCurFunc(), instr['rht']['id'], llvmInstrs)
      else:
         rhs = lookupLabelDecl(block, instr['rht']['id'], instrType = "i32")
   elif rhsType == "unary":
      rhsInstr = instr['rht']
      negation = False
      if rhsInstr['operator'] == "-":
         while rhsInstr.get("exp") == "unary":
            rhsInstr = rhsInstr.get("operand")
            negation = not negation
      if rhsInstr.get('exp') == "num":
         rhs = rhsInstr['value']
      elif rhsInstr.get('exp') == "id":
         if printType == "stack":
            rhs = loadVar(getCurFunc(), rhsInstr['rht']['id'], llvmInstrs)
         else:
            rhs = lookupLabelDecl(block, rhsInstr['id'], instrType = "i32")
      if negation:
         rhs = "-" + rhs
   elif rhsType == "invocation":
      rhs = translateInstr(instr['rht'], block, llvmInstrs, globals_and_locals, structTypes, cfg)


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
   printType = getPrintType()
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
   print(f"\tICMP lType: {lhsType}\n\tICMP rType: {rhsType}")
   
   if lhsType == "num":
      lhs = instr['lft']['value']
   elif lhsType == "id":
      if printType == "stack":
         lhs = loadVar(getCurFunc(), instr['lft']['id'], llvmInstrs)
      else:
         lhs = lookupLabelDecl(block, instr['lft']['id'], instrType = "i32")
   else:
      lhs = translateInstr(instr['lft'], block, llvmInstrs, globals_and_locals, structTypes, cfg)


   if rhsType == "num":
      rhs = instr['rht']['value']
   elif rhsType == "id":
      if printType == "stack":
         rhs = loadVar(getCurFunc(), instr['rht']['id'], llvmInstrs)
      else:
         rhs = lookupLabelDecl(block, instr['rht']['id'], instrType = "i32")
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


#recursive version with more abstraction
#if in paramRegs/imm is a string then its a register of it is an int then it is an imm
#params can only be arithmetic, nums, bools, invocations
def transInvoc(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg):
   paramRegs = [None] * len(instr['args'])
   paramTypes = [None] * len(instr['args'])
   invocRetType = getFuncTable()[instr['id']]['return_type']

   for i in range(len(instr["args"])):
      if instr["args"][i] == "invocation":
         paramRegs[i] = transInvoc(instr["args"][i], block, llvmInstrs, globals_and_locals, structTypes, cfg)
         paramTypes[i] = getFuncTable()[instr['args'][i]['id']]['return_type']

      else:
         #paramRegs[i] = getNextRegLabel()
         paramRegs[i] = translateInstr(instr['args'][i], block, llvmInstrs, globals_and_locals, structTypes, cfg)
         paramTypes[i] = lookupLlvmType(getFuncTable()[instr['id']]['parameters'][i]['type'])
         """
         if instr['args'][i]['exp'] == 'id':
            paramTypes[i] = lookupLlvmType(getFuncSymType(getCurFunc(), instr['args'][i]['id']))
         elif instr['args'][i]['exp'] == 'invocation':
            paramTypes[i] = lookupLlvmType(getFuncTable()[instr['args'][i]['id']]['return_type'])
         elif instr['args'][i]['exp'] == 'dot':
            #paramTypes[i] = lookupLabelDecl(getDotType(instr, globals_and_locals, structTypes))
            paramTypes[i] = lookupLlvmType(translateInstrConnor.lookupStructType(instr['args'][i], globals_and_locals, structTypes, block))
         elif instr['args'][i]['exp'] == 'null':
            paramTypes[i] = lookupLlvmType(getFuncTable()[getCurFunc()]['parameters'][i]['type'])


         else:
            paramTypes[i] = 'i32'
         """

         
   paramStr = """"""
   for i in range(len(paramRegs)):
      if i != 0 and i != len(paramRegs):
         paramStr += ", "
      paramStr += f"{paramTypes[i]} {paramRegs[i]}"
   resultReg = getNextRegLabel()

   if invocRetType == "void":
      llvmInstrs.append(f"call {invocRetType} @{instr['id']}({paramStr})")
      return None
   elif invocRetType == "int":
      llvmInstrs.append(f"%u{resultReg} = call i32 @{instr['id']}({paramStr})")
      return f"%u{resultReg}"
   elif invocRetType == "bool":
      llvmInstrs.append(f"%u{resultReg} = call i1 @{instr['id']}({paramStr})")
      return f"%u{resultReg}"
   else:
      llvmInstrs.append(f"%u{resultReg} = call %struct.{invocRetType}* @{instr['id']}({paramStr})")
      return f"%u{resultReg}"


def transUnary(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg):
   negation = False
   instrItr = instr
   retVal = None
   while instrItr.get('exp') == "unary":
      instrItr = instrItr.get('operand')
      negation = not negation
   
   retValType = instrItr.get("exp")
   if retValType == "num":
      retVal  = instrItr.get("value")
   elif retValeType == "id":
      retVal = lookupLabelDecl(block, instrItr['id'])

   if negation:
      retVal = "-" + retVal
   return retVal

def transAlloc():
   return ""

def transMisc():
   return ""
"""
def getDotType(instr, globals_and_locals, structTypes):
   dotType = None
   leftList = list()

   while instr['exp'] == 'dot':
      leftList.append(instr['id'])
      instr = instr['left']
"""




#TODO instruction may be dict({guard: instr})
def lookupInstrType(instr):

   if "guard" in instr:
      return "guard"

   instrType = instr.get('stmt')
   if not instrType:
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
   
   elif instrType == "id":
      return "id"

   elif instrType == "null":
      return "null"

   elif instrType == "unary":
      return "unary"

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

   elif instrType == "id":
      if getPrintType() == "stack":
         return loadVar(getCurFunc(), instr['id'], llvmInstrs)
      else:
         return lookupLabelDecl(block, instr['id'])

   elif instrType == "unary":
      return transUnary(instr, block, llvmInstrs, globals_and_locals, structTypes, cfg)

   elif instrType == "block":
      for blockInstr in instr['list']:
         translateInstr(blockInstr, block, llvmInstrs, globals_and_locals, structTypes, cfg)

   #elif instrType == "return":


   else:
      #pass the instruction to connors translation
      if  getLabelDeclTable(block.label) == None:
         #print(f"ERROR: empty mapping:\n\tblock: {block.label}\ninstr:{instr}")
         print(f"block {block.label} decls : {getLabelDeclTable(block.label)}")
      if getPrintType() == "stack":
         return translateInstrConnor.transInstr(
               instr, 
               llvmInstrs, 
               block,
               getLabelDeclTable(block.label),
               structTypes,
               globals_and_locals,
               cfg,
               getFuncTable(),
               milestone2 = True) 
      else:
         return translateInstrConnor.transInstr(
               instr, 
               llvmInstrs, 
               block,
               getLabelDeclTable(block.label),
               structTypes,
               globals_and_locals,
               cfg,
               getFuncTable()) 
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
   
   labelDecls[label][var] = regName

   """
   if type(regName) == int:
      labelDecls[label][var] = f"%u{regName}"
   else:
      if re.match("[1234567890]+", regName):
         labelDecls[label][var] = regName
      else:
         labelDecls[label][var] = "%" + regName 
   """

def initVar(label, var):
   global labelDecls
   if not labelDecls.get(label):
      labelDecls[label] = dict()

   labelDecls[label][var] = None
   print(f"Added {var} to decls")


def getLabelDeclTable(label):
   global labelDecls

   return labelDecls.get(label)

def getAllLabelDeclTables():
   global labelDecls
   return labelDecls

#TODO
def handlePhi(label, funcId):
   global labelDecls
   print(f"<Looking for phis in label {label}>")
   phiStrList = list()

   if labelDecls.get(label):
      if labelDecls[label].get("incPhis"):
         print(f"Looking at Label: {label} inc phis: {labelDecls[label]['incPhis']}")
         for phiReg in labelDecls[label]["incPhis"]:
            #print(phiInstr)
            #phiStr = f"%u{phiReg} = phi {labelDecls[label]['incPhis'][phiReg]['type']} "
            phiStr = f"%u{phiReg} = phi {lookupLlvmType(getFuncSymType(funcId, labelDecls[label]['incPhis'][phiReg]['varName']))} "
            for pred in labelDecls[label]["incPhis"][phiReg]["block"].preds:
               alreadyComputed = False
               phiLabelLoc = [None]
               for param in labelDecls[label]["incPhis"][phiReg]["params"]:
                  if param['startLabel'] == pred.label:
                     alreadyComputed = True
                     #phiStr += f"[{param['reg']}, %LU{param['label']}],"
                     phiStr += f"[{param['reg']}, %LU{pred.label}],"
               if not alreadyComputed:
                  print("Lookup starting from handler")
                  sourceReg = lookupLabelDecl(pred, labelDecls[label]["incPhis"][phiReg]['varName'], phiLabelLoc) 
                  #phiStr += f"[{sourceReg}, %LU{phiLabelLoc[0]}],"
                  phiStr += f"[{sourceReg}, %LU{pred.label}],"
            phiStrList.append(phiStr[:-1])
   return phiStrList


   """
   if labelDecls.get("incPhis"):
      if labelDecls["incPhis"].get(label):
         for key in labelDecls["incPhis"][label]:
            print(f"key {key}\tval: {labelDecls['incPhis'][label][key]}")
            #return None
   """

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
#TODO fix phi's with bools to be i1
def lookupLabelDecl(block, varName, phiLabelLoc = None, phiHandler = False, instrType = None):
   global labelDecls
   print(f"looking for {varName} in {block.label}")
   #TODO fix this to propogate upwards correctly   
   reg = None
   if labelDecls.get(block.label):
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
         return lookupLabelDecl(block.preds[0], varName, phiLabelLoc, phiHandler = phiHandler, instrType = instrType)
      else:
         return lookupLabelDecl(block.preds[0], varName, phiHandler = phiHandler, instrType = instrType)

   else:
      phiReg = getNextRegLabel()
      print(f"Adding decl {varName} -> {phiReg}")
      if not labelDecls.get(block.label):
         labelDecls[block.label] = dict()
      labelDecls[block.label][varName] = f"%u{phiReg}" 
      if labelDecls[block.label].get('incPhis') == None:
         labelDecls[block.label]['incPhis'] = dict()

      labelDecls[block.label]['incPhis'][phiReg] = dict()
      labelDecls[block.label]['incPhis'][phiReg]['block'] = block
      labelDecls[block.label]['incPhis'][phiReg]['varName'] = varName
      labelDecls[block.label]['incPhis'][phiReg]['params'] = list()



      preds = block.preds
      for pred in preds:
         print(f"Looking for {varName} in pred label {pred.label}... visited: {visited(pred.label)}")
         if visited(pred.label):
            phiLabel = [None]
            lookupReg = lookupLabelDecl(pred, varName, phiLabelLoc = phiLabel, instrType = instrType)
            labelDecls[block.label]['incPhis'][phiReg]['params'].append({
               "reg": lookupReg, 
               "label":phiLabel[0], 
               "startLabel" : pred.label})
            print(f"Phi entry: {labelDecls[block.label]['incPhis'][phiReg]}")

         """
         else:
            labelDecls[block.label]['incPhis'][phiReg].append({"reg":None, "label": None})
         """
      """
      if not labelDecls[block.label]['incPhis'][phiReg].get('type'):
         labelDecls[block.label]['incPhis'][phiReg]['type'] = instrType
      """

      return f"%u{phiReg}"
         
#"""

"""
def phiLookup():
"""


def completePhi(block, varName, phiLabelLoc):
   pass


def translateInstrs(cfg, globals_and_locals, structTypes):
   llvmInstrs = []
   llvmInstrs.append(f"LU{cfg.entry.label}:")
   """ 
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
   """

   #set current working function
   setCurFunc(cfg.funcName)
   
   #Get list of all blocks to iterate through
   blockList = getAllBlocks(cfg)

   #initialize and add local/global vars
   print(f"%%%%%%%%%%%%%%%GLOBALS_AND_LOCALS: {globals_and_locals}")
   for var in globals_and_locals:
      initVar(cfg.entry.label, var)
      #addFuncSymEntry(cfg.funcName, var, globals_and_locals[var])
   for param in cfg.params:
      #addLabelDecl(cfg.entry.label, param['id'], param['id'] )
      addLabelDecl(cfg.entry.label, param['id'], "%" + param['id'] )
      addFuncSymEntry(cfg.funcName, param['id'], param)
   addFuncSymEntry(cfg.funcName, 'return', {'type' : cfg.returnType})

   if getPrintType() == "stack":
      if cfg.returnType != "void":
         retType = lookupLlvmType(cfg.returnType)
         llvmInstrs.append(f"%_retval_ = alloca {retType}")

      for param in cfg.params:
         paramType = lookupLlvmType(param['type'])
         llvmInstrs.append(f"%{param['id']} = alloca {paramType}")

      for local in cfg.localDecls:
         localType = lookupLlvmType(local['type'])
         llvmInstrs.append(f"%{local['id']} = alloca {localType}")

      for param in cfg.params:
         paramType = lookupLlvmType(param['type'])
         llvmInstrs.append(f"store {paramType} %_P_{param['id']}, {paramType}* %{param['id']}")

   #Iterate through blockList and translate instructions
   #for each block
   for block in blockList:
      if block.label != cfg.entry.label:
         llvmInstrs.append(f"LU{block.label}:")


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
      if len(block.succrs) == 1:
         llvmInstrs.append(f"br label %LU{block.succrs[0].label}")

      if block.label == cfg.exit.label and cfg.returnType == "void":
         llvmInstrs.append("ret void")


      print(f"Block {block.label} has been completely visited")
      addVisited(block.label)
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
      return "i1"
   elif llvmType == "void":
      return "void"
   else:
      #return "i32"
      return f"%struct.{llvmType}*"

def lookupParamTypes(params):
   paramTable = {}
   printType = getPrintType()
   
   for param in params:
      paramTable[param['id']] = lookupLlvmType(param['type'])

   paramStrs = []

   if printType == "stack":
      for param in params:
         paramStrs.append(f"{paramTable[param['id']]} %_P_{param['id']}")
   else:
      for param in params:
         paramStrs.append(f"{paramTable[param['id']]} %{param['id']}")

   formattedParamStr = ""
   for paramStr in paramStrs:
      formattedParamStr += paramStr + ","
   #remove trailing comma
   return formattedParamStr[:len(formattedParamStr) - 1]


def translateProg(progCfg, globalSyms, structTypes, funTable, pType):
   #print(progCfg.funcCfgs)
   global funcTable
   progFuncs = {}
   funcTable = funTable

   setPrintType(pType)
   
   for sym in globalSyms:
      addFuncSymEntry(None, sym, globalSyms[sym], globalSym = True)

   for cfg in progCfg.funcCfgs:
      #progFuncs.add(cfg.funcName, funcLlvm(cfg))
      for sym, entry in combineDict(declListToDict(cfg.localDecls), declListToDict(cfg.params)).items():
         addFuncSymEntry(cfg.funcName, sym, entry)
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
      #print(cfg.params)
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
            combineDict(combineDict(globalSyms, declListToDict(cfg.localDecls)),declListToDict(cfg.params)), 
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

