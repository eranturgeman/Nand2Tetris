"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from SymbolTable import SymbolTable
from Parser import Parser
from Code import Code

A_COMMAND = "A_COMMAND"
L_COMMAND = "L_COMMAND"
C_COMMAND = "C_COMMAND"
RAM_STARTING_SECOND_PASS = 16


def assemble_file(input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Assembles a single file.

    Args:
        input_file (typing.TextIO): the file to assemble.
        output_file (typing.TextIO): writes all output to this file.
    """
    if not input_file or not output_file:
        return

    sym_table = firstPass(input_file)
    secondPass(input_file, output_file, sym_table)
    input_file.close()
    output_file.close()


def firstPass(input_file: typing.TextIO) -> SymbolTable:
    """
    creates a SymbolTable with all predefined symbols and adds all LABLES
    also during the process creates an array of the input file lines filtered and cleaned for
    proceeding stages
    Returns:
        table:SymbolTable
    """
    par = Parser(input_file)
    table = SymbolTable()

    rom_address = 0
    while par.has_more_commands():
        par.advance()
        if par.command_type() == L_COMMAND:
            table.add_entry(par.symbol(), rom_address)
        else:
            rom_address += 1
    return table


def secondPass(input_file: typing.TextIO, output_file: typing.TextIO, table: SymbolTable) -> None:
    input_file.seek(0)
    par = Parser(input_file)
    ram_address = RAM_STARTING_SECOND_PASS
    translator = Code()

    while par.has_more_commands():
        par.advance()
        if par.command_type() == A_COMMAND and not par.cur_command[1:].isdigit():
            symbol = par.symbol()
            if symbol not in table.table.keys():
                table.add_entry(symbol, ram_address)
                ram_address += 1
            binary_rep = translator.toBinary(table.get_address(symbol))
            # val_to_bin = table.get_address(symbol)
        elif par.command_type() == A_COMMAND and par.cur_command[1:].isdigit():
            binary_rep = translator.toBinary(int(par.cur_command[1:]))
            # val_to_bin = int(par.cur_command[1:])
        elif par.command_type() == C_COMMAND:
            dest, comp, jump = par.dest(), par.comp(), par.jump()
            if par.is_shift():
                binary_rep = "101" + translator.comp(comp) + translator.dest(dest) + translator.jump(jump)
            else:
                binary_rep = "111" + translator.comp(comp) + translator.dest(dest) + translator.jump(jump)
        else:
            continue
        output_file.write(binary_rep + "\n")


if "__main__" == __name__:
    # Parses the input path and calls assemble_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: Assembler <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".asm":
            continue
        output_path = filename + ".hack"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            assemble_file(input_file, output_file)
