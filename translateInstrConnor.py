import llvmTranslator

# mapping -- a dictionary that maps string to int. Used to map identifiers to registers
# types -- the list of types declared at the beginning of the json file
# decls -- the list of global and local declarations for the function
def transInstr(instr, llvmInstrList, currBlock, mapping, types, decls, 
               funcCfg, milestone2 = False):
   #print(f"&&&Connor.transInstr: decls:\n   {decls}")
   
   # Insert return instruction if at the cfg exit block
   if len(currBlock.succrs) == 0:
      #TODO: Ask Donnie if he handles void return statements
      if funcCfg.returnType == "void":
         #llvmInstrList.append("ret void")
         pass
      else:
         if milestone2:
            retType = convertLlvmType(funcCfg.returnType)
            retReg = f"%u{llvmTranslator.getNextRegLabel()}"
            llvmInstrList.append(f"{retReg} = load {retType}* %_retval_")
            llvmInstrList.append(f"ret {retType} {retReg}")
         else:
            retReg = llvmTranslator.lookupLabelDecl(currBlock, 'return')
            retInstr = f"ret {convertLlvmType(funcCfg.returnType)} {retReg}"
            llvmInstrList.append(retInstr)
      return

   # check if guard for if/else or while statement
   if "guard" in instr:
      transBrInstr(instr["guard"], llvmInstrList, currBlock, mapping, 
                   decls, types, funcCfg, milestone2)
      # Break out of guard translation
      return
    
   ###################################################
   # Not a guard expression
  
   # Check if passed an expression
   if "stmt" not in instr:
      return getExpReg(instr, llvmInstrList, mapping, currBlock, decls, types,
                       funcCfg, milestone2)

   # Translate STATEMENT
   instrStmt = instr["stmt"]

   if instrStmt == "assign":
      ###################################################
      # translate source
      sourceReg = getExpReg(instr["source"], llvmInstrList, mapping, 
                            currBlock, decls, types, funcCfg, milestone2)

      ###################################################
      # translate target
      targetType = lookupLlvmType(instr["target"], decls, types, currBlock)

      if "left" in instr["target"]: # store source in struct field
         targetType = lookupLlvmType(instr["target"], decls, types, currBlock)
         targetReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                       instr["target"], decls, types,
                                       milestone2)
         
         llvmInstrList.append(f"store {targetType} {sourceReg}, " +
                              f"{targetType}* {targetReg}")
      else: # update block declarations
         targetId = instr["target"]["id"]

         if milestone2:
            storeInstr = (f"store {targetType} {sourceReg}, {targetType}* " +
                          f"%{targetId}")
            llvmInstrList.append(storeInstr)
         else:
            llvmTranslator.addLabelDecl(currBlock.label, targetId, 
                                        sourceReg)

   elif instrStmt == "delete":
      sourceReg = getExpReg(instr["exp"], llvmInstrList, mapping, 
                            currBlock, decls, types, funcCfg, milestone2)
      sourceType = lookupLlvmType(instr["exp"], decls, types, currBlock)
      bitcastReg = f"%u{llvmTranslator.getNextRegLabel()}"
      
      llvmInstrList.append(bitcastReg + f" = bitcast {sourceType} " +
                           f"{sourceReg} to i8*")
      llvmInstrList.append(f"call void @free(i8* {bitcastReg})")
   elif instrStmt == "return":
      if "exp" in instr:
         #sourceType = lookupLlvmType(instr["exp"], decls, types)
         sourceReg = getExpReg(instr["exp"], llvmInstrList, mapping,
                               currBlock, decls, types, funcCfg, milestone2)
         if milestone2:
            retType = convertLlvmType(funcCfg.returnType)
            storeInstr = f"store {retType} {sourceReg}, {retType}* %_retval_"
            llvmInstrList.append(storeInstr)
         else:
            llvmTranslator.addLabelDecl(currBlock.label, "return", 
                                        sourceReg)

      exitBlock = currBlock
      # Locate the CFG exit block
      while len(exitBlock.succrs) > 0:
         exitBlock = exitBlock.succrs[0]

      # Add the return statement to the Exit block to remind the translator
      # that it must be translated. 
      # TODO: I'm hoping this will also work with the phi instructions.
      # Depending on how phi instructions are handled, this may need changing
      
      if len(exitBlock.instrs) == 0:
         exitBlock.instrs.append(instr)
   elif instrStmt == "print":
      sourceReg = getExpReg(instr["exp"], llvmInstrList, mapping, currBlock,
                            decls, types, funcCfg, milestone2)

      # Start off the print instruction
      printInstr = ("call i32 (i8*, ...)* @printf(i8* getelementptr " +
                    "inbounds ([5 x i8]* @.print")
 
      # Check for endl in print statement
      if instr["endl"] == True:
         printInstr += "ln"

      # Finish off the print instruction
      printInstr += f", i32 0, i32 0), i32 {sourceReg})"

      llvmInstrList.append(printInstr)
   elif instrStmt == "invocation":
      """
      argList = []
      argTypeList = []
      for arg in instr["args"]:
         argList.append(getExpReg(arg, llvmInstrList, mapping, currBlock,
                                  decls, types, funcCfg))
         argTypeList.append(lookupLlvmType(arg, decls, types))

      # TODO: change return type to reflect method of obtaining it
      returnType = "void"
      invocLlvmInstr = f"call void @{instr['id']}("
      for argIndex in range(len(argList)):
         invocLlvmInstr += f"{argTypeList[argIndex]} {argList[argIndex]}"
         if argIndex < len(argList) - 1:
            invocLlvmInstr += ", "
      invocLlvmInstr += ")"

      llvmInstrList.append(invocLlvmInstr)
      """
      pass
   else:
      print(f"&&&Connor.transInstr err: Unrecognized statement '{instrStmt}'"+
            f"\nin instr: {instr}")


