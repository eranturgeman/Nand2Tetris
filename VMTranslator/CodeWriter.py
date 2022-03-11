"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

ADD = "add"
SUB = "sub"
NEG = "neg"
EQ = "eq"
GT = "gt"
LT = "lt"
AND = "and"
OR = "or"
NOT = "not"
SHIFT_L = "shiftleft"
SHIFT_R = "shiftright"

SEGMENTS = {"local": "LCL", "argument": "ARG", "this": "THIS", "that": "THAT"}
POINTERS = {0: "THIS", 1: "THAT"}
STATIC = "static"
CONSTANT = "constant"
POINTER = "pointer"
TEMP = "temp"

STATIC_START = 16
TEMP_START = 5

TRUE = "-1"
FALSE = "0"

TAB = "    "
NL = "\n"

SEGMENTS_TO_RESTORE = {1: "THAT", 2:"THIS", 3:"ARG", 4:"LCL"}


class CodeWriter:
    """Translates VM commands into Hack assembly code."""

    EQ = 0
    GT = 1
    LT = 2
    INIT_FUNC = "Sys.init"

    def __init__(self, output_stream: typing.TextIO) -> None:
        """Initializes the CodeWriter.

        Args:
            output_stream (typing.TextIO): output stream.
        """
        self.output = output_stream
        self.__compare_index = [0, 0, 0]  # [EQ, GT, LT]
        self.__cur_file_name = None
        self.__cur_func = ""
        self.__functions_returns = dict()

    def set_file_name(self, filename: str) -> None:
        """Informs the code writer that the translation of a new VM file is
        started.

        Args:
            filename (str): The name of the VM file.
        """
        self.__cur_file_name = filename

    def write_init(self):
        """
        initializes the .asm file with the initial commands (calling sys.init) and sets the stack
        """
        self.output.write("// initializing stack & calling Sys.init" + NL +
                          "@256" + NL +
                          "D=A" + NL +
                          "@SP" + NL +
                          "M=D" + NL)
        self.__call("", CodeWriter.INIT_FUNC, 0)


    def write_arithmetic(self, command: str) -> None:
        """Writes the assembly code that is the translation of the given
        arithmetic command.

        Args:
            command (str): an arithmetic command.
        """
        if command == ADD:
            self.__add(command)
        if command == SUB:
            self.__sub(command)
        if command == NEG:
            self.__neg(command)
        if command == EQ:
            self.__eq(command)
        if command == GT:
            self.__gt(command)
        if command == LT:
            self.__lt(command)
        if command == AND:
            self.__and(command)
        if command == OR:
            self.__or(command)
        if command == NOT:
            self.__not(command)
        if command == SHIFT_L:
            self.__shift_left(command)
        if command == SHIFT_R:
            self.__shift_right(command)


    def write_push_pop(self, command: str, segment: str, index: int) -> None:
        """Writes the assembly code that is the translation of the given
        command, where command is either C_PUSH or C_POP.

        Args:
            command (str): "C_PUSH" or "C_POP".
            segment (str): the memory segment to operate on.
            index (int): the index in the memory segment.
        """
        if command == "C_PUSH":
            self.__push("push", segment, index)
        else:
            self.__pop("pop", segment, index)


    def write_branching(self, command:str, label:str):
        label = f"{self.__cur_func}${label}"
        if command == "C_GOTO":
            self.__goto("goto", label)
        elif command == "C_IF":
            self.__if_goto("if-goto", label)
        else:
            self.__label("label", label)


    def write_functions(self, command:str, func_name:str, n:int):
        """
        calls the __write_function or __write__call commands
        @command commant type
        @func_name function name
        @n number of args or vars, according to the given command type
        """
        if command == "C_FUNCTION":
            self.__function("function", func_name, n)
        else:
            self.__call("call", func_name, n)


    def write_return(self, command:str):
        self.__return("return")

