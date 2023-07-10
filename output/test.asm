@256
D=A
@SP
M=D
@1
D=M
@LCL
A=D+M
D=M
@SP
A=M
M=D
@SP
M=M+1

@2
D=A
@5
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1

@3
D=A
@SP
A=M
M=D
@SP
M=M+1

@3
D=M
@LCL
A=D+M
D=M
@R13
M=D
@SP
AM=M-1
D=M
@R13
A=M
M=D

