#!/bin/python3
import json
import sys
#import stmtChecks as st
from stmtChecks import lookupType, lookupExpType, checkStmt

types = ("int", "bool", "struct id")

def makeStructTable(prog, structTable):
   for struct in prog["types"]:
      #print(struct)
      #print("\n\n")
      #structTable.append(struct["id"])
      addDecl(structTable, struct)

def getGlobalDecls(prog, symTable):
   for ID in prog["declarations"]:
      addDecl(symTable, ID)


##################################################################################
#Error functions
def redeclError(dup):
   print("Redeclration error\n\tline:{}\n\tid:{}\n".format(dup["line"], dup["id"]))

def returnError(funcId):
   print("Return error in func: {} not return equivalent\n".format(funcId))

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

def createJson():
   with open(sys.argv[1], "r") as f:
      progFile = json.load(f)
   #print(json.dumps(progFile, indent=4))
   return progFile

def main():
   symTable = {"__global__" : {}}
   structTable = {}
   funTable = {}
   progFile = createJson()

   makeStructTable(progFile, structTable)
   getGlobalDecls(progFile, symTable["__global__"])
   checkFuncs(progFile, symTable, structTable, funTable)

   #print(structTable)
   #print(symTable)

   ''' for x,y in progFile.items():
      for p in progFile[x]:
         print(p)
      print("=======================================================")
   '''


main()
