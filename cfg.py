#!/bin/python3


class ProgramCfgs:
   def __init__(self):
      self.types = []
      self.decls = []
      self.funcCfgs = []

   def printProg(self):
      for cfg in self.funcCfgs:
         print(" CFG =======================================")
         cfg.printCfg()
         print("\n\n")


class Cfg:
   def __init__(self, label):
      self.entry = BlockNode(label)
      self.exit = BlockNode(label + 1)

   def printCfg(self):
      self.entry.printBlock()

   
# Every block contains:
#   list of instructions
#   list of successors
#   list of predecessors
#   Label
class BlockNode:
   def __init__(self, label):
      self.instrs = []
      self.succrs = []
      self.preds = []
      self.label = label

   def printBlock(self):
      print("Label "+str(self.label)+"==================")
      print("Instructions:")
      print(self.instrs)
      print("\nLabel "+str(self.label)+" successors:")
      for successor in self.succrs:
         successor.printBlock()
      print("\nLabel "+str(self.label)+" predecessors:")
      for pred in self.preds:
         print("Label "+str(pred.label)+",")
      print()

def buildProg(jsonProg): 
   returnProg = ProgramCfgs()
   labelCount = 0

   returnProg.types = jsonProg["types"]
   returnProg.decls = jsonProg["declarations"]

   for func in jsonProg["functions"]:
      funcCfgAndLabel = createCfg(func, labelCount)
      labelCount = funcCfgAndLabel[1]
      returnProg.funcCfgs.append(funcCfgAndLabel[0])

   return returnProg


def createCfg(func, labelCount):
   returnCfg = Cfg(labelCount)
   returnLabCnt = labelCount + 2
   
   currBlock = returnCfg.entry
   
   returnLabCnt = addBlock(func["body"], returnCfg.entry, returnCfg.exit, 
         returnLabCnt)

   return (returnCfg, returnLabCnt)


def addBlock(body, currBlock, exit, label):
   labelCount = label

   for stmt in body:
      stmtType = stmt["stmt"]
      if stmtType == "return":
         # attach current block to exit node
         currBlock.instrs.append(stmt)
         # ignore code after return statement; break out of loop
         break
      elif stmtType == "if":
         
         # add guard expression to current block
         currBlock.instrs.append(stmt["guard"])

         thenEntry = BlockNode(labelCount)
         thenExit = BlockNode(labelCount + 1)

         # update preds and successors for current block and then entry
         thenEntry.preds.append(currBlock)
         currBlock.succrs.append(thenEntry)
         
         # assess instructions inside Then branch
         labelCount = addBlock([stmt["then"]], thenEntry, thenExit, 
               labelCount + 2)
         
         # create Join Block aka Exit Node for if statement
         joinBlock = BlockNode(labelCount)
         labelCount += 1

         # update preds&succcrs for thenExit and join block
         thenExit.succrs.append(joinBlock)
         joinBlock.preds.append(thenExit)

         if "else" in stmt:
            elseEntry = BlockNode(labelCount)
            elseExit = BlockNode(labelCount + 1)

            # update preds and successors for current block and else entry
            elseEntry.preds.append(currBlock)
            currBlock.succrs.append(elseEntry)
            
            # assess instructions inside Else branch
            labelCount = addBlock([stmt["else"]], elseEntry, elseExit,
                  labelCount + 2)

            # update preds & succrs for else exit and join block
            elseExit.succrs.append(joinBlock)
            joinBlock.preds.append(elseExit)
         else:  # just an if statement with no else
            currBlock.succrs.append(joinBlock)
            joinBlock.preds.append(currBlock)

         # resume adding instructions to the join block on next iteration 
         #    of for loop.
         currBlock = joinBlock
      elif stmtType == "while":
         # add guard expression to current block
         currBlock.instrs.append(stmt["guard"])

         whileBlock = BlockNode(labelCount)
         joinBlock = BlockNode(labelCount + 1)

         # update succrs for current block
         currBlock.succrs.append(whileBlock)
         currBlock.succrs.append(joinBlock)
         whileBlock.preds.append(currBlock)
         #whileBlock.succrs.append(whileBlock)
         #whileBlock.succrs.append(joinBlock)
         labelCount = addBlock(stmt["body"], whileBlock, joinBlock,
               labelCount + 2)
         
         # add guard at end of while block to determine which successor follows
         whileBlock.instrs.append(stmt["guard"])

         # update preds&succrs
         joinBlock.preds.append(currBlock)
         whileBlock.preds.append(whileBlock)

         # first successor of while block will be what follows if the guard
         #   is true. Second successor follows if guard is false.
         #   Therefore, make whileBlock its FIRST successor.
         whileBlock.succrs = [whileBlock] + whileBlock.succrs
     
         # resume adding instructions to the join block on next iteration 
         #    of for loop.
         currBlock = joinBlock
      elif stmtType == "block":
         # add instructions from block statement into the current block
         # also add an exit node for block statement so that shit makes sense
         blockExit = BlockNode(labelCount)
         addBlock(stmt["list"], currBlock, blockExit, labelCount + 1)
         currBlock = blockExit
      else:  # print, assign, invocation
         currBlock.instrs.append(stmt)

   # At this point, all statements in the block were assessed. 
   # Add the exit block to the current block's successors
   currBlock.succrs.append(exit)
   exit.preds.append(currBlock)

   return labelCount


