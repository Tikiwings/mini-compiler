#!/bin/python3


class ProgramCfgs:
   def __init__(self, jsonProg):
      self.types = jsonProg["types"]
      self.decls = jsonProg["declarations"]
      self.funcCfgs = []

   def printProg(self):
      for cfg in self.funcCfgs:
         print("CFG for function \""+cfg.funcName+"\" " + "=" * 25)
         cfg.printCfg()
         print("\n\n")


class Cfg:
   def __init__(self, label, func):
      self.entry = BlockNode(label, "CFGEntry")
      self.exit = BlockNode(label + 1, "CFGExit")
      self.params = func["parameters"]
      self.localDecls = func["declarations"]
      self.funcName = func["id"]
      self.returnType = func["return_type"]


   def removeDeadBlocks(self):
      # Create list of reachable block labels
      reachableLabels = self.entry.getReachableBlocks([])
      
      self.entry.removeDeadPreds(reachableLabels, [])


   def printCfg(self):
      self.entry.printBlock(1, [])

   
# Every block contains:
#   list of instructions
#   list of successors
#   list of predecessors
#   Label
class BlockNode:
   def __init__(self, label, blockType):
      self.instrs = []
      self.succrs = []
      self.preds = []
      self.label = label
      self.blockType = blockType
      self.visited = False


   # Returns a list of reachable blocks including the block itself and its
   # successors.
   def getReachableBlocks(self, visitedLabels):
      # Prevent visiting blocks more than once
      if self.label in visitedLabels:
         return []
      visitedLabels.append(self.label)

      retList = [self.label]

      # Add reachable blocks of successors into current block's reachables
      for succr in self.succrs:
         retList += succr.getReachableBlocks(visitedLabels)

      return retList


   # Removes the unreachable predecessors
   def removeDeadPreds(self, reachableLabels, visitedBlocks):
      # Prevent visiting blocks more than once
      if self.label in visitedBlocks:
         return
      visitedBlocks.append(self.label)

      # Remove dead predecessors of current block
      predIndex = 0
      while predIndex < len(self.preds):
         if self.preds[predIndex].label not in reachableLabels:
            del self.preds[predIndex]
         else:
            predIndex += 1

      # Remove dead predecessors of the successors
      for succr in self.succrs:
         succr.removeDeadPreds(reachableLabels, visitedBlocks)


   def printBlock(self, indentDepth, visitedLabels):
      # Prevent visiting blocks more than once
      if self.label in visitedLabels:
         return
      visitedLabels.append(self.label)

      printIndent(indentDepth)
      print("Label " + str(self.label) + " " + str(self.blockType)+"="*10)
      
      # Instructions
      printIndent(indentDepth+1)
      print("Instructions:")
      printIndent(indentDepth+1)
      print(self.instrs)
      
      # Succrs
      printIndent(indentDepth+1)
      print("Successors:")
      if len(self.succrs) == 0:
         printIndent(indentDepth+2)
         print("None")
      else:
         for succr in self.succrs:
            printIndent(indentDepth+2)
            print("Label " + str(succr.label)+" "+str(succr.blockType)+",")

      # Predecessors
      printIndent(indentDepth+1)
      print("Predecessors:")
      if len(self.preds) == 0:
         printIndent(indentDepth+2)
         print("None")
      else:
         for pred in self.preds:
            printIndent(indentDepth+2)
            print("Label " + str(pred.label)+" "+str(pred.blockType)+",")
      
      # Print successor blocks
      printIndent(indentDepth+1)
      print("Successors to Block " + str(self.label))
      for successor in self.succrs:
         successor.printBlock(indentDepth + 2, visitedLabels)
      printIndent(indentDepth+1)
      print("End of Successors to Block " + str(self.label))
      print()


def buildProg(jsonProg): 
   returnProg = ProgramCfgs(jsonProg)
   labelCount = 0

   for func in jsonProg["functions"]:
      funcCfgAndLabel = createCfg(func, labelCount)
      labelCount = funcCfgAndLabel[1]
      funcCfgAndLabel[0].removeDeadBlocks()
      returnProg.funcCfgs.append(funcCfgAndLabel[0])

   return returnProg


def createCfg(func, labelCount):
   returnCfg = Cfg(labelCount, func)
   returnLabCnt = labelCount + 2
   
   currBlock = returnCfg.entry
   
   returnLabCnt = addBlock(func["body"], returnCfg.entry, returnCfg.exit,
                           returnCfg.exit, returnLabCnt)

   return (returnCfg, returnLabCnt)


def addBlock(body, currBlock, exit, cfgExit, label):
   labelCount = label

   for stmt in body:
      stmtType = stmt["stmt"]
      if stmtType == "return":
         currBlock.instrs.append(stmt)
         
         # Attach current block to exit node
         currBlock.succrs.append(cfgExit)
         cfgExit.preds.append(currBlock)

         # ignore code after return statement
         return labelCount
      elif stmtType == "if":
         
         # add guard expression to current block
         currBlock.instrs.append({"guard" : stmt["guard"]})

         thenEntry = BlockNode(labelCount, "ThenEntry")
         thenExit = BlockNode(labelCount + 1, "ThenExit")

         # update preds and successors for current block and then entry
         thenEntry.preds.append(currBlock)
         currBlock.succrs.append(thenEntry)
         
         # assess instructions inside Then branch
         labelCount = addBlock([stmt["then"]], thenEntry, thenExit, cfgExit,
               labelCount + 2)
         
         # create Join Block aka Exit Node for if statement
         joinBlock = BlockNode(labelCount, "IfElseJoin")
         labelCount += 1

         # update preds&succcrs for thenExit and join block
         thenExit.succrs.append(joinBlock)
         joinBlock.preds.append(thenExit)

         if "else" in stmt:
            elseEntry = BlockNode(labelCount, "ElseEntry")
            elseExit = BlockNode(labelCount + 1, "ElseExit")

            # update preds and successors for current block and else entry
            elseEntry.preds.append(currBlock)
            currBlock.succrs.append(elseEntry)
            
            # assess instructions inside Else branch
            labelCount = addBlock([stmt["else"]], elseEntry, elseExit, cfgExit,
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
         currBlock.instrs.append({"guard" : stmt["guard"]})

         whileBlock = BlockNode(labelCount, "While")
         joinBlock = BlockNode(labelCount + 1, "WhileJoin")

         # update succrs for current block
         currBlock.succrs.append(whileBlock)
         currBlock.succrs.append(joinBlock)
         whileBlock.preds.append(currBlock)
         #whileBlock.succrs.append(whileBlock)
         #whileBlock.succrs.append(joinBlock)
         labelCount = addBlock([stmt["body"]], whileBlock, joinBlock, cfgExit,
               labelCount + 2)
         
         # add guard at end of while block to determine which successor follows
         whileBlock.instrs.append({"guard" : stmt["guard"]})

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
         #TODO: If llvm translation has errors with block labels, refer to this
         # add instructions from block statement into the current block
         # also add an exit node for block statement so that shit makes sense
         blockExit = BlockNode(labelCount, "BlockStmtExit")
         addBlock(stmt["list"], currBlock, blockExit, cfgExit, labelCount + 1)
         currBlock = blockExit
      else:  # print, assign, invocation
         currBlock.instrs.append(stmt)

   # At this point, all statements in the block were assessed. 
   # Add the exit block to the current block's successors
   currBlock.succrs.append(exit)
   exit.preds.append(currBlock)

   return labelCount


def printIndent(indentDepth):
   print("|  " * (indentDepth - 1), end = "")
