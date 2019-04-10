#!/bin/python3
import json
import sys

types = ("int", "bool", "struct id")

def makeStructTable(prog, structTable):
   for struct in prog["types"]:
      print(struct)
      print("\n\n")
      structTable.append(struct["id"])

def getGlobalDecls(prog, symTable):
   for ID in prog["declarations"]:
      symTable.append(ID)

#check if main is present. Exit if not
def checkForMain(funList):
   mainExist = False
   for fun in funList:
      if fun["id"] is "main":
         mainExist = True
   return mainExist

#check if two types are equivalent or null
def checkTypes(t1, t2):
   if t1 is not t2:
      if t1 is "null" or t2 is "null":
         return True
      return False
   return True

#check if checkMe is a duplication declrations in the current
#set of declarations
def checkDups(decls, checkMe):
   for decl in decls:
      if decl["id"] is checkMe["id"]:
         return (decl["id"], checkMe["id"])
   return None

#check and validate a function in the program
def checkFunc(func, symTable, structTable, funTable):
   #TODO fix this
   for param in func["parameters"]:
      if 
         symTable.append(param)

   for decl in func["declarations"]:
      symTable.append(decl)
   
#checks and provides setup to check each function in program
def checkFuncs(prog, symTable, structTable, funTable):
   if not checkForMain(prog["functions"]):
      sys.exit(1)

   #get each function decl from the prog json
   for item in prog["functions"]:
      funTable.append(item["id"])
   
   #check each function decl in the prog
   #provides a local copy of the symTable for each function
   for func in prog["functions"]:
      symTableCpy = symTable.copy()
      checkFunc(func, symTableCpy, structTable, funTable)

def createJson():
   with open(sys.argv[1], "r") as f:
      progFile = json.load(f)
   #print(json.dumps(progFile, indent=4))
   return progFile

def main():
   symbolTable = []
   structTable = []
   funTable = []
   progFile = createJson()

   makeStructTable(progFile, structTable)
   getGlobalDecls(progFile, symbolTable)
   checkFuncs(progFile, symTable, structTable, funTable)

   print(structTable)
   print(symbolTable)

   ''' for x,y in progFile.items():
      for p in progFile[x]:
         print(p)
      print("=======================================================")
   '''


main()
