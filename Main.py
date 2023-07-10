#!/usr/bin/env python
'''
This is the main entrance to the VirtualMachine Program.
VirtualMachine program produces machine code from the VM commands
'''

import os
import argparse
from VMParser import *
from CodeWriter import *

DEBUG_MODE = True
class Main:
    def __init__(self):
        # parse arguments and get the list of file names
        self.parseArgs()
        self.writeFiles()

    def parseArgs(self):
        # parse filename as an argument
        argParser = argparse.ArgumentParser(description = "Process a file or a directory")
        argParser.add_argument('name', type=str, help="Path to the file or directory")
        args = argParser.parse_args()
        path = args.name

        # create a list of filenames
        if ".vm" in path: # if it is a filename
            files = path
        else:
            files = [os.path.join(path, filename) for filename in os.listdir(path) if ".vm" in filename]

        # initiate files and writer
        self.writer = CodeWriter(path)
        self.files = files

    def writeFiles(self):
        for file in self.files:
            parser = VMParser(file) # load the file to the AssymblyParser

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
                    self.writer.writeArithmetic(command)
                
                elif parser.commandType() in ["C_PUSH", "C_POP"]:
                    self.writer.writePushPop(command)
                elif parser.commandType() in ["C_GOTO", "C_IF", "C_LABEL"]:
                    self.writer.writeBranch(command)
                elif parser.commandType() in ["C_RETURN", "C_CALL", "C_FUNCTION"]:
                    self.writer.writeFunc(command)

if __name__ == "__main__":
    Main()