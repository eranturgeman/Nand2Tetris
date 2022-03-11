"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


A_COMMAND = "A_COMMAND"
L_COMMAND = "L_COMMAND"
C_COMMAND = "C_COMMAND"
COMMENT ="//"
RIGHT_SHIFT = ">>"
LEFT_SHIFT = "<<"



class Parser:
    """Encapsulates access to the input code. Reads and assembly language
    command, parses it, and provides convenient access to the commands
    components (fields and symbols). In addition, removes all white space and
    comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        input_lines = input_file.read().splitlines() # getting an array of the file lines

        self.lines = input_lines
        self.__next_valid_command = None
        self.cur_command = None
        self.__command_ind = 0


    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        # None check
        # if next_valid == None -> set runner to 0
        # if next_valid != None && next_valid < len(lines) -> runner++ and keep check from there
        # if next_valid == len(lines) -> return False

        if self.__next_valid_command == len(self.lines): #TODO check if comparison is correct
            return False

        if self.__next_valid_command is None:
            runner = 0
        else:
            runner = self.__next_valid_command + 1

        while runner < len(self.lines):
            if _isValidCommand(self.lines[runner]):
                self.__next_valid_command = runner
                return True
            runner += 1

        self.__next_valid_command = runner
        return False


    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        Also cleans the next valid command if exists
        """
        self.cur_command = cleanCommand(self.lines[self.__next_valid_command])
        self.__command_ind = 0


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """

        if self.cur_command[0] == "@":
            return A_COMMAND
        elif self.cur_command[0] == "(":
            return L_COMMAND
        else:
            return C_COMMAND


    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or
            "L_COMMAND".
        """
        if self.command_type() == A_COMMAND:
            return self.cur_command[1:]
        if self.command_type() == L_COMMAND:
            return self.cur_command[1:-1]
        else:
            raise TypeError("The symbol func is not valid for C_COMMANDS") #TODO check if needed


    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        des = ""
        if self.command_type() != C_COMMAND:
            raise TypeError("The symbol func is not valid for C_COMMANDS") #TODO check if needed

        for ch in self.cur_command:
            if ch == "=":
                return des
            des += ch
            self.__command_ind += 1
        self.__command_ind = 0
        return ""


    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        comp = ""
        if self.__command_ind != len(self.cur_command) and self.cur_command[self.__command_ind] == "=":
            self.__command_ind += 1

        if self.command_type() != C_COMMAND:
            raise TypeError("The symbol func is not valid for C_COMMANDS") #TODO check if needed
        for ch in self.cur_command[self.__command_ind:]:
            self.__command_ind += 1
            if ch == ";":
                break
            comp += ch
        return comp


    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called
            only when commandType() is "C_COMMAND".
        """
        if self.__command_ind == len(self.cur_command):
            return ""
        return self.cur_command[self.__command_ind:]

    def is_shift(self) -> bool:
        if RIGHT_SHIFT in self.cur_command or LEFT_SHIFT in self.cur_command:
            return True
        return False


def _isValidCommand(command:str) ->bool:
    """
    checks if the given command is valid: not empty, not a whitespace line and not a comment
    """
    if command.isspace() or command == "" or command[0:2] == COMMENT:
        return False
    return True

def cleanCommand(command:str) -> str:
    """
    Filters a given command from spaces, comments after the command
    """
    comment_idx = command.find("//")
    if comment_idx != -1:
        command = command[:comment_idx]
    return command.replace(" ", "")
