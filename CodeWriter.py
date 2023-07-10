"""
################### Main Command types ########################
command type 1: push/pop
    constant: store at the current sp, pop from the previous sp
    local: store at LCL + i, pop from the previous sp 
    static: store at 16 + i, pop from the previous sp
    temp: store at 5 + i, pop from the previous sp 
        5 to 12
    pointer: 
        this: push/pop pointer 0 = push/pop pointer THIS
        that: push/pop pointer 1 = push/pop pointer THAT 

command type 2: Arithmetic/Logical
    add, sub neg
    eq, gt, lt
    and, or, not

"""

import os

# neg and not takes single value -> pop a single time
ARITHMETIC = {"add": "M=M+D", "sub": "M=M-D", "neg": "M=-M",\
              "eq": "D;JEQ", "gt": "D;JGT", "lt": "D;JLT",\
                "and": "M=M&D", "or": "M=M|D", "not": "M=!M"}

REGISTER_MAPPING = {"constant": "SP", "argument" : "ARG", "local": "LCL",\
                    "pointer": ["THIS", "THAT"], "temp": "5"}

class CodeWriter:
    def __init__(self, path: str) -> None:
        # initiate file to write on
        destPath = self.processPath(path)
        self.file = open(destPath, "w")
        self.fcount = 0

        # write the bootstrap asm at the start of the translation
        self.writeInit()

    def processPath(self, path):
        # process input path and returns the destination path
        destPathName = path.split('/')[-1].split('.')[0]
        self.destPathName = destPathName + ".asm"
        destPath = os.path.join(os.getcwd(), "output", self.destPathName)
        return destPath

    def writeArithmetic(self, command):
        # get the value at the top of the stack to the D register
        assembly = []
        if command not in ["neg", "not"]:
            assembly += self.stack_to_d()
        assembly += ['@SP', 'A=M'] # set A register to the SP value
        
        # if not a bool operator
        if command not in ["eq", "gt", "lt"]:
            assembly += str(ARITHMETIC[command[0]])
        else:
            # compare the two
            assembly += self.stack_to_d()
            assembly += ['@SP', 'AM=M-1', 'D=D-M'] # subtract to the previous stack
            assembly += [f'@BOOL{self.fcount}', str(ARITHMETIC[command[0]]), 'D=0'] # if true set D to -1 else 0
            assembly += [f'@FINAL{self.fcount}', '0;JEQ']
            assembly += [f'(EQUAL{self.fcount})', 'D=-1']
            assembly += [f'(FINAL{self.fcount})', '@SP', 'A=M', 'M=D']
            self.fcount += 1

        assembly += self.stackPlus() # SP++
        self.combineAndWrite(assembly)            

    def writeInit(self):
        assembly = []
        # set stack pointer to 256
        assembly += ['@256', 'D=A', '@SP', 'M=D']
        self.combineAndWrite(assembly)

        # call sys.init
        self.writeCall(["call", "Sys.init", "0"])


    ##### write push pop #####
    def writePushPop(self, command):
        '''
        writePush and writePop handler
        '''

        # set the variables from the command
        cType, arg1, arg2 = command

        if cType == "push":
            self.writePush(arg1, arg2)
        
        elif cType == "pop":
            self.writePop(arg1, arg2)

    def writePush(self, arg1, arg2):
        '''
        Write push command given arg1 and arg2 to the file.
        '''
        assembly = []

        # update the offset for pointer and static
        if arg1 == "pointer":
            arg2 = "THIS" if not arg2 else "THAT"

        if arg1 == 'static':
            arg2 = f"{self.destPathName}.{arg2}"

        # 1) get the value from the specified memory
        assembly += self.from_addr_to_d(arg1, arg2)

        # 2) store that in the current SP
        assembly += self.d_to_stack()

        # 3) move the pointer up
        assembly += self.stackPlus()

        self.combineAndWrite(assembly)

    def writePop(self, arg1, arg2):
        '''
        Write pop command given arg1 and arg2 to the file.
        '''
        assembly = []

        # 1) get the adress to store the arg2 to, and store the address to R13
        if arg1 not in ['pointer', 'static']:
            assembly += self.from_addr_to_d(arg1, arg2)
            assembly += ['@R13', 'M=D']

        # 2) get the stack value to D and move the SP--
        assembly += self.stack_to_d()

        # 3) store value in d to m at the target address
        assembly += self.d_to_m(arg1, arg2)

        self.combineAndWrite(assembly)

    def d_to_stack(self):
        return ["@SP", "A=M", "M=D"]
    
    def stack_to_d(self):
        return ["@SP", 'AM=M-1', 'D=M']

    def d_to_m(self, arg1, arg2):
        res = []
        if arg1 == "pointer":
            res += [f'@{arg2}']
        elif arg1 == 'static':
            res += [f'@{self.destPathName}.{arg2}']
        else:
            res += ['@R13', 'A=M']

        res += ['M=D']
        return res

    def from_addr_to_d(self, arg1, arg2):
        '''
        Get the value stored in the address(optionally, address + offset) to D register
        arg1: address
        arg2: offset
        '''
        
        A_or_M = "A" if arg1 in ["constant", "temp"] else "M"
        res = [f"@{arg2}", f"D={A_or_M}"]
        if arg1 in ['pointer', 'static', 'constant']:
            return res
        
        # use value stored in A or M as an offset and retrieve value from the arg1
            # temp(A) or the rest(M)
        res.extend([f'@{REGISTER_MAPPING[arg1]}', f'A=D+{A_or_M}', 'D=M'])
        return res

    def stackPlus(self):
        return ["@SP", "M=M+1"]

    def combineAndWrite(self, assembly: list):
        res = "\n".join(assembly) + '\n\n'
        self.file.write(res)

    ##### write branch #####
    def writeBranch(self, command):
        # if-goto label, goto label, label
        if command[0] == "if-goto":
            self.writeIf(command)
        elif command[0] == 'goto':
            self.writeGoto(command)
        else:
            self.writeLabel(command)
        
    def writeLabel(self, command):
        assembly = []

        if len(command) > 2:
            label, name = command[1], command[2]
            assembly += [f"({name}${label})"]
        else:
            label = command[1]
            assembly += [f"({label})"]
        
        self.combineAndWrite(assembly)

    def writeGoto(self, command):
        label = command[1]
        assembly = [f"@{label}", "0;JMP"]
        self.combineAndWrite(assembly)

    def writeIf(self, command):
        assembly = []

        # get the stack to D
        assembly += self.stack_to_d()

        if len(command) >= 2:
            label, name = command[1], command[2]
            assembly += [f"@{name}${label}"]
        else:
            assembly += [f"@{label}"]

        self.combineAndWrite(assembly)

    ##### write function #####
    def writeFunc(self, command):
        if command[0] == 'call':
            self.writeCall(command)
        elif command[0] == 'return':
            self.writeReturn()
        else:
            self.writeFunction(command)

    def writeCall(self, command):
        name, numLocals = command[1], command[2]
        assembly = []

        # push return address, LCL, ARG, THIS, THAT in order
        for addr in [f'@{name}$ret.{self.fcount}', "@LCL", "@ARG", "THIS", "THAT"]:
            assembly += [addr, "D=A"]
            assembly += self.d_to_stack()
            assembly += self.stackPlus()

        # set ARG
        assembly += ['D=M', f'@{numLocals}', 'D=D-A',"@ARG","M=D"]

        # get set LCL to SP
        assembly += ['@SP', 'D=M', '@LCL', 'M=D']

        # go to the function
        assembly += [f"@{name}", "0;JMP"]

        # write lable; return address
        assembly += [f'({name}$ret.{self.fcount})']

        self.combineAndWrite(assembly)
        self.fcount += 1
    
    def writeReturn(self):
        assembly = []

        # get the end of the previous frame
        assembly += ['@LCL', 'D=M', '@frame', 'M=D']

        # get the return address
        assembly += ['@5', 'D=D-A', 'A=D', 'D=M', '@return', 'M=D']

        # set the arg as the return value
        self.stack_to_d()
        assembly += ['@ARG', 'A=M', 'M=D']

        # set the stack pointer to the arg + 1
        assembly += ['@ARG', 'D=M+1', '@SP', 'M=D']

        # retrieve the previous addr from the stack
        for offset, addr in zip([1,2,3,4], ['THAT','THIS','ARG', 'LCL']):
            assembly += ['@frame', 'D=M', f'@{offset}', 'D=D-A', 'A=D', 'D=M', f'@{addr}', 'M=D']

        # return to the address
        assembly += ['@return', 'A=M', '0;JMP']


    def writeFunction(self, command):
        numLocals = int(command[-1])
        assembly = []

        # put 0 to num of locals
        for _ in range(numLocals):
            assembly += ["@0", "D=A"] # load 0 to D
            assembly += self.d_to_stack() # set d to stack
            assembly += self.stackPlus() # move stack up

        self.combineAndWrite(assembly)

    def close(self):
        self.file.close()