def transBrInstr(guard, llvmInstrList, currBlock, idToRegMap, decls, types,
                 cfg, milestone2 = False):
   if len(currBlock.succrs) < 2:
      print("&&&Connor.transBrInstr err: Cant evaluate branch instruction."+
            f"  Too few succrs to current block when evaluating guard {guard}")
   guardEvalReg = getExpReg(guard, llvmInstrList, idToRegMap, currBlock,
                            decls, types, cfg, milestone2)
   llvmInstrList.append(f"br i1 {guardEvalReg}, label "+
                        f"%LU{currBlock.succrs[0].label}, label "+
                        f"%LU{currBlock.succrs[1].label}")


# returns either the register of the identifier or expression, or the
#   immediate value
# exp types: id, num, binary, new, dot, invocation, read, unary
def getExpReg(expr, llvmInstrList, mapping, currBlock, decls, types, cfg,
              milestone2 = False):
   resultReg = ""
   
   if expr["exp"] == "id":  # identifier
      if milestone2:
         #TODO: if problems with null, refer here
         loadToReg = f"%u{llvmTranslator.getNextRegLabel()}"
         exprType = lookupLlvmType(expr, decls, types, currBlock)
         loadFromReg = llvmTranslator.lookupLabelDecl(currBlock, expr['id'])
         llvmInstrList.append(f"{loadToReg} = load {exprType}* {loadFromReg}")

         return loadToReg
      else:
         return llvmTranslator.lookupLabelDecl(currBlock, expr["id"])
   if expr["exp"] == "num":  # immediate
      return expr["value"] 
   if expr["exp"] == "null":
      return 'null'
   if expr["exp"] == "unary":  # operator is only '-'
      negatant = getExpReg(expr["operand"], llvmInstrList, mapping, currBlock,
                           decls, types, cfg, milestone2)
      resultReg = f"%u{llvmTranslator.getNextRegLabel()}"
      llvmInstr = resultReg + " = "

      operator = expr["operator"]
      if operator == "-":
         llvmInstr += f"sub i32 0, {negatant}"
      elif operator == "!":  # TODO: zext/trunc if type error
         llvmInstr += f"xor i1 true, {negatant}"

      llvmInstrList.append(llvmInstr)
   elif expr["exp"] == "binary":  # binary expr with a left and right side
      resultReg = f"%u{llvmTranslator.getNextRegLabel()}"
      llvmInstr = resultReg + " = "

      #print(f"&&&Connor.getExpReg: translating expr:\n   {expr}")

      operator = expr["operator"]
      if operator == "<=":
         llvmInstr += "icmp sle i32 "
      elif operator == ">=":
         llvmInstr += "icmp sge i32 "
      elif operator == ">":
         llvmInstr += "icmp sgt i32 "
      elif operator == "<":
         llvmInstr += "icmp slt i32 "
      elif operator == "==":
         operandType = lookupLlvmType(expr['lft'], decls, types, currBlock)
         if operandType == None:
            operandType = lookupLlvmType(expr['rht'], decls, types, currBlock)
            if operandType == None:
               print("&&&Connor.getExpReg: No type for either operand in expr:\n"+
                     f"   {expr}")      
         llvmInstr += f"icmp eq {operandType} "
      elif operator == "!=":
         operandType = lookupLlvmType(expr['lft'], decls, types, currBlock)
         if operandType == None:
            operandType = lookupLlvmType(expr['rht'], decls, types, currBlock)
            if operandType == None:
               print("&&&Connor.getExpReg: No type for either operand in expr:\n"+
                     f"   {expr}")
         llvmInstr += f"icmp ne {operandType} "
      elif operator == "-":
         llvmInstr += "sub i32 "
      elif operator == "+":
         llvmInstr += "add i32 "
      elif operator == "*":
         llvmInstr += "mul i32 "
      elif operator == "/":
         llvmInstr += "sdiv i32 "
      elif operator == "&&":  # TODO: zext/trunc if type errors
         llvmInstr += "and i1 "
      elif operator == "||":
         llvmInstr += "or i1 "
      else:
         print(f"getExpReg error: Unknown or unaccounted operator: {operator}")
         print(f"   in expression: {expr}")

      leftSide = getExpReg(expr["lft"], llvmInstrList, mapping, currBlock,
                           decls, types, cfg, milestone2)
      rightSide = getExpReg(expr["rht"], llvmInstrList, mapping, currBlock,
                            decls, types, cfg, milestone2)
      llvmInstr += f"{leftSide}, {rightSide}"
      llvmInstrList.append(llvmInstr)
   elif expr["exp"] == "new":
      # Get number of fields
      fieldCount = -1
      for typ in types:
         if expr["id"] == typ:
            fieldCount = len(types[typ]["fields"])
      if fieldCount == -1:
         print("&&&Connor.getExpReg error: Tried to create new " +
               f"{expr['id']}, but not in types.")
         
      mallocReg = f"%u{llvmTranslator.getNextRegLabel()}"
      llvmInstrList.append(f"{mallocReg} = call i8* " +
                           f"@malloc(i32 {fieldCount * 4})")
      resultReg = f"%u{llvmTranslator.getNextRegLabel()}"
      llvmInstrList.append(f"{resultReg} = bitcast i8* " + 
                           f"{mallocReg} to " + 
                           f"%struct.{expr['id']}*")
   elif expr["exp"] == "dot":
      # TODO: If problem with dot expressions, refer here
      structPtrReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                       expr, decls, types)
      resultReg = loadFromStructField(llvmInstrList, 
                            lookupLlvmType(expr, decls, types, currBlock),
                            structPtrReg)
   elif expr["exp"] == "invocation":
      resultReg = llvmTranslator.translateInstr(expr, currBlock,
                                    llvmInstrList, decls, types, cfg)
   elif expr["exp"] == "read":
      llvmInstrList.append("call i32 (i8*, ...)* @scanf(i8* getelementptr " +
                           "inbounds([4 x i8]* @.read, i32 0, i32 0), " +
                           "i32* @.read_scratch)")
      resultReg = f"%u{llvmTranslator.getNextRegLabel()}"
      llvmInstrList.append(f"{resultReg} = load i32* @.read_scratch")
   else:
      print("Connor.getExpReg error: Unrecognized expression type\n  " +
            f"'{expr['exp']}' in expression: {expr}")

   return resultReg


