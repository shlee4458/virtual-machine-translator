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

ARITHMETIC = {"add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"}
REGISTER_MAPPING = {"constant": "SP", "argument" : "ARG", "local": "LCL",\
                    "pointer": ["THIS", "THAT"]}

class CodeWriter:
    def __init__(self, filename: str) -> None:
        # initiate file to write on
        destFileName = filename.split('/')[-1].split('.')[0]
        destFileName = destFileName + ".asm" # TODO: change extension
        destPath = os.path.join(os.getcwd(), "test", destFileName)
        self.file = open(destPath, "w")

    def writeArithmetic(self, command):
        # pop two and execute the arithmetic operation
        # TODO
        pass

    def writePushPop(self, command):
        '''
        writePush and writePop handler
        '''

        # set the variables from the command
        cType, arg1, arg2 = command

        if arg1 == "pointer":
            arg1, arg2 = REGISTER_MAPPING[arg1][arg2], 0

        if cType == "push":
            self.writePush(arg1, arg2)
        
        elif cType == "pop":
            self.writePop(arg1, arg2)

    def writePush(self, arg1, arg2):
        '''
        Write pop command given arg1 and arg2 to the file.
        '''

        # store the arg2 to the D register
        self.file.write(f"@{arg2}\nD=A\n")

        if arg1 != "constant":
            base = REGISTER_MAPPING[arg1] # get the base pointer for the arg1
            self.file.write(f"@{base}\nA=D+M\nD=M\n")

        # store in the current sp
        self.file.write("@SP\nM=D\n")
    
        # move the sp up
        self.moveSP(True)
        self.file.write("\n")

    def writePop(self, arg1, arg2):
        '''
        Write pop command given arg1 and arg2 to the file.
        '''

        # move the sp down
        self.moveSP(False)

        # get the value from sp and save it to the R13
        self.file.write(f"@SP\nA=M\nD=M\n")
        self.file.write(f"@R13\nM=D\n")

        # get the address of the pointer to store the value at, and store it to R14
        base = REGISTER_MAPPING[arg1]

        self.file.write(f"@{arg2}\nD=A\n")
        self.file.write(f"{base}\nA=D+M\nD=A\n")
        self.file.write(f"@R14\nM=D\n")

        # retrieve R13 value
        self.file.write("@R13\nD=M\n")

        # save R13 value to the address
        self.file.write("@R14\nA=M\nM=D\n")
        self.file.write("\n")

    def moveSP(self, add):
        '''
        Writes to the file to move stack pointer
        add bool: true if move the pointer forward(add), else false
        '''
        direction = "+1" if add else "-1"
        self.file.write(f"@SP\nM=M{direction}\n")


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