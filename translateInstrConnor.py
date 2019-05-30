import llvmTranslator


# mapping -- a dictionary that maps string to int. Used to map identifiers to registers
# types -- the list of types declared at the beginning of the json file
# decls -- the list of global and local declarations for the function
def transInstr(instr, llvmInstrList, currBlock, mapping,types,decls, funcCfg):
   # Insert return instruction if at the cfg exit block
   if len(currBlock.succrs) == 0:
      if funcCfg.returnType == "void":
         llvmInstrList.append("ret void")
      else:
         retReg = llvmTranslator.lookupLabelDecl(currBlock, 'return')
         retInstr = f"ret {funcCfg.returnType} {retReg}"
         llvmInstrList.append(retInstr)
      return

   # check if guard for if/else or while statement
   if "guard" in instr:
      transBrInstr(instr["guard"], llvmInstrList, currBlock, mapping, 
                   decls, types, funcCfg)
      # Break out of guard translation
      return
    
   ###################################################
   # Not a guard expression
  
   # Check if passed an expression
   if "stmt" not in instr:
      return getExpReg(instr, llvmInstrList, mapping, currBlock, decls, types,
                       funcCfg)

   # Translate STATEMENT
   instrStmt = instr["stmt"]

   if instrStmt == "assign":
      ###################################################
      # translate source
      sourceReg = getExpReg(instr["source"], llvmInstrList, mapping, 
                            currBlock, decls, types, funcCfg)

      ###################################################
      # translate target
      if "left" in instr["target"]: # store source in struct field
         targetType = lookupLlvmType(instr["target"], decls, types)
         targetReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                       instr["target"], decls, types)
         
         llvmInstrList.append(f"store {targetType} {sourceReg}, " +
                              f"{targetType}* {targetReg}")
      else: # update mapping
         targetId = instr["target"]["id"]
         #print(f"mapping: {mapping}\nMapping dict index: {targetId}")
         #print("transInstr error: trying to write value into mapping" +
         #      f" but can't.\n    Mapping is  {mapping}\n    " +
         #      f"Mapping key is  {targetId}")

         #llvmTranslator.addLabelDecl(label, var, regName)
         llvmTranslator.addLabelDecl(currBlock.label, targetId, 
                                     int(sourceReg[2:]))
         #mapping[targetId] = sourceReg

   elif instrStmt == "delete":
      sourceReg = getExpReg(instr["exp"], llvmInstrList, mapping, 
                            currBlock, decls, types, funcCfg)
      sourceType = lookupLlvmType(instr["exp"], decls, types)
      bitcastReg = f"%u{llvmTranslator.getNextRegLabel()}"
      
      llvmInstrList.append(bitcastReg + f" = bitcast {sourceType} " +
                           f"{sourceReg} to i8*")
      llvmInstrList.append(f"call void @free(i8* {bitcastReg})")
   elif instrStmt == "return":
      if "exp" in instr:
         #sourceType = lookupLlvmType(instr["exp"], decls, types)
         sourceReg = getExpReg(instr["exp"], llvmInstrList, mapping,
                               currBlock, decls, types, funcCfg)
         print("transInstr error: trying to write return value into mapping" +
               f" but can't.\nMapping is  {mapping}")
         llvmTranslator.addLabelDecl(currBlock.label, "return", 
                                     int(sourceReg[2:]))
         #mapping["return"] = sourceReg

      #TODO: hope this doesn't break translation
      exitBlock = currBlock
      # Locate the CFG exit block
      while len(exitBlock.succrs) > 0:
         exitBlock = exitBlock.succrs[0]

      # Add the return statement to the Exit block to remind the translator
      # that it must be translated. 
      # TODO: I'm hoping this will also work with the phi instructions.
      # Depending on how phi instructions are handled, this may need changing
      exitBlock.instrs.append(instr)

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
      print(f"transInstr err: Unrecognized statement '{instrStmt}' in instr:" +
            f"\n{instr}")


