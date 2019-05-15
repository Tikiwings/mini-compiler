
def getNextRegLabel():
   global regLabel
   retReg = regLabel
   regLabel += 1
   return retReg


# mapping -- a dictionary that maps string to int. Used to map identifiers to registers
# types -- the list of types declared at the beginning of the json file
# decls -- the list of global and local declarations for the function
def transInstr(instr, llvmInstrList, currBlock, mapping, types, decls):
   # check if guard for if/else or while statement
   if "guard" in instr:
      # TODO: add branching instructions
      
      return

   instrStmt = instr["stmt"]

   if instrStmt == "assign":
      ###################################################
      # translate source
      sourceReg = -1
      
      if instr["source"]["exp"] == "new":
         # Get number of fields
         fieldCount = -1
         for typ in types:
            if instr["source"]["id"] == typ["id"]:
               fieldCount = len(typ["fields"])
         if fieldCount == -1:
            print("transInstr error: Tried to create new " +
                  f"{instr['source']['id']}, but not in types.")
         
         mallocReg = getNextRegLabel()
         llvmInstrList.append(f"%u{mallocReg} = call i8* " +
                              f"@malloc(i32 {fieldCount})")
         sourceReg = getNextRegLabel()
         llvmInstrList.append(f"%u{sourceReg} = bitcast i8* " + 
                              f"%u{mallocReg} to " + 
                              f"%struct.{instr['source']['id']}*")
      
      elif instr["source"]["exp"] == "dot":
         # TODO: add instructions for loading from struct field
         pass

      # TODO: make compatible with cases for other types of source expressions 


      if sourceReg == -1:
         print("transInstr error: source register unknown")


      ###################################################
      # translate target
      if "left" in instr["target"]: # store source in struct field
         targetType = lookupLlvmType(instr["target"], decls, types)
         targetReg = getStructFieldReg(llvmInstrList, mapping, target, decls,
                                       types)
         llvmInstrList.append(f"store {targetType} %u{sourceReg}, " +
                              f"{targetType}* {targetReg}")
      else: # update mapping
         targetId = instr["target"]["id"]
         mapping[targetId] = targetReg


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
      leftStructType = getStructType(target["left"], decls, types)
      for typ in types:
         if typ["id"] == leftStructType:
            for field in typ["fields"]:
               if field["id"] == target["id"]:
                  return field["type"]
      # none of the types' fields matched the target's left identifier
      print("getStructType Error: Could not find type for left of target: \n" +
            f"{target}\nwithin types: \n{types}")

   else:
      for decl in decls:
         if decl["id"] == target["id"]:
            return decl["type"]
      # no declaration matched target's identifier
      print("getStructType Error: Could not find type for target: \n" +
            f"{target}\nwithin declarations:\n{decls}")

   # If no types came up from looking in the types, return None
   return None


def getStructFieldReg(llvmInstrList, mapping, target, decls, types, 
                      withLoad = False):
   leftStructType = lookupStructType(target["left"], decls, types)
   leftStructLlvmType = lookupLlvmType(target["left"], decls, types)
   rightType = lookupStructType(target, decls, types)
   rightLlvmType = lookupLlvmType(target, decls, types)
   fieldReg = -1
   if "left" in target["left"]:
      if withLoad:
         tmpFieldReg = getStructFieldReg(llvmInstrList, target, decls, types)
         fieldReg = loadFromStructField(llvmInstrList, rightLlvmType,
                                        tmpFieldReg)
      else:
         tmpFieldReg = getStructField(llvmInstrList, target["left"], decls,
                                      types, True)
         fieldReg = getNextRegLabel()
         # get field number
         fieldNum = -1
         for typ in types:
            if typ["id"] == leftStructType:
               for i in range(len(typ["fields"])):
                  if typ["fields"][i]["id"] == target["id"]:
                     fieldNum = i
         if fieldNum == -1:
            print("getStructFieldReg error: no type found for ")

         llvmInstrList.append(f"%u{fieldReg} = getelementptr " +
                              f"{leftStructLlvmType} " +
                              f"%u{tmpFieldReg}, " +
                              f"i1 0, i32 {fieldNum}")

   else:
      if withLoad:
         tmpfieldReg = getStructFieldReg(llvmInstrList, mapping, target, decls,
                                      types, False)
         fieldReg = loadFromStructField(llvmInstrList, rightLlvmType, 
                                        tmpfieldReg)
      else:
         fieldReg = getNextRegLabel()
         # get field number
         fieldNum = -1
         for typ in types:
            if typ["id"] == leftStructType:
               for i in range(len(typ["fields"])):
                  if typ["fields"][i]["id"] == target["id"]:
                     fieldNum = i
         if fieldNum == -1:
            print("getStructFieldReg error: no type found for ")

         llvmInstrList.append(f"%u{fieldReg} = getelementptr " +
                              f"{leftStructLlvmType} " +
                              f"%u{mapping[target['left']['id']]}, " +
                              f"i1 0, i32 {fieldNum}")

   return fieldReg


def loadFromStructField(llvmInstrList, fieldType, fieldReg):
   toReg = getNextRegLabel()
   llvmInstrList.append(f"%u{toReg} = load {fieldType}* %u{fieldReg}")
   return toReg

