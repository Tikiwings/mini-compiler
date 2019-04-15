
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
      -{} -> exp
      -invocation
      -dot
         -left
         -id 
      -null
      -true
      -false
      -new
      -unary

   
'''

#=======================ERROR Functions============================================

def typeError(stmt):
   print("Type error found: Line: {}\n".format(stmt["line"]))

def funcError(stmt):
   print("Func error found:\n\tLine: {}\n\tFunc: {}\n".format(stmt["line"], stmt["id"]))

def argCountError(stmt, actual, given):
   print("Incorrect number of arguments error found:\n\tLine: {}\n\t\
         args needed: {}\n\targs given: {}\n".format(stmt["line"], actual, given))

def guardError(stmt):
   print("Guard error found:\n\tLine: {}\n".format(stmt["line"]))

def binaryError(stmt):
   print("Binary error found:\n\tLine: {}".format(stmt["line"]))

def structError(left, fieldId, errMsg, stmt):
   print("Struct error found: ({})\n\tLine: {}\n \
         Left: {}\n\t\t\tField: {}\n".format(errMsg, stmt.get("line"), left.get("id"), fieldId))

def printError(stmt):
   print("Print error found: (Not an int)\n\tLine: {}\n".format(stmt["line"]))

#====================================================================================



def checkReturn(syms, funcs, structs, stmt, func):
   retType = func["return_type"]
   if stmt.get("exp") != None:
      expType = lookupExpType(syms, funcs, structs, stmt["exp"])
   else:
      expType = None

   #print("return type: {}".format(retType))
   #print("expType: {}\n".format(expType))
   #print("expType: {}\n\tFrom Stmt: {}".format(expType, stmt))

   if not checkTypes(retType, expType):
      typeError(stmt)


def checkIf(syms, funcs, structs, stmt, func):
   guardType = lookupExpType(syms, funcs, structs, stmt["guard"])
   if guardType != "bool":
      guardError(stmt)

   #print("Then statement: {}".format(stmt["then"]))
   checkStmt(syms, funcs, structs, stmt["then"], func)
   #print(stmt["then"]) 
   elseStmt = stmt.get("else")
   if elseStmt != None:
      #print(elseStmt)
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
   sourceType = lookupExpType(syms, funcs, structs, stmt["source"])

   if not checkTypes(tarType, sourceType):
      typeError(stmt)


def checkPrint(syms, funcs, structs, stmt, func):
   #TODO
   expType = lookupExpType(syms, funcs, structs, stmt)
   #print(stmt)
   #print(expType)
   if expType != "int":
      printError(stmt)
   return None

def checkWhile(syms, funcs, structs, stmt, func):
   guardType = lookupExpType(syms, funcs, structs, stmt["guard"])

   if guardType != "bool":
      guardError(stmt)

   checkStmt(syms, funcs, structs, stmt["body"], func)



def checkInvocation(syms, funcs, structs, stmt):
   #print(stmt)
   #print("\n")
   if stmt["id"] not in funcs:
      funcError(stmt)
      return

   argStmts = stmt["args"]
   #print(argStmts)
   paramStmts = funcs[stmt["id"]]["parameters"]

   if len(argStmts) != len(paramStmts):
      argCountError(stmt, len(paramStmts), len(argStmts))
      return

   for i in range(len(argStmts)):
      #print(argStmts[i])
      #print("\n")
      argType = lookupExpType(syms, funcs, structs, argStmts[i])
      #print("argType checked")
      paramType = paramStmts[i]["type"]
      
      #print("argType: {}".format(argType))
      #print("paramType: {}".format(paramType))
      if not checkTypes(argType, paramType):
         typeError(stmt)

def checkBinary(syms, funcs, structs, stmt):
   lhsType = lookupExpType(syms, funcs, structs, stmt["lft"])
   rhsType = lookupExpType(syms, funcs, structs, stmt["rht"])
   op = stmt["operator"]
   badTypes = ("bool", "null")

   if not checkTypes(lhsType, rhsType)\
         or lhsType in badTypes\
         or rhsType in badTypes:
      typeError(stmt)


def checkField(structs, structType, fieldId):
   struct = structs.get(structType)
   if struct == None:
      #print(structs)
      #print(structType)
      return "StructNotFound", None
   
   for field in struct["fields"]:
      #if fieldId == field["id"]:
      if fieldId["id"] == field["id"]:
         return "FieldFound", field["type"]

   return "FieldNotFound", None



def checkDot(syms, funcs, structs, stmt):
   #format: exp.fieldId.fieldId...
   exp = stmt
   dotIds = list()

   #Iterate through all dot operator id's used
   #and push them onto a list based stack
   #dotIds.append(exp.get("id"))
   dotIds.append(exp)
   #print(exp["id"])
   while exp["left"]["exp"] == "dot":
      exp = exp["left"]
      #print(exp["id"])
      dotIds.append(exp)
   
   #Push the farthest left exp onto the stack
   #dotIds.append(exp["left"]["id"])
   dotIds.append(exp["left"])
   #print(dotIds)

   #
   #print(dotIds)
   fieldId = dotIds.pop()
   #fieldType = lookupType(syms, fieldId)
   fieldType = lookupExpType(syms, funcs, structs, fieldId)
   #fieldType = None
   #print(fieldId)
   #print(fieldType)
   #print(stmt)
   while dotIds:
      left = fieldId
      fieldId = dotIds.pop()
      errMsg, fieldType = checkField(structs, fieldType, fieldId)
      if errMsg != "FieldFound":
         #print(fieldType)
         structError(left, fieldId["id"], errMsg, stmt)
         return None
   return fieldType

def checkStmt(syms, funcs, structs, stmt, func):
   if stmt["stmt"] == "return":
      checkReturn(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] == "if":
      checkIf(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] == "block":
      checkBlock(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] == "assign":
      checkAssign(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] == "print":
      checkPrint(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] == "while":
      checkWhile(syms, funcs, structs, stmt, func)

   elif stmt["stmt"] == "invocation":
      checkInvocation(syms, funcs, structs, stmt)
      return



#check if two types are equivalent or null
def checkTypes(t1, t2):
   #print("type1: {}".format(ascii(t1)))
   #print("type2: {}".format(ascii(t2)))
   if t1 == t2:
      return True
   if t1 == "null" or t2 == "null":
      return True
   return False
   '''
   if t1 != t2:
      if t1 == "null" or t2 == "null":
         return True
      return False
   return True
   '''

#lookup varID in symTable to find what type it is 
#and if it exists
def lookupType(syms, varID):
   if varID in syms:
      return syms[varID]["type"]
   elif varID in syms["__global__"]:
      return syms["__global__"][varID]["type"]
   return None

#lookup what type an exp equates to
def lookupExpType(syms, funcs, structs, stmt):
   exp = stmt["exp"]

   if exp == "num":
      return "int"

   elif exp == "binary":
      #TODO typeCheck binary expression here
      checkBinary(syms, funcs, structs, stmt)
      op = stmt["operator"]
      if op in ("+", "-", "/", "*", "%"):
         return "int"
      elif op in ("<", ">", "<=", ">="):
         return "bool"

   elif exp == "id":
      return lookupType(syms, stmt["id"])

   elif type(exp) == type(dict()):
      #TODO evaluate whats in the dictionary block
      return lookupExpType(syms, funcs, structs, exp)

   elif exp == "invocation":
      #TODO check func params here
      checkInvocation(syms, funcs, structs, stmt)
      return funcs[stmt["id"]]["return_type"]

   elif exp == "dot":
      #TODO check that field is a part of the lhs var
      #return value is the type of the initial field
      #ie. f.a.a.i type of the field i will be returned
      return checkDot(syms, funcs, structs, stmt)
      

   elif exp == "null":
      return "null"

   elif exp == "true":
      return "bool"

   elif exp == "false":
      return "bool"
   
   elif exp == "new":
      return stmt["id"]

   elif exp == "unary":
      return lookupExpType(syms, funcs, structs, stmt["operand"])
      