def transBrInstr(guard, llvmInstrList, currBlock, idToRegMap,decls,types,cfg):
   if len(currBlock.succrs) < 2:
      print("transInstr err: Cannot evaluate branch instruction. Too few" +
            f" successors to current block when evaluating guard {guard}")
   #llvmInstrList.append(guardEvalInstr)
   guardEvalReg = getExpReg(guard, llvmInstrList, idToRegMap, currBlock,
                            decls, types, cfg)
   llvmInstrList.append(f"br i1 {guardEvalReg}, label "+
                        f"%LU{currBlock.succrs[0].label}, label "+
                        f"%LU{currBlock.succrs[1].label}")


# returns either the register of the identifier or expression, or the
#   immediate value
# exp types: id, num, binary, new, dot, invocation, read
def getExpReg(expr, llvmInstrList, mapping, currBlock, decls, types, cfg):
   resultReg = ""
   
   if expr["exp"] == "id":  # identifier
      return llvmTranslator.lookupLabelDecl(currBlock, expr["id"])
      #return mapping.get(expr["id"])
   if expr["exp"] == "num":  # immediate
      return expr["value"] 
   if expr["exp"] == "binary":  # binary expr with a left and right side
      resultReg = f"%u{llvmTranslator.getNextRegLabel()}"
      llvmInstr = resultReg + " = "

      operator = expr["operator"]
      # eq, ne, sgt, sge, slt, sle
      if operator == "<=":
         llvmInstr += "icmp sle i32 "
      elif operator == ">=":
         llvmInstr += "icmp sge i32 "
      elif operator == ">":
         llvmInstr += "icmp sgt i32 "
      elif operator == "<":
         llvmInstr += "icmp slt i32 "
      elif operator == "==":
         llvmInstr += "icmp eq i32 "
      elif operator == "!=":
         llvmInstr += "icmp ne i32 "
      elif operator == "-":
         llvmInstr += "add i32 "
      elif operator == "+":
         llvmInstr += "sub i32 "
      elif operator == "*":
         llvmInstr += "mul i32 "
      elif operator == "/":
         llvmInstr += "sdiv i32 "
      else:
         print("getExpReg error: Unknown or unaccounted operator: '" +
               operator + "'")
         print(f"in expression: {expr}")

      leftSide = getExpReg(expr["lft"], llvmInstrList, mapping, currBlock,
                           decls, types, cfg)
      rightSide = getExpReg(expr["rht"], llvmInstrList, mapping, currBlock,
                            decls, types, cfg)
      llvmInstr += (f"{leftSide}, {rightSide}")
      llvmInstrList.append(llvmInstr)
   elif expr["exp"] == "new":
      # Get number of fields
      fieldCount = -1
      for typ in types:
         #print(f"types: {types}")
         #print(f"expr: {expr}\ntyp: {typ}")
         if expr["id"] == typ:
            fieldCount = len(types[typ]["fields"])
      if fieldCount == -1:
         print("getExpReg error: Tried to create new " +
               f"{expr['id']}, but not in types.")
         
      mallocReg = llvmTranslator.getNextRegLabel()
      llvmInstrList.append(f"%u{mallocReg} = call i8* " +
                           f"@malloc(i32 {fieldCount})")
      resultReg = f"%u{llvmTranslator.getNextRegLabel()}"
      llvmInstrList.append(f"{resultReg} = bitcast i8* " + 
                           f"%u{mallocReg} to " + 
                           f"%struct.{expr['id']}*")
   elif expr["exp"] == "dot":
      # TODO: If problem with dot expressions, refer here
      structPtrReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                       expr, decls, types, True)
      resultReg = "%u" + str(loadFromStructField(llvmInstrList, 
                                 lookupLlvmType(expr, decls, types),
                                 structPtrReg))
   elif expr["exp"] == "invocation":
      #TODO: Make sure invocation works
      resultReg = llvmTranslator.translateInstr(expr, currBlock,
                                    llvmInstrList, decls, types, cfg)
   elif expr["exp"] == "read":
      llvmInstrList.append("call i32 (i8*, ...)* @scanf(i8* getelementptr " +
                           "inbounds([4 x i8]* @.read, i32 0, i32 0), " +
                           "i32* @.read_scratch)")
      resultReg = f"%u{llvmTranslator.getNextRegLabel()}"
      llvmInstrList.append(f"{resultReg} = load i32* @.read_scratch")
   else:
      print("getExpReg error: Unrecognized expression type '" + expr["exp"] +
            f"' in expression: {expr}")

   return resultReg


