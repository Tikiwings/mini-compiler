
'''
Types of Stmt:
   
   return
      -exp

   if
      -guard
         -exp
         -operator
         -lft
         -rht
      -then
         -block
         -list
      -else <is not required>
         -block
         -list

   block
      -list
   
   assign
      -source
      -target
   
   print
      -exp
      -endl -> boolean

   while
      -guard
      -body

   invocation
      -id -> function name
      -args -> list of args
'''
'''
   EXP Types
      -num
      -binary
      -id
      -{}
      -invocation
      -dot
      -null
      -true
      -false
      -new

   
'''

#=======================ERROR Functions============================================

def typeError(stmt):
   print("Type error found: Line - {}".format(stmt["line"]))

def funcError(stmt):
   print("Func error found:\n\tLine - {}\n\tFunc: {}".format(stmt["line"], stmt["id"]))

def argCountError(stmt, actual, given):
   print("Incorrect number of arguments error found:\n\tLine: {}\n\t\
         args needed: {}\n\targs given: {}".format(stmt["line"], actual, given))

def guardError(stmt):
   print("Guard error found:\n\tLine: {}\n\t".format(stmt["line"]))


#====================================================================================



def checkReturn(syms, funcs, structs, stmt, func):
   retType = func["return_type"]
   expType = lookupExpType(syms, funcs, structs, stmt)

   if not checkTypes(retType, expType):
      typeError(stmt)


def checkIf(syms, funcs, structs, stmt, func):
   guardType = lookupExpType(syms, funcs, structs, stmt["guard"])
   if guardType is not "bool":
      guardError(stmt)

   checkStmt(syms, funcs, structs, stmt["then"], func)
   
   elseStmt = stmt.get("else")
   if elseStmt is not None:
      checkStmt(syms, funcs, structs, elseStmt, func)

def checkBlock(syms, funcs, structs, stmt, func):
   for blckStmt in stmt["list"]:
      checkStmt(syms, funcs, structs, blckStmt, func)


def checkAssign(syms, funcs, structs, stmt, func):
   source = stmt["source"]
   target = stmt["target"]
   
   tarId = target["id"]

   #tarType = vd.lookupType(syms, tarId)
   #sourceType = vd.lookupExpType(syms, funcs, structs, stmt)
   tarType = lookupType(syms, tarId)
   sourceType = lookupExpType(syms, funcs, structs, stmt)

   if checkTypes(tarType, sourceType):
      typeError(stmt)


def checkPrint(syms, funcs, structs, stmt, func):
   return None

def checkWhile(syms, funcs, structs, stmt, func):
   guardType = lookupExpType(syms, funcs, structs, stmt["guard"])

   if guardType is not "bool":
      guardError(stmt)

   checkStmt(syms, funcs, structs, stmt["body"], func)



def checkInvocation(syms, funcs, structs, stmt):
   if stmt["id"] not in funcs:
      funcError(stmt)
      return

   argsStmts = stmt["args"]
   paramStmts = funcs[stmt["id"]]["paramaters"]

   if len(argStmts) is not len(paramStmts):
      argCountError(stmt, len(paramStmts), len(argStmts))
      return

   for i in range(len(argStmts)):
      argType = lookupExpType(syms, funcs, structs, argStmts[i])
      paramType = paramStmts[i]["type"]
      
      if not checkTypes(argType, paramType):
         typeError(stmt)


def checkStmt(syms, funcs, structs, stmt, func):
   if stmt["stmt"] is "return":
      checkReturn(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] is "if":
      checkIf(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] is "block":
      checkBlock(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] is "assign":
      checkAssign(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] is "print":
      checkPrint(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] is "while":
      checkWhile(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] is "invocation":
      checkInvocation(syms, funcs, structs, stmt)



#check if two types are equivalent or null
def checkTypes(t1, t2):
   if t1 is not t2:
      if t1 is "null" or t2 is "null":
         return True
      return False
   return True

#lookup varID in symTable to find what type it is 
#and if it exists
def lookupType(syms, varID):
   if varID in syms:
      return syms[varID]["type"]
   else:
      return None

#lookup what type an exp equates to
def lookupExpType(syms, funcs, structs, stmt):
   exp = stmt["exp"]

   if exp is "num":
      return "int"

   elif exp is "binary":
      #TODO typeCheck binary expression here
      op = exp["operator"]
      if op in ("+", "-", "/", "*", "%"):
         return "int"
      elif op in ("<", ">", "<=", ">="):
         return "bool"

   elif exp is "id":
      return lookupType(syms, stmt["id"])

   elif type(exp) is type(dict()):
      #TODO evaluate whats in the dictionary block
      return None

   elif exp is "invocation":
      #TODO check func params here
      checkInvocation(syms, funcs, structs, exp)
      return funcs[stmt["id"]]["return_type"]

   elif exp is "dot":
      #TODO check that field is a part of the lhs var
      return None

   elif exp is "null":
      return "null"

   elif exp is "true":
      return "bool"

   elif exp is "false":
      return "bool"
   
   elif exp is "new":
      return stmt["id"]

