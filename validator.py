#!/bin/python3
import json
import sys
#import stmtChecks as st
from stmtChecks import lookupType, lookupExpType, checkStmt, didPass, checkFailed
from cfg import buildProg
from llvmTranslator import translateProg, handlePhi, getAllLabelDeclTables
import re

#types = ("int", "bool", "struct id")



def makeStructTable(prog, structTable):
   for struct in prog["types"]:
      #print(struct)
      #print("\n\n")
      #structTable.append(struct["id"])
      addDecl(structTable, struct)

def getGlobalDecls(prog, symTable):
   for ID in prog["declarations"]:
      addDecl(symTable, ID)



#=================================Flags==========================================
printLlvm = False

def setPrintFlag():
   global printLlvm
   printLlvm = True

def getPrintFlag():
   global printLlvm
   return printLlvm

#================================================================================


##################################################################################
#Error functions
def redeclError(dup):
   checkFailed()
   print("Redeclration error\n\tline:{}\n\tid:{}\n".format(dup["line"], dup["id"]))

def returnError(funcId):
   checkFailed()
   print("Return error in func: {} not return equivalent\n".format(funcId))

def typeCheckFailed():
   print("Errors found while type checking.\nFix the found errors in order to compile")
   sys.exit(1)

##################################################################################


#check if main is present. Exit if not
def checkForMain(funList):
   mainExist = False
   for fun in funList:
      if fun["id"] == "main":
         mainExist = True
         #print("main found")
   return mainExist


def checkIfReturns(ifStmt):
   thenReturn = False
   elseReturn = False

   thenStmt = ifStmt.get("then")
   elseStmt = ifStmt.get("else")

   if thenStmt:
      for stmt in thenStmt["list"]:
         if stmt["stmt"] == "if":
            thenReturn = checkIfReturns(stmt)

         elif stmt["stmt"] == "while":
            thenReturn = checkWhileReturns(stmt)

         elif stmt["stmt"] == "return":
            thenReturn = True
      
   if elseStmt:
      for stmt in elseStmt["list"]:
         if stmt["stmt"] == "if":
            elseReturn = checkIfReturns(stmt)

         elif stmt["stmt"] == "while":
            elseReturn = checkWhileReturns(stmt)

         elif stmt["stmt"] == "return":
            elseReturn = True
   
   if elseStmt:
      if thenReturn and elseReturn:
         return True
      else:
         return False
   else:
      return thenReturn



def checkWhileReturns(whileStmt):
   for stmt in whileStmt["body"]["list"]:
      if stmt["stmt"] == "if":
         if checkIfReturns(stmt):
            return True

      elif stmt["stmt"] == "while":
         if checkWhileReturns(stmt):
            return True

      elif stmt["stmt"] == "return":
         return True
   return False

def checkReturns(func):
   if func["return_type"] == "void":
      return True

   for stmt in func["body"]:
      if stmt["stmt"] == "if":
         if checkIfReturns(stmt):
            return True

      elif stmt["stmt"] == "while":
         if checkWhileReturns(stmt):
            return True

      elif stmt["stmt"] == "return":
         return True
   return False



#check if checkMe is a duplication declrations in the current
#set of declarations
'''
def checkDups(decls, checkMe):
   for decl in decls:
      if decl["id"] is checkMe["id"]:
         return (decl["id"], checkMe["id"])
   return None
'''

#attempt to add decl by checking sym table
#for an existing id
def addDecl(table, decl):
   #TODO allow for new declarations to overwrite globals
   '''
   dup = checkDups(symTable, decl)
   if dup is None:
      symTable.append(decl)
   else:
      redeclError(decl)
   '''
   if decl["id"] not in table:
      newId  = decl["id"]
      table[newId] = decl
   else:
      redeclError(decl)


#check and validate a function in the program
def checkFunc(func, symTable, structTable, funTable):
   for param in func["parameters"]:
      addDecl(symTable, param)

   for decl in func["declarations"]:
      addDecl(symTable, decl)
      #symTable.append(decl)

   if func.get("return_type") != None:
      if not checkReturns(func):
         returnError(func.get("id"))

   for stmt in func["body"]:
      #st.checkStmt(syms, funcs, structs, stmt)
      checkStmt(symTable, funTable, structTable, stmt, func)
      #print(stmt)
      #print("\n")
   
#checks and provides setup to check each function in program
def checkFuncs(prog, symTable, structTable, funTable):
   if not checkForMain(prog["functions"]):
      print("No Main function")
      sys.exit(1)

   #get each function decl from the prog json
   for item in prog["functions"]:
      addDecl(funTable, item)
      #funTable.append(item["id"])
   
   #check each function decl in the prog
   #provides a local copy of the symTable for each function
   for func in prog["functions"]:
      symTableCpy = symTable.copy()
      print("==========================")
      print("Checking function: {}".format(func["id"]))
      print("==========================\n")
      checkFunc(func, symTableCpy, structTable, funTable)


