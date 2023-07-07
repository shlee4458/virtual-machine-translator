'''
This is the main entrance to the VirtualMachine Program.
VirtualMachine program produces machine code from the VM commands
'''

import argparse
from VMParser import *

def main():

    # parse filename as an argument
    argParser = argparse.ArgumentParser(description = "Process a file")
    argParser.add_argument('filename', type=str, help="Path to the file")
    args = argParser.parse_args()
    filename = args.filename

    # Load the file to the AssymblyParser
    parser = VMParser(filename)

    while parser.hasMoreCommands():
        parser.advance()
        print(f"arg1:{parser.arg1()}, arg2: {parser.arg2()}")


if __name__ == "__main__":
    main()