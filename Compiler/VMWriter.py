"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

OPS_COMMANDS = {"+": "add", "-": "sub", "=": "eq", "<": "lt", ">": "gt", "&": "and", "|": "or",
                "/": "call Math.divide 2", "*": "call Math.multiply 2"}

UNARY_COMMANDS = {"-": "neg", "^": "shiftleft", "#": "shiftright", "~": "not"}

PUSH_POP_SEGMENTS_DICT = {"field": "this", "var": "local"}


class VMWriter:
    """
    Writes VM commands into a file. Encapsulates the VM command syntax.
    """

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Creates a new file and prepares it for writing VM commands."""
        self.output = output_stream

    def write_push(self, segment: str, index: int) -> None:
        """Writes a VM push command.

        Args:
            segment (str): the segment to push to, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP"
            index (int): the index to push to.
        """
        if segment in PUSH_POP_SEGMENTS_DICT:
            self.output.write(f"push {PUSH_POP_SEGMENTS_DICT[segment]} {index}\n")
        else:
            if segment == "arg":
                segment = "argument"
            self.output.write(f"push {segment} {index}\n")

    def write_pop(self, segment: str, index: int) -> None:
        """Writes a VM pop command.

        Args:
            segment (str): the segment to pop from, can be "CONST", "ARG", 
            "LOCAL", "STATIC", "THIS", "THAT", "POINTER", "TEMP".
            index (int): the index to pop from.
        """
        if segment in PUSH_POP_SEGMENTS_DICT:
            self.output.write(f"pop {PUSH_POP_SEGMENTS_DICT[segment]} {index}\n")
        else:
            if segment == "arg":
                segment = "argument"
            self.output.write(f"pop {segment} {index}\n")

    def write_arithmetic(self, command: str) -> None:
        """Writes a VM arithmetic command.

        Args:
            command (str): the command to write, can be "ADD", "SUB",
            "EQ", "GT", "LT", "AND", "OR".
        """
        self.output.write(f"{OPS_COMMANDS[command]}\n")

    def write_unary(self, command: str) -> None:
        """Writes a VM unary operation.

        Args:
            command (str): the command to write, can be "LEFT_SHIFT", "RIGHT_SHIFT", "NEG", "NOT".
        """
        self.output.write(f"{UNARY_COMMANDS[command]}\n")

    def write_label(self, label: str) -> None:
        """Writes a VM label command.

        Args:
            label (str): the label to write.
        """
        self.output.write(f"label {label}\n")

    def write_goto(self, label: str) -> None:
        """Writes a VM goto command.

        Args:
            label (str): the label to go to.
        """
        self.output.write(f"goto {label}\n")

    def write_if(self, label: str) -> None:
        """Writes a VM if-goto command.

        Args:
            label (str): the label to go to.
        """
        self.output.write(f"if-goto {label}\n")

    def write_call(self, name: str, n_args: int) -> None:
        """Writes a VM call command.

        Args:
            name (str): the name of the function to call.
            n_args (int): the number of arguments the function receives.
        """
        self.output.write(f"call {name} {n_args}\n")

    def write_function(self, name: str, n_locals: int) -> None:
        """Writes a VM function command.

        Args:
            name (str): the name of the function.
            n_locals (int): the number of local variables the function uses.
        """
        self.output.write(f"function {name} {n_locals}\n")

    def write_return(self) -> None:
        """Writes a VM return command."""
        self.output.write("return\n")
