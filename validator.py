#!/bin/python3
import json
import sys

types = ("int", "bool", "struct id")
structTable = []

def makeStructTable(prog):
   for struct in prog["types"]:
      print(struct)
      print("\n\n")
      structTable.append(struct["id"])

def getGlobalDecls(prog, symTable):
   for ID in prog["declarations"]:
      symTable.append(ID)

#def checkFuncs(prog):

def createJson():
   with open(sys.argv[1], "r") as f:
      progFile = json.load(f)
   #print(json.dumps(progFile, indent=4))
   return progFile

def main():
   symbolTable = []
   progFile = createJson()

   makeStructTable(progFile)
   getGlobalDecls(progFile, symbolTable)

   print(structTable)
   print(symbolTable)

   ''' for x,y in progFile.items():
      for p in progFile[x]:
         print(p)
      print("=======================================================")
   '''


main()