def parseArgs():
   args = sys.argv.copy()
   if "-stack" in sys.argv:
      args.remove("-stack")
      setPrintFlag()
   return args[1]




def createJson(fileName):
   with open(fileName, "r") as f:
      progFile = json.load(f)
   #print(json.dumps(progFile, indent=4))
   return progFile


def transGlobals(globals):
   globStrs = list()
   
   for var in globals:
      globType = var['type']
      if globType == "int" or globType == "bool":
         globTypeStr = "i32"
      else:
         globTypeStr = f"%struct.{globType}*"
      globStrs.append(f"@{var['id']} = common global {globTypeStr} null, align 8")

   return globStrs


def transStructs(structs):
   structStrs = list()

   for struct in structs:
      structType = struct['id']
      structStr = f"%struct.{structType} = type "
      structStr += "{"
      for field in struct['fields']:
         fieldType = field['type']

         if fieldType == "int" or fieldType == "bool":
            structStr += "i32, "
         else:
            structStr += f"%struct.{fieldType}*, "
      structStr = structStr[:-2] + "}"
      structStrs.append(structStr)
   return structStrs




def main():
   symTable = {"__global__" : {}}
   structTable = {}
   funTable = {}
   fileName = parseArgs()
   if "." in fileName:
      llvmFileName = re.search("(.*)[.].*", fileName).groups()[0] + ".ll"
   else:
      llvmFileName = re.search("(.*)json.*", fileName).groups()[0] + ".ll"
   progFile = createJson(fileName)

   makeStructTable(progFile, structTable)
   getGlobalDecls(progFile, symTable["__global__"])
   checkFuncs(progFile, symTable, structTable, funTable)

   #check if type checking passed without errors
   #exit if not and continue if passed
   if not didPass():
      typeCheckFailed()
   
   #don't print if flag is not set
   if not getPrintFlag():
      sys.exit(1)

   #print(structTable)
   #print(symTable)
   progCfg = buildProg(progFile)
   progCfg.printProg()
   progFuncs = translateProg(
         progCfg, 
         symTable["__global__"],
         structTable,
         funTable)

   print("#####################################")
   print("###########Llvm Prog#################")
   print("#####################################")
   #print(f"Writing to {llvmFileName}")
   #print(f"Choices with {fileName}: {re.search('(.*)[.]*.*', fileName).groups()}")
   llvmFile = open(llvmFileName, "w+")

   #LLvm header, struct definitions, and globals
   print("target triple=\"i686\"")
   llvmFile.write("target triple=\"i686\"\n")
   for str in transStructs(progFile['types']):
      print(str)
      llvmFile.write(str + "\n")
   for str in transGlobals(progFile['declarations']):
      print(str)
      llvmFile.write(str + "\n")

   #LLvm instructions translation
   for func in progFuncs.keys():
      print(f"define {progFuncs[func].retType} @{progFuncs[func].funcId}({progFuncs[func].params})")
      print("{")
      llvmFile.write(f"define {progFuncs[func].retType} @{progFuncs[func].funcId}({progFuncs[func].params})\n")
      llvmFile.write("{\n")
      curLabel = None
      for instr in progFuncs[func].instrs:
         labels = re.findall("\ALU[1234567890]*:", instr.strip())
         if len(labels) >= 1:
            curLabel = int(labels[0][2:-1])
         if instr == "<PHI placeholder>":
            #print(f"    <PHI placeholder found>")
            phiInstrs = handlePhi(curLabel)
            for phi in phiInstrs:
               print(f"    {phi}")
               llvmFile.write(f"    {phi}\n")
         else:
            print(f"    {instr}")
            llvmFile.write(f"    {instr}\n")
      print("}\n")
      llvmFile.write("}\n")
   print(f"""declare i8* @malloc(i32)
declare void @free(i8*)
declare i32 @printf(i8*, ...)
declare i32 @scanf(i8*, ...)
@.println = private unnamed_addr constant [5 x i8] c"%ld\\0A\\00", align 1
@.print = private unnamed_addr constant [5 x i8] c"%ld \\00", align 1
@.read = private unnamed_addr constant [4 x i8] c"%ld\\00", align 1
@.read_scratch = common global i32 0, align 4""")
   llvmFile.write(f"""declare i8* @malloc(i32)
declare void @free(i8*)
declare i32 @printf(i8*, ...)
declare i32 @scanf(i8*, ...)
@.println = private unnamed_addr constant [5 x i8] c"%ld\\0A\\00", align 1
@.print = private unnamed_addr constant [5 x i8] c"%ld \\00", align 1
@.read = private unnamed_addr constant [4 x i8] c"%ld\\00", align 1
@.read_scratch = common global i32 0, align 4\n""")
   print(f"All Decls {getAllLabelDeclTables()}")
   print(f"Phi Decls {getAllLabelDeclTables().get('incPhis')}")
   ''' for x,y in progFile.items():
      for p in progFile[x]:
         print(p)
      print("=======================================================")
   '''
   llvmFile.close()

if __name__ == "__main__":
   main()
