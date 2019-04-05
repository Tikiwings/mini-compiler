#!/bin/python3
import json
import sys

def main():
   with open(sys.argv[1], "r") as f:
      progFile = json.load(f)
   print(json.dumps(progFile, indent=4))

main()
