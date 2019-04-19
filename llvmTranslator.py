#!/bin/python3

"""
Arithmetic:
   <result> = add <ty> <op1>, <op2>
   <result> = mul <ty> <op1>, <op2>
   <result> = sdiv <ty> <op1>, <op2>
   <result> = sub <ty> <op1>, <op2>

Boolean:
   <result> = and <ty> <op1>, <op2>
   <result> = or <ty> <op1>, <op2>
   <result> = xor <ty> <op1>, <op2>

Comparison and Branching:
   <result> = icmp <cond> <ty> <op1>, <op2> ; <cond> ie.  eq
   br i1 <cond>, label <ifTrue>, label <ifFalse>
   br label <dest>

Load and Stores:
   <result> = load <ty>* <pointer>
   store <ty> <value>, <ty>* <pointer>
   <result> getelementptr <ty>* <ptrval>, i1 0, i32 <index>

Invocation:
   <result> = call <ty> <fnptrval>(<function args>)
   ret void
   ret <ty> <value>

Allocation:
   <result> = alloca <ty>

Misc:
   <result> = bitcast <ty> <value> to <ty2>     ;cast type
   <result> = trunc <ty> <value> to <ty2>       ;truncate to ty2
   <result> = zext <ty> <value> to <ty2>        ;zero extend to ty2
   <result> = phi <ty> [<value 0>, <label 0>] [<value 1> <label 1>] ...

<ty>
   iN - integer with N bits
   void
   null - null pointer constant, must be of 'pointer type'
   boolean - 'true' and 'false' are constants of type 'i1'
   imm - integers can be used as constants / immediate values

<cond>
   eq - equal
   ne - not equal
   ugt - unsigned greater than
   uge - unsigned greater than or equal
   ult - unsigned less than
   ult - unsigned less than or equal
   sgt - signed greater than
   sge - signed greater than or equal
   slt - signed less than
   sle - signed less than or equal

<result>
   register to store returned result

<op>
   imm - #
   register - %<regName>
   *void
   *null

"""


def transArith():
   return ""
def transBool():
   return ""
def transCmp():
   return ""
def transBr():
   return ""
def transLoad():
   return ""
def transStore():
   return ""
def transInvoc():
   return ""
def transAlloc():
   return ""
def transMisc():
   return ""


def lookUpInstType(instr):
   #if arithmetic:
   #elif boolean:
   #elif comparison and branching
   #elif load and stores
   #elif invocation
   #elif allocation
   #elif misc


def translateInstr():
   #instrType = lookupInstrType(instr)

   #if instrType == "arithmetic":
   #elif instrType == "boolean":
   #elif instrType == "comparison":
   #elif instrType == "branching":
   #elif instrType == "load":
   #elif instrType == "store":
   #elif instrType == "invocation":
   #elif instrType == "allocation":
   #elif instrType == "misc":
   #else:
      #ERROR instrType doesn't exist
   return None
