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
        if command not in ["neg", "not"]:
            self.file.write("@SP\nM=M-1\nA=M\nD=M\n") # pop the stack value to D
        self.moveSP(False) # SP--
        self.file.write('@SP\nA=M\n') # set A register to the SP value
        
        # if not a bool operator
        if command not in ["eq", "gt", "lt"]:
            self.file.write(ARITHMETIC[command[0]])
        else:
            # compare the two
            self.file.write("D=M-D")
            self.file.write(ARITHMETIC[command[0]])

        # SP++
        self.moveSP(True)

    def writeInit(self):
        # set stack pointer to 256
        self.file.write('@256\nD=A\n')
        self.file.write('@SP\nM=D\n')

        # call sys.init
        self.writeCall("Sys.init", 0)

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

        res = "\n".join(assembly) + '\n\n'
        self.file.write(res)

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

        res = "\n".join(assembly) + '\n\n'
        self.file.write(res)

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

    def combine(self, assembly: list):
        pass

    def writeLabel(self, label):
        self.file.write(f"({label})")

    def writeGoto(self, label):
        self.file.write(f"@{label}\n0;JMP\n")

    def writeIf(self, label):
        self.file.write()

    def writeCall(self, functionName: str, numArgs: int):
        pass
    
    def writeReturn(self, ):
        pass

    def writeFunction(self, functionName: str, numLocals: int):
        pass
    
    def close(self):
        self.file.close()

"""
################### Main Implementation ########################
push:
RAM[SPpointer] = val
SP++

    1)
    ######### push to the sp #########
    @num
    D=A

    2)
    (
    # get the num in the pointer
    @LCL
    A=D+M
    D=M
    )

    3)
    @SP
    M=D

    4)
    move SP up
    
pop:
SP--
val = RAM[SPpointer]

    1)
    SP--

    2)
    # get the value from SP and save it to R13
    @SP
    A=M
    D=M

    @R13
    M=D

    3)
    # get the address of LCL + num and save it R14
    @num
    D=A

    @LCL
    A=D+M
    D=A
    
    @R14
    M=D

    4)
    # get the r13 value
    @R13
    D=M

    5)
    # save the r13 value to the address
    @R14
    A=M
    M=D




arith:
    pop operation at the current stack
    pop operation at the current stack
    push pop1 (sth:arith) pop2
"""