def lookupLlvmType(target, decls, types, currBlock):
   if "exp" in target and target["exp"] == "null":
      return None
   #if target['exp'] == 'num':
   #   return 'i32'

   miniType = lookupStructType(target, decls, types, currBlock)
  
   if miniType == None:
      print("&&&Connor.lookupLlvmType ERROR: 'None' returned from " +
            "Connor.lookupStructType.\n    No type was found for " +
            f"argument {target}")

   return convertLlvmType(miniType)


def convertLlvmType(miniType):
   if miniType == "int" or miniType == "bool":
      return "i32"
   elif miniType == "void":
      return "void"
   elif miniType == None:
      return "i32"
   else:
      return f"%struct.{miniType}*"


def lookupStructType(target, decls, types, currBlock):
   #print(f"&&&Running lookupStructType on target:\n   {target}")
   if "left" in target:
      leftStructType = lookupStructType(target["left"],decls,types, currBlock)
      for typ in types:
         if typ == leftStructType:
            for field in types[typ]["fields"]:
               if field["id"] == target["id"]:
                  return field["type"]
      # none of the types' fields matched the target's left identifier
      print("&&&Connor.lookupStructType err: Could not find type for" +
            f"left of target:\n    {target}\n    within types: \n    {types}")

   else:
      for decl in decls:
         if decl == target["id"]:
            return decls[decl]["type"]
      # no declaration matched target's identifier
      print("&&&Connor.lookupStructType Error: Could not find type for"+
            f" target:\n   {target}\n    within declarations:\n    {decls}")

   # If no types came up from looking in the types, return None
   return None


