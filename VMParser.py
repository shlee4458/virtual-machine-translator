class VMParser:
    def __init__(self, filename) -> None:
        '''
        Opens the input file/stream and gets ready to parse it
        '''
        self.file = open(filename)
        self.prevPosition = self.file.tell()
        self.currPosition = -1
        self.command = [] # initiated while advancing

    def hasMoreCommands(self):
        '''
        Check if there are more commands in the input.
        return bool
        '''
        return self.prevPosition != self.currPosition
    
    def advance(self):
        '''
        Reads the next command from the input and makes it the current
        command. Should be called only if hasMoreCommands() is true.
        Initially there is no current command.
        '''
        if self.hasMoreCommands():
            line = self.file.readline()
            # assign curr command position to the previous position
            if self.currPosition != -1:
                self.prevPosition = self.currPosition

            # assign the new command position to the current position
            self.currPosition = self.file.tell()
            
            # update the currentCommand
            currCommand = line.strip()
            
            # if comment is in the currentCommand remove the string after '/'
            if '//' in currCommand:
                currCommand = currCommand.split('//')[0].strip()

            # load the list that contains command and arguments to the self.command
            self.command = currCommand.lower().split()

    def commandType(self):
        '''
        Returns a constant representing the type of the current command.
        If the current is an arithmetic-logical command, returns C_ARITHMETIC.
        '''
        # if it is an empty line
        if not self.command:
            return ""
        
        if len(self.command) == 1:
            return "C_ARITHMETIC"
    
        if self.command[0] == 'push':
            return "C_PUSH"
    
        if self.command[0] == 'pop':
            return "C_POP"

        # TODO:
            # C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL,

    def arg1(self):
        '''
        Returns the first argument of the current command.
        In case of the C_ARTHMETIC, the command itself is returned.
        Should not be called if the current command is C_RETURN
        '''
        if len(self.command) <= 1:
            return self.command
        return self.command[1]

    def arg2(self):
        '''
        Returns the first argument of the current command.
        In case of the C_ARTHMETIC, the command itself is returned.
        Should be called only if the current command is;
            C_PUSH, C_POP, C_FUNCTION, or C_CALL
        '''
        if len(self.command) <= 1:
            return self.command
        return self.command[2]
    
    def getCommand(self):
        return self.command