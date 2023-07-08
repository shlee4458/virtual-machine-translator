#!/usr/bin/env python
'''
This is the main entrance to the VirtualMachine Program.
VirtualMachine program produces machine code from the VM commands
'''

import argparse
from VMParser import *
from CodeWriter import *

DEBUG_MODE = True

def main():

    # parse filename as an argument
    argParser = argparse.ArgumentParser(description = "Process a file")
    argParser.add_argument('filename', type=str, help="Path to the file")
    args = argParser.parse_args()
    filename = args.filename

    parser = VMParser(filename) # load the file to the AssymblyParser
    writer = CodeWriter(filename) # initiate the writer

    while parser.hasMoreCommands():

        # get the next command
        parser.advance()
        command = parser.getCommand()

        if DEBUG_MODE:
            print(f"Current command is: {command}")

        # skip empty line or comment
        if not command:
            continue

        # call respective function to write in the output file
        if parser.commandType() == "C_ARITHMETIC":
            print()
            writer.writeArithmetic(command)
        
        elif parser.commandType() == "C_PUSH" or parser.commandType() == "C_POP":
            writer.writePushPop(command)

if __name__ == "__main__":
    main()