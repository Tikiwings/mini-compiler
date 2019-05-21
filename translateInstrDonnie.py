

   #invocation
   #boolean
   #arithmetic
#return list of llvm instruction strings
def transArith(instr, llvmInstrs):
   #instrs = []
   op = instr['operator']
   #resultReg = getNextRegLabel()

   lhsType = instr['lft']['exp']
   lrhsType = instr['rht']['exp']
   
   if lhsType == "num":
      lhs = instr['lft']['value']
   elif lhsType == "id":
      lhs = lookupLabelDecl(label, instr['lft']['id']


   if rhsType == "num":
      rhs = instr['rht']['value']
   elif rhsType == "id":
      rhs = lookupLabelDecl(label, instr['rht']['id']


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

   return target 

#looks at all the params of a given invocation and store in them in the order they appear in a list
#the index number will be the given params position
#each param will be the exp from the args section
#if an param is an invocation then recurse to this method again and create a new list for that invocations params'
#  that invocations params will be returned as a list which will be put in its param position from where it was called
"""
def checkInvoParams(instr):
   params = []

   for arg in instr['args']:
      if arg['exp'] != "invocation":
         params.append(arg)
      else:
         params.append(checkInvoParams(arg))
   return params

#TODO test this out on paper
def getInvoParams(invoc):
   InvocList = [None]*len(invoc['args'])

   for i in range(len(invoc['args'])):
      if invoc['args'][i]['exp'] == "invocation":
         invocList[i].append((invoc['args'][i], getInvoParams(invoc['args'][i]))
      else:
         invocList[i] = None
      
   return InvocList
"""

"""
def evalInvoParams(params, funcId, invoCalls=[], instrs=[]):
   for param in params:
"""


#recursive version with more abstraction
#if in paramRegs/imm is a string then its a register of it is an int then it is an imm
#params can only be arithmetic, nums, bools, invocations
def transInvoc(instr, cfg, llvmInstrs):
   paramRegs = [None] * len(instr['args'])

   for i in range(len(instr["args"])):
      if instr["args"][i] == "invocation":
         paramRegs[i] = transInvoc(instr["args"][i], cfg, llvmInstrs)

      else:
         #paramRegs[i] = getNextRegLabel()
         paramRegs[i] = translateInstr(instr['args'][i], cfg, llvmInstrs)

   paramStr = """"""
   for i in range(len(paramRegs)):
      if i != 0 and i != len(paramRegs) - 1:
         paramStr += ", "
      paramStr += f"i32 {paramRegs[i]}"
   resultReg = getNextRegLabel()
   llvmInstrs.append(f"%u{resultReg} = call @{instr['id']}({paramStr})")
   return f"%u{resultReg}"
 

#dont treat params as distinct things, abstract them to be just exps and then map over them into a list of the instructions they would end up creating
"""
def transInvoc(instr, cfg):
   instrs = []
   
   #paramStr will be params translated into there llvm form
   paramStr = ""
   for param in cfg.params:
      #TODO figure out how to handle invocations as params and how to remember
      #the register they store their value in
      if param['exp'] == "invocation":
         paramInstr = transInvoc(param, cfg)

      llvmType = lookupLlvmType(param['type'])
      #lookup the current register for each param
      paramReg = lookupLabelDecl(cfg, param['id'])
      paramStr += f"{llvmType} {paramReg}, "

   funcId = instr['id']
   if cfg.returnType == "void":
      instrs.append(f"call void @{funcId}({paramStr[:len(paramStr] - 1})")
   else:
      instrs.append(f"{getNextRegLabel()} = call { lookupLlvmType(cfg.returnType) } @{funcId}({len( paramStr ) - 1})")

   return instrs
"""

def transCmp(instr, llvmInstrs):
   #instrs = []
   op = instr["operator"]
   
   if op == "==":
      cond = "eq"
   elif op == "!=":
      cond = "ne":
   elif op == "<":
      cond = "slt"
   elif op == "<=":
      cond = "sle"
   elif op == ">":
      cond = "sgt"
   elif op == ">=":
      cond = "sge"

   target = getNextRegLabel()
   llvmInstrs.append(f"%u{target} = icmp {cond} i32 {lhs}, {rhs}")

   return target

"""
def transBool():
   return None
"""