def lookupLlvmType(target, decls, types):
   llvmType = lookupStructType(target, decls, types)
   
   if llvmType == "int" or llvmType == "bool":
      return "i32"
   elif llvmType == "void":
      return "void"
   elif llvmType == None:
      return "i32"
   else:
      return f"%struct.{llvmType}*"


def lookupStructType(target, decls, types):
   if "left" in target:
      leftStructType = lookupStructType(target["left"], decls, types)
      for typ in types:
         if typ == leftStructType:
            for field in types[typ]["fields"]:
               if field["id"] == target["id"]:
                  return field["type"]
      # none of the types' fields matched the target's left identifier
      print("getStructType Error: Could not find type for left of target: \n" +
            f"{target}\nwithin types: \n{types}")

   else:
      for decl in decls:
         if decl == target["id"]:
            return decls[decl]["type"]
      # no declaration matched target's identifier
      print("getStructType Error: Could not find type for target: \n" +
            f"{target}\nwithin declarations:\n{decls}")

   # If no types came up from looking in the types, return None
   return None


def getStructFieldReg(llvmInstrList, mapping, currBlock, target, decls, types,
                      withLoad = False):
   leftStructType = lookupStructType(target["left"], decls, types)
   leftStructLlvmType = lookupLlvmType(target["left"], decls, types)
   #rightType = lookupStructType(target, decls, types)
   rightLlvmType = lookupLlvmType(target, decls, types)
   fieldReg = -1
   if "left" in target["left"]:
      if withLoad:
         tmpFieldReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                         target, decls, types)
         fieldReg = loadFromStructField(llvmInstrList, rightLlvmType,
                                        tmpFieldReg)
      else:
         tmpFieldReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                         target["left"], decls, types, True)
         fieldReg = llvmTranslator.getNextRegLabel()
         # get field number
         fieldNum = -1
         for typ in types:
            if typ == leftStructType:
               for i in range(len(types[typ]["fields"])):
                  if types[typ]["fields"][i]["id"] == target["id"]:
                     fieldNum = i
         if fieldNum == -1:
            print("getStructFieldReg error: no type found for ")

         llvmInstrList.append(f"%u{fieldReg} = getelementptr " +
                              f"{leftStructLlvmType} " +
                              f"%u{tmpFieldReg}, " +
                              f"i1 0, i32 {fieldNum}")

   else:
      if withLoad:
         tmpfieldReg = getStructFieldReg(llvmInstrList, mapping, currBlock,
                                         target, decls, types)
         fieldReg = loadFromStructField(llvmInstrList, rightLlvmType, 
                                        tmpfieldReg)
      else:
         fieldReg = llvmTranslator.getNextRegLabel()
         # get field number
         fieldNum = -1
         for typ in types:
            if typ == leftStructType:
               for i in range(len(types[typ]["fields"])):
                  if types[typ]["fields"][i]["id"] == target["id"]:
                     fieldNum = i
         if fieldNum == -1:
            print("getStructFieldReg error: no type found for ")

         structReg = llvmTranslator.lookupLabelDecl(currBlock, 
                                                    target['left']['id'])
         #structReg = mapping.get(target['left']['id'])
         llvmInstrList.append(f"%u{fieldReg} = getelementptr " +
                              f"{leftStructLlvmType} " +
                              f"%u{structReg}, " +
                              f"i1 0, i32 {fieldNum}")

   return fieldReg


def loadFromStructField(llvmInstrList, fieldType, fieldReg):
   toReg = llvmTranslator.getNextRegLabel()
   llvmInstrList.append(f"%u{toReg} = load {fieldType}* %u{fieldReg}")
   return toReg

