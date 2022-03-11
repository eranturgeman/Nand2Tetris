"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

COMMENT ="//"


class Parser:
    """
    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient 
    access to their components. 
    In addition, it removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.__lines = input_file.read().splitlines()
        self.__cur_command = None
        self.__next_valid_command = None #command index (int)


    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        if self.__next_valid_command == len(self.__lines):
            return False

        if self.__next_valid_command is None:
            runner = 0
        else:
            runner = self.__next_valid_command + 1

        while runner < len(self.__lines):
            if is_valid_command(self.__lines[runner]):
                self.__next_valid_command = runner
                return True
            runner += 1

        self.__next_valid_command = runner
        return False


    def advance(self) -> None:
        """Reads the next command from the input and makes it the current 
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        self.__cur_command = clean_command(self.__lines[self.__next_valid_command])

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        if self.__cur_command.startswith("push"):
            return "C_PUSH"
        elif self.__cur_command.startswith("pop"):
            return "C_POP"
        elif self.__cur_command.startswith("label"):
            return "C_LABEL"
        elif self.__cur_command.startswith("goto"):
            return "C_GOTO"
        elif self.__cur_command.startswith("if-goto"):
            return "C_IF"
        elif self.__cur_command.startswith("function"):
            return "C_FUNCTION"
        elif self.__cur_command.startswith("return"):
            return "C_RETURN"
        elif self.__cur_command.startswith("call"):
            return "C_CALL"
        else:
            return "C_ARITHMETIC"


    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of 
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned. 
            Should not be called if the current command is "C_RETURN".
        """
        command_type = self.command_type()
        if command_type == "C_RETURN":
            return "" # not really needed
        if command_type == "C_ARITHMETIC": # returns the command itself
            return self.__cur_command
        else:
            return self.__cur_command.split(" ")[1]
            # "C_PUSH" or "C_POP":  returns the segment
            # "C_LABEL": returns the label
            # "C_GOTO": returns the label to go to
            # "C_IF": returns the label to go to
            # "C_FUNCTION": returns function name
            # "C_CALL": returns function name


    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP", 
            "C_FUNCTION" or "C_CALL".
        """
        return int(self.__cur_command.split(" ")[2])
        # C_PUSH, C_POP return index in a segment
        # C_CALL returns number of arguments
        # C_FUNCTION returns number of local variables


def is_valid_command(command: str) -> bool:
    """
    checks if the given command is valid: not empty, not a whitespace line and not a comment
    """
    if command.isspace() or command == "" or command[0:2] == COMMENT:
        return False
    return True

def clean_command(command:str) -> str:
    """
    Filters a given command from spaces, comments after the command
    """
    comment_idx = command.find(COMMENT)
    if comment_idx != -1:
        command = command[:comment_idx]
    return command.strip()