def getStructFieldReg(llvmInstrList, mapping, currBlock, target, decls, types,
                      withLoad = False):
   leftStructType = lookupStructType(target["left"], decls, types, currBlock)
   leftStructLlvmType = lookupLlvmType(target["left"], decls, types, currBlock)
   rightLlvmType = lookupLlvmType(target, decls, types, currBlock)
   fieldReg = ""
   if "left" in target["left"]:
      if withLoad:
         tmpFieldReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                         target, decls, types)
         fieldReg = loadFromStructField(llvmInstrList, rightLlvmType,
                                        tmpFieldReg)
      else:
         tmpFieldReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                         target["left"], decls, types, True)
         fieldReg = f"%u{llvmTranslator.getNextRegLabel()}"
         
         # get field number
         fieldNum = -1
         for typ in types:
            if typ == leftStructType:
               for i in range(len(types[typ]["fields"])):
                  if types[typ]["fields"][i]["id"] == target["id"]:
                     fieldNum = i
         if fieldNum == -1:
            print("&&&Connor.getStructFieldReg err: no type found for "+
                  f"expression: {target}\n   within types: {types}")

         llvmInstrList.append(f"{fieldReg} = getelementptr " +
                              f"{leftStructLlvmType} " +
                              f"{tmpFieldReg}, " +
                              f"i1 0, i32 {fieldNum}")

   else:
      if withLoad:
         tmpfieldReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                         target, decls, types)
         fieldReg = loadFromStructField(llvmInstrList, rightLlvmType, 
                                        tmpfieldReg)
      else:
         fieldReg = f"%u{llvmTranslator.getNextRegLabel()}"
         
         # get field number
         fieldNum = -1
         for typ in types:
            if typ == leftStructType:
               for i in range(len(types[typ]["fields"])):
                  if types[typ]["fields"][i]["id"] == target["id"]:
                     fieldNum = i
         if fieldNum == -1:
            print("&&&Connor.getStructFieldReg err: no type found for "+
                  f"expression: {target}\n   within types: {types}")

         structReg = llvmTranslator.lookupLabelDecl(currBlock, 
                                                    target['left']['id'])
         llvmInstrList.append(f"{fieldReg} = getelementptr " +
                              f"{leftStructLlvmType} " +
                              f"{structReg}, i1 0, i32 {fieldNum}")

   return fieldReg


def loadFromStructField(llvmInstrList, fieldType, fieldReg):
   toReg = f"%u{llvmTranslator.getNextRegLabel()}"
   llvmInstrList.append(f"{toReg} = load {fieldType}* {fieldReg}")
   return toReg