#========================================= functions implementations ==========================================

    def __add(self, command: str):
        """
        translates 'add' command from VM to ASM
        """
        self.output.write(f"// {command}" + NL)
        self.output.write("@SP" + NL +
                          "AM=M-1" + NL +
                          "D=M" + NL +
                          "A=A-1" + NL +
                          "M=M+D" + NL)


    def __sub(self, command: str):
        """
        translates 'sub' command from VM to ASM
        """
        self.output.write(f"// {command}" + NL)
        self.output.write("@SP" + NL +
                          "AM=M-1" + NL +
                          "D=M" + NL +
                          "A=A-1" + NL +
                          "M=M-D" + NL)


    def __neg(self, command: str):
        """
        translates 'neg' command from VM to ASM
        """
        self.output.write(f"// {command}" + NL)
        self.output.write("@SP" + NL +
                          "A=M-1" + NL +
                          "M=-M" + NL)


    def __eq(self, command: str):
        """
        initialize a jump to the 'eq' command written at the end of the asm file, and saves a label to return to al R13
        """
        self.output.write(f"// {command}" + NL)
        self.__compare_index[CodeWriter.EQ] += 1
        self.output.write(f"@EQ{self.__compare_index[CodeWriter.EQ]}" +
                          f"    // EQ{self.__compare_index[CodeWriter.EQ]}" + NL +
                          "D=A" + NL +
                          "@R13" + NL +
                          "M=D" + NL +
                          "@EQ" + NL +
                          "0;JMP" + NL +
                          f"(EQ{self.__compare_index[CodeWriter.EQ]})" +
                          f"    // EQ{self.__compare_index[CodeWriter.EQ]} label" + NL)


    def __gt(self, command):
        """
        initialize a jump to the 'gt' command written at the end of the asm file, and saves a label to return to al R13
        """
        self.output.write(f"// {command}" + NL)
        self.__compare_index[CodeWriter.GT] += 1
        self.output.write(f"@GT{self.__compare_index[CodeWriter.GT]}" +
                          f"    // GT{self.__compare_index[CodeWriter.GT]}" + NL +
                          "D=A" + NL +
                          "@R13" + NL +
                          "M=D" + NL +
                          "@GT" + NL +
                          "0;JMP" + NL +
                          f"(GT{self.__compare_index[CodeWriter.GT]})" +
                          f"    // GT{self.__compare_index[CodeWriter.GT]} label" + NL)


    def __lt(self, command):
        """
        initialize a jump to the 'lt' command written at the end of the asm file, and saves a label to return to al R13
        """
        self.output.write(f"// {command}" + NL)
        self.__compare_index[CodeWriter.LT] += 1
        self.output.write(f"@LT{self.__compare_index[CodeWriter.LT]}" +
                          f"    // LT{self.__compare_index[CodeWriter.LT]}" + NL +
                          "D=A" + NL +
                          "@R13" + NL +
                          "M=D" + NL +
                          "@LT" + NL +
                          "0;JMP" + NL +
                          f"(LT{self.__compare_index[CodeWriter.LT]})" +
                          f"    // LT{self.__compare_index[CodeWriter.LT]} label" + NL)


    def __and(self, command):
        """
        translates 'and' command from VM to ASM
        """
        self.output.write(f"// {command}" + NL)
        self.output.write("@SP" + NL +
                          "AM=M-1" + NL +
                          "D=M" + NL +
                          "A=A-1" + NL +
                          "M=D&M" + NL)


    def __or(self, command):
        """
        translates 'or' command from VM to ASM
        """
        self.output.write(f"// {command}" + NL)
        self.output.write("@SP" + NL +
                          "AM=M-1" + NL +
                          "D=M" + NL +
                          "A=A-1" + NL +
                          "M=D|M" + NL)


    def __not(self, command):
        """
        translates 'not' command from VM to ASM
        """
        self.output.write(f"// {command}" + NL)
        self.output.write("@SP" + NL +
                          "A=M-1" + NL +
                          "M=!M" + NL)


    def __shift_left(self, command):
        """
        translates 'shiftleft' command from VM to ASM
        """
        self.output.write(f"// {command}" + NL)
        self.output.write("@SP" + NL +
                          "A=M-1" + NL +
                          "M=M<<" + NL)


    def __shift_right(self, command):
        """
        translates 'shiftright' command from VM to ASM
        """
        self.output.write(f"// {command}" + NL)
        self.output.write("@SP" + NL +
                          "A=M-1" + NL +
                          "M=M>>" + NL)


    def __push(self, command, segment, index):
        """
        translates 'push' command from VM to ASM according to the given segment and given index
        """
        self.output.write(f"// {command} {segment} {index}" + NL)

        if segment == CONSTANT:
            self.output.write(f"@{index}" + NL +
                              "D=A" + NL +
                              "@SP" + NL +
                              "A=M" + NL +
                              "M=D" + NL +
                              "@SP" + NL +
                              "M=M+1" + NL)

        elif segment in SEGMENTS:
            self.output.write(f"@{SEGMENTS[segment]}" + NL +
                              "D=M" + NL +
                              f"@{index}" + NL +
                              "A=D+A" + NL +
                              "D=M" + NL +
                              "@SP" + NL +
                              "A=M" + NL +
                              "M=D" + NL +
                              "@SP" + NL +
                              "M=M+1" + NL)

        elif segment == TEMP:
            self.output.write(f"@{TEMP_START + index}" + NL +
                              "D=M" + NL +
                              "@SP" + NL +
                              "A=M" + NL +
                              "M=D" + NL +
                              "@SP" + NL +
                              "M=M+1" + NL)

        elif segment == POINTER:
            self.output.write(f"@{POINTERS[index]}" + NL +
                              "D=M" + NL +
                              "@SP" + NL +
                              "M=M+1" + NL +
                              "A=M-1" + NL +
                              "M=D" + NL)

        elif segment == STATIC:
            self.output.write(f"@{self.__cur_file_name}.{index}" + NL +
                              "D=M" + NL +
                              "@SP" + NL +
                              "M=M+1" + NL +
                              "A=M-1" + NL +
                              "M=D" + NL)


    def __pop(self, command, segment, index):
        """
        translates 'pop' command from VM to ASM according to the given segment and given index
        """
        self.output.write(f"// {command} {segment} {index}" + NL)
        if segment in SEGMENTS:
            self.output.write(f"@{SEGMENTS[segment]}" + NL +
                              "D=M" + NL +
                              f"@{index}" + NL +
                              "D=D+A" + NL +
                              "@R13" + NL +
                              "M=D" + NL +
                              "@SP" + NL +
                              "AM=M-1" + NL +
                              "D=M" + NL +
                              "@R13" + NL +
                              "A=M" + NL +
                              "M=D" + NL)

        elif segment == TEMP:
            self.output.write(f"@{TEMP_START}" + NL +
                              "D=A" + NL +
                              f"@{index}" + NL +
                              "D=D+A" + NL +
                              "@R13" + NL +
                              "M=D" + NL +
                              "@SP" + NL +
                              "AM=M-1" + NL +
                              "D=M" + NL +
                              "@R13" + NL +
                              "A=M" + NL +
                              "M=D" + NL)

        elif segment == POINTER:
            self.output.write("@SP" + NL +
                              "AM=M-1" + NL +
                              "D=M" + NL +
                              f"@{POINTERS[index]}" + NL +
                              "M=D" + NL)

        elif segment == STATIC:
            self.output.write("@SP" + NL +
                              "AM=M-1" + NL +
                              "D=M" + NL +
                              f"@{self.__cur_file_name}.{index}" + NL +
                              "M=D" + NL)


    def __goto(self, command:str, label: str):
        """
        writes goto command
        @label label to go to
        """
        self.output.write(f"// {command} {label}" + NL)
        self.output.write(f"@{label}" + NL +
                          "0;JMP" + NL)


    def __if_goto(self, command:str, label:str):
        """
        writes if-goto command
        @label label to go to
        """
        self.output.write(f"// {command} {label}" + NL)
        self.output.write("@SP" + NL +
                          "AM=M-1" + NL +
                          "D=M" + NL +
                          f"@{label}" + NL +
                          "D;JNE" + NL)


    def __label(self, command:str, label:str):
        """
        writes label command
        @label label to go to
        """
        self.output.write(f"// {command} {label}" + NL)
        self.output.write(f"({label})" + NL)


    def __function(self, command, function_name, num_local_vars):
        """
        write function command
        @command command type
        @function_name function name
        @num_local_vars number of local args to push
        """
        self.__cur_func = function_name
        self.output.write(f"// {command} {function_name} {num_local_vars}" + NL)
        self.output.write(f"({function_name})" + NL)
        for i in range(num_local_vars):
            self.__push("push", "constant", 0)


    def __call(self, command, function_name, num_args):
        """
        write function command
        @command command type
        @function_name function name
        @num_local_vars number of args to push
        """
        if function_name not in self.__functions_returns:
            self.__functions_returns[function_name] = 0
        else:
            self.__functions_returns[function_name] += 1

        self.output.write(f"// {command} {function_name} {num_args}" + NL)
        self.output.write(f"@{function_name}$ret.{self.__functions_returns[function_name]}" + NL +
                          "D=A" + NL +
                          "@SP" + NL +
                          "M=M+1" + NL +
                          "A=M-1" + NL +
                          "M=D" + NL)

        segments_to_setup = ["LCL", "ARG", "THIS", "THAT"]

        for segment in segments_to_setup:
            self.output.write("@" + segment + NL +
                              "D=M" + NL +
                              "@SP" + NL +
                              "M=M+1" + NL +
                              "A=M-1" + NL +
                              "M=D" + NL)

        self.output.write("@SP" + NL +
                          "D=M" + NL +
                          "@5" + NL +
                          "D=D-A" + NL +
                          f"@{num_args}" + NL +
                          "D=D-A" + NL +
                          "@ARG" + NL +
                          "M=D" + NL)   #up to here- setting ARG to SP-5-num_args

        self.output.write("@SP" + NL +
                          "D=M" + NL +
                          "@LCL" + NL +
                          "M=D" + NL)    #up to here- setting LCL to SP

        self.__goto("goto", function_name)
        self.output.write(f"({function_name}$ret.{self.__functions_returns[function_name]})")


    def __return(self, command):
        """
        write return function
        @command command type
        """
        self.output.write(f"// {command}" + NL)

        self.output.write("@LCL" + NL +
                          "D=M" + NL +
                          "@R14" + NL +
                          "M=D" + NL +          # endFrame(R14) = LCL
                          "@5" + NL +
                          "D=A" + NL +
                          "@R14" + NL +
                          "A=M-D" + NL +
                          "D=M" + NL +
                          "@R15" + NL +
                          "M=D" + NL)           # retAddr(R15) = *(endFrame - 5)

        self.__pop("pop", "argument", 0)        # putting the return value kept at the top of the stack to ARG[0]

        self.output.write("@ARG" + NL +
                          "D=M+1" + NL +
                          "@SP" + NL +
                          "M=D" + NL)           # SP=ARG + 1

        self.output.write("@R14" + NL +
                          "A=M-1" + NL +
                          "D=M" + NL +
                          "@THAT" + NL +
                          "M=D" + NL)           # THAT = *(endFrame - 1)

        self.output.write("@R14" + NL +
                          "D=M" + NL +
                          "@2" + NL +
                          "A=D-A" + NL +
                          "D=M" + NL +
                          "@THIS" + NL +
                          "M=D" + NL)           # THIS = *(endFrame - 2)

        self.output.write("@R14" + NL +
                          "D=M" + NL +
                          "@3" + NL +
                          "A=D-A" + NL +
                          "D=M" + NL +
                          "@ARG" + NL +
                          "M=D" + NL)           # ARG = *(endFrame - 3)

        self.output.write("@R14" + NL +
                          "D=M" + NL +
                          "@4" + NL +
                          "A=D-A" + NL +
                          "D=M" + NL +
                          "@LCL" + NL +
                          "M=D" + NL)           # LCL = *(endFrame - 4)

        self.output.write("@R15" + NL +
                          "A=M" + NL +
                          "0;JMP" + NL)         # jump to the return address


    def __write_general_eq(self):
        """
        writes the general 'eq' command to be jumped to from __eq
        """
        self.output.write(NL + "// GENERAL EQ" + NL)
        self.output.write("@END" + NL +
                          "0;JMP" + NL + NL +
                          "(EQ)" + NL +
                          TAB + "@32767" + NL +
                          TAB + "D=!A" + NL +
                          TAB + "@R14" + NL +
                          TAB + "M=D" + NL +
                          TAB + "@R15" + NL +
                          TAB + "M=D" + NL +
                          TAB + "@SP" + NL +
                          TAB + "AM=M-1" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@R14" + NL +
                          TAB + "M=D&M" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M-1" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@R15" + NL +
                          TAB + "M=D&M" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@R14" + NL +
                          TAB + "D=D-M" + NL +
                          TAB + "@NOT_EQ" + NL +
                          TAB + "D;JNE" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M" + NL +
                          TAB + "D=M" + NL +
                          TAB + "A=A-1" + NL +
                          TAB + "D=D-M" + NL +
                          TAB + "@EQUAL" + NL +
                          TAB + "D;JEQ" + NL + NL +
                          "(NOT_EQ)" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M-1" + NL +
                          TAB + f"M={FALSE}" + NL +
                          TAB + "@R13" + NL +
                          TAB + "A=M" + NL +
                          TAB + "0;JMP" + NL + NL +
                          "(EQUAL)" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M-1" + NL +
                          TAB + f"M={TRUE}" + NL +
                          TAB + "@R13" + NL +
                          TAB + "A=M" + NL +
                          TAB + "0;JMP" + NL)


    def __write_general_gt(self):
        """
        writes the general 'gt' command to be jumped to from __gt
        """
        self.output.write(NL + "// GENERAL GT" + NL)
        self.output.write("@END" + NL +
                          "0;JMP" + NL + NL +
                          "(GT)" + NL +
                          TAB + "@32767" + NL +
                          TAB + "D=!A" + NL +
                          TAB + "@R14" + NL +
                          TAB + "M=D" + NL +
                          TAB + "@R15" + NL +
                          TAB + "M=D" + NL +
                          TAB + "@SP" + NL +
                          TAB + "AM=M-1" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@R14" + NL +
                          TAB + "M=D&M" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M-1" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@R15" + NL +
                          TAB + "M=D&M" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@R14" + NL +
                          TAB + "D=D-M" + NL +
                          TAB + "@GT_DIFF_SIGN" + NL +
                          TAB + "D;JNE" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M" + NL +
                          TAB + "D=M" + NL +
                          TAB + "A=A-1" + NL +
                          TAB + "D=D-M" + NL +
                          TAB + "@GT_GREATER_THAN" + NL +
                          TAB + "D;JLT" + NL +
                          TAB + "@GT_LESSER_THAN" + NL +
                          TAB + "0;JMP" + NL + NL +
                          "(GT_DIFF_SIGN)" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@GT_LESSER_THAN" + NL +
                          TAB + "D;JGE" + NL +
                          TAB + "@GT_GREATER_THAN" + NL +
                          TAB + "0;JMP" + NL + NL +
                          "(GT_LESSER_THAN)" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M-1" + NL +
                          TAB + f"M={FALSE}" + NL +
                          TAB + "@R13" + NL +
                          TAB + "A=M" + NL +
                          TAB + "0;JMP" + NL + NL +
                          "(GT_GREATER_THAN)" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M-1" + NL +
                          TAB + f"M={TRUE}" + NL +
                          TAB + "@R13" + NL +
                          TAB + "A=M" + NL +
                          TAB + "0;JMP" + NL)


    def __write_general_lt(self):
        """
        writes the general 'lt' command to be jumped to from __lt
        """
        self.output.write(NL + "// GENERAL LT" + NL)
        self.output.write("@END" + NL +
                          "0;JMP" + NL + NL +
                          "(LT)" + NL +
                          TAB + "@32767" + NL +
                          TAB + "D=!A" + NL +
                          TAB + "@R14" + NL +
                          TAB + "M=D" + NL +
                          TAB + "@R15" + NL +
                          TAB + "M=D" + NL +
                          TAB + "@SP" + NL +
                          TAB + "AM=M-1" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@R14" + NL +
                          TAB + "M=D&M" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M-1" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@R15" + NL +
                          TAB + "M=D&M" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@R14" + NL +
                          TAB + "D=D-M" + NL +
                          TAB + "@LT_DIFF_SIGN" + NL +
                          TAB + "D;JNE" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M" + NL +
                          TAB + "D=M" + NL +
                          TAB + "A=A-1" + NL +
                          TAB + "D=D-M" + NL +
                          TAB + "@LT_GREATER_THAN" + NL +
                          TAB + "D;JLE" + NL +
                          TAB + "@LT_LESSER_THAN" + NL +
                          TAB + "0;JMP" + NL + NL +
                          "(LT_DIFF_SIGN)" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M" + NL +
                          TAB + "D=M" + NL +
                          TAB + "@LT_LESSER_THAN" + NL +
                          TAB + "D;JGE" + NL +
                          TAB + "@LT_GREATER_THAN" + NL +
                          TAB + "0;JMP" + NL + NL +
                          "(LT_LESSER_THAN)" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M-1" + NL +
                          TAB + f"M={TRUE}" + NL +
                          TAB + "@R13" + NL +
                          TAB + "A=M" + NL +
                          TAB + "0;JMP" + NL + NL +
                          "(LT_GREATER_THAN)" + NL +
                          TAB + "@SP" + NL +
                          TAB + "A=M-1" + NL +
                          TAB + f"M={FALSE}" + NL +
                          TAB + "@R13" + NL +
                          TAB + "A=M" + NL +
                          TAB + "0;JMP" + NL)


    def fill_missing_functions(self):
        """
        adding all missing functions that we want to jump to at the end of the file.
        adding only those among: eq, gt, lt that we actually used
        """
        used_comparison = False
        if self.__compare_index[CodeWriter.EQ]:
            used_comparison = True
            self.__write_general_eq()
        if self.__compare_index[CodeWriter.GT]:
            used_comparison = True
            self.__write_general_gt()
        if self.__compare_index[CodeWriter.LT]:
            used_comparison = True
            self.__write_general_lt()
        if used_comparison:
            self.output.write("(END)" + NL)

