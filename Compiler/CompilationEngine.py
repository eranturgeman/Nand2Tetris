"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter

TAB = "  "
OPS = {"+", "-", "*", "/", "&", "|", ">", "<", "="}

FUNCTIONS_DEC = {"function", "method", "constructor"}

UNARY_OP = {"-", "~", "^", "#"}

WHILE_ENTER_LABEL = "WHILE_EXP"
WHILE_EXIT_LABEL = "WHILE_END"
IF_LABEL = "IF_TRUE"
ELSE_LABEL = "IF_FALSE"
IF_END_LABEL = "IF_END"

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream:VMWriter, symbol_table:SymbolTable, file_name:str) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.fileName = file_name
        self.tokenizer = input_stream
        self.writer = output_stream
        self.symbolTable = symbol_table
        self.className = ""
        self.whileCount = 0
        self.ifCount = 0

    def compile_class(self) -> None:
        """Compiles a complete class."""
        if self.tokenizer.has_more_tokens():
            self.validate_and_advance("class")
            self.className = self.tokenizer.get_cur_token()
            self.next_token()
            self.validate_and_advance("{")

            while self.tokenizer.get_cur_token() not in FUNCTIONS_DEC:
                self.compile_class_var_dec()

            while self.tokenizer.get_cur_token() in FUNCTIONS_DEC:
                self.symbolTable.start_subroutine()
                self.ifCount = 0
                self.whileCount = 0
                self.compile_subroutine()

            self.validate_and_advance("}")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        kind = self.tokenizer.get_cur_token() # field | static
        self.next_token()
        tokenType = self.tokenizer.get_cur_token() # primitive | classes
        self.next_token()
        name = self.tokenizer.get_cur_token() # identifier - var name
        self.next_token()
        self.symbolTable.define(name, tokenType, kind)

        while self.tokenizer.get_cur_token() != ";":
            self.validate_and_advance(",")
            self.symbolTable.define(self.tokenizer.get_cur_token(), tokenType, kind)
            self.next_token()

        self.validate_and_advance(";")

    def compile_subroutine(self) -> None:
        """Compiles a complete method, function, or constructor."""
        functionType = self.tokenizer.get_cur_token() # constructor | method | function
        self.next_token()
        self.next_token() # advance over the return type
        functionName = self.tokenizer.get_cur_token()
        self.next_token()

        self.validate_and_advance("(")
        self.compile_parameter_list(functionType)
        self.validate_and_advance(")")

        self.compile_subroutineBody(functionName, functionType)

    def compile_subroutineBody(self, functionName:str, functionType:str) -> None:
        """compiles a subroutine"""
        self.validate_and_advance("{")
        while self.tokenizer.get_cur_token() == "var":
            self.compile_var_dec()

        self.writer.write_function(f"{self.className}.{functionName}", self.symbolTable.var_count("var"))
        if functionType == "constructor":
            # allocating memory for the new object and set pointer 0 to it
            fieldsNumber = self.symbolTable.var_count("field")
            self.writer.write_push("constant", fieldsNumber)
            self.writer.write_call("Memory.alloc", 1)
            self.writer.write_pop("pointer", 0)
        elif functionType == "method":
            # pushes 'this' as first arg to the stack
            self.writer.write_push("argument", 0)
            self.writer.write_pop("pointer", 0)

        self.compile_statements()
        self.validate_and_advance("}")

    def compile_parameter_list(self, functionType:str) -> None:
        """Compiles a (possibly empty) parameter list, not including the
        enclosing "()".
        """
        if functionType == "method":
            self.symbolTable.define("this", self.className, "arg")

        if self.tokenizer.get_cur_token() != ")":
            argType = self.tokenizer.get_cur_token()
            self.next_token()
            argName = self.tokenizer.get_cur_token()
            self.next_token()
            self.symbolTable.define(argName, argType, "arg")

            while self.tokenizer.get_cur_token() == ",":
                self.validate_and_advance(",")
                argType = self.tokenizer.get_cur_token()
                self.next_token()
                argName = self.tokenizer.get_cur_token()
                self.next_token()
                self.symbolTable.define(argName, argType, "arg")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.validate_and_advance("var")
        varType = self.tokenizer.get_cur_token()
        self.next_token()
        varName = self.tokenizer.get_cur_token()
        self.next_token()
        self.symbolTable.define(varName, varType, "var")

        while self.tokenizer.get_cur_token() != ";":
            self.validate_and_advance(",")
            varName = self.tokenizer.get_cur_token()
            self.next_token()
            self.symbolTable.define(varName, varType, "var")

        self.validate_and_advance(";")

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        while self.tokenizer.get_cur_token() != "}":
            self.compile_statement()

    def compile_statement(self) -> None:
        """
        compile single statement
        """
        if self.tokenizer.get_cur_token() == "do":
            self.compile_do()
            return
        elif self.tokenizer.get_cur_token() == "return":
            self.compile_return()
            return
        elif self.tokenizer.get_cur_token() == "let":
            self.compile_let()
            return
        elif self.tokenizer.get_cur_token() == "while":
            self.compile_while()
            return
        elif self.tokenizer.get_cur_token() == "if":
            self.compile_if()
            return

    def compile_do(self) -> None:
        """Compiles a do statement."""

        self.validate_and_advance("do")
        self.compile_subroutineCall()
        self.validate_and_advance(";")
        self.writer.write_pop("temp", 0)

    def compile_subroutineCall(self, name=""):
        """
        compiles a single case of subroutineCall
        """

        if name:
            calleeName = name
        else:
            calleeName = self.tokenizer.get_cur_token()
            self.next_token()

        argsNumber = 0

        if self.tokenizer.get_cur_token() == ".":
            self.validate_and_advance(".")
            kind = self.symbolTable.kind_of(calleeName)  # checks if we call method on object
            if kind:
                # if indeed we call method on object
                self.writer.write_push(kind, self.symbolTable.index_of(calleeName))
                calleeName = f"{self.symbolTable.type_of(calleeName)}.{self.tokenizer.get_cur_token()}"
                argsNumber += 1
            else:
                # we call a function from out call with prefix or function from another class
                calleeName = f"{calleeName}.{self.tokenizer.get_cur_token()}"

            self.next_token()
        else:
            # if working on the current object
            argsNumber += 1
            self.writer.write_push("pointer", 0)
            calleeName = f"{self.className}.{calleeName}"

        self.validate_and_advance("(")
        argsNumber += self.compile_expression_list()
        self.validate_and_advance(")")
        self.writer.write_call(calleeName, argsNumber)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.validate_and_advance("let")

        varName = self.tokenizer.get_cur_token()
        self.next_token()

        arrayFlag = False
        if self.tokenizer.get_cur_token() == "[":
            self.compile_array(varName, False)
            arrayFlag = True

        self.validate_and_advance("=")

        self.compile_expression()

        if arrayFlag:
            self.writer.write_pop("temp", 0)
            self.writer.write_pop("pointer", 1)
            self.writer.write_push("temp", 0)
            self.writer.write_pop("that", 0)
        else:
            self.writer.write_pop(self.symbolTable.kind_of(varName), self.symbolTable.index_of(varName))

        self.validate_and_advance(";")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        curCount = self.whileCount
        self.whileCount += 1
        self.validate_and_advance("while")
        self.writer.write_label(f"{WHILE_ENTER_LABEL}{curCount}")
        self.validate_and_advance("(")
        self.compile_expression()
        self.validate_and_advance(")")
        self.writer.write_unary("~")
        self.writer.write_if(f"{WHILE_EXIT_LABEL}{curCount}")

        self.validate_and_advance("{")
        self.compile_statements()
        self.validate_and_advance("}")
        self.writer.write_goto(f"{WHILE_ENTER_LABEL}{curCount}")
        self.writer.write_label(f"{WHILE_EXIT_LABEL}{curCount}")

    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.validate_and_advance("return")
        if self.tokenizer.get_cur_token() == ";":
            self.writer.write_push("constant", 0)
            self.writer.write_return()
            self.validate_and_advance(";")
        else:
            self.compile_expression()
            self.writer.write_return()
            self.validate_and_advance(";")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        curCounter = self.ifCount
        self.ifCount += 1
        self.validate_and_advance("if")
        self.validate_and_advance("(")
        self.compile_expression()
        self.validate_and_advance(")")
        self.writer.write_if(f"{IF_LABEL}{curCounter}")
        self.writer.write_goto(f"{ELSE_LABEL}{curCounter}")
        self.writer.write_label(f"{IF_LABEL}{curCounter}")
        self.validate_and_advance("{")
        self.compile_statements()
        self.validate_and_advance("}")

        if self.tokenizer.get_cur_token() == "else":
            self.writer.write_goto(f"{IF_END_LABEL}{curCounter}")
            self.validate_and_advance("else")
            self.writer.write_label(f"{ELSE_LABEL}{curCounter}")
            self.validate_and_advance("{")
            self.compile_statements()
            self.validate_and_advance("}")
            self.writer.write_label(f"{IF_END_LABEL}{curCounter}")
        else:
            self.writer.write_label(f"{ELSE_LABEL}{curCounter}")

    def compile_expression(self, arrayFlag=True) -> None:
        """Compiles an expression."""
        if self.tokenizer.get_cur_token() == "(":
            self.validate_and_advance("(")
            self.compile_expression(arrayFlag)
            self.validate_and_advance(")")
        else:
            self.compile_term()

        while self.tokenizer.get_cur_token() in OPS:
            curOp = self.tokenizer.get_cur_token()
            self.next_token()

            if self.tokenizer.get_cur_token() == "(":
                self.validate_and_advance("(")
                self.compile_expression()
                self.validate_and_advance(")")
            else:
                self.compile_term()

            self.writer.write_arithmetic(curOp)

    def compile_term(self, arrayFlag=True) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        tokenType = self.tokenizer.token_type()

        if tokenType == "integerConstant":
            self.writer.write_push("constant", self.tokenizer.get_cur_token())
            self.next_token()
        elif tokenType == "stringConstant":
            self.compile_string()
            self.next_token()
        elif tokenType == "keyword":
            # true | false | null | this
            curToken = self.tokenizer.get_cur_token()
            if curToken == "true":
                self.writer.write_push("constant", 0)
                self.writer.write_unary("~")
                self.next_token()
            elif curToken == "false" or curToken == "null":
                self.writer.write_push("constant", 0)
                self.next_token()
            elif curToken == "this":
                self.writer.write_push("pointer", 0)
                self.next_token()
            else:
                raise TypeError(f"incorrect type of keywordConstant in line {self.tokenizer.get_cur_line_index()}")
        elif tokenType == "symbol":
            # unaryOp expression
            # (unaryOp expression)
            # (expression)
            curToken = self.tokenizer.get_cur_token()
            if curToken in UNARY_OP:
                unaryOp = curToken
                self.next_token()
                self.compile_expression()
                self.writer.write_unary(unaryOp)
            elif curToken == "(":
                self.validate_and_advance("(")
                self.compile_expression()
                self.validate_and_advance(")")
            else:
                raise TypeError(f"incorrect type of symbol received ({curToken}) in line {self.tokenizer.get_cur_line_index()}")

        else:  # identifier
            # subroutineCall: funcName(expressionList) | className.funcName(ExpressionList) |  varName.funcName(expressionList)
            # varName
            # varName[expression]

            name = self.tokenizer.get_cur_token()
            if self.symbolTable.kind_of(name): # in symbol table (it's a var)
                self.next_token()
                if self.tokenizer.get_cur_token() == ".":  # varName.funcName(expressionList)
                    self.compile_subroutineCall(name)
                elif self.tokenizer.get_cur_token() == "[":
                    # varName[expression]
                    self.compile_array(name)
                    if arrayFlag:
                        self.writer.write_pop("pointer", 1)
                        self.writer.write_push("that", 0)

                else:
                    self.writer.write_push(self.symbolTable.kind_of(name), self.symbolTable.index_of(name))
            else:
                self.compile_subroutineCall()

    def compile_expression_list(self) -> int:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        counter = 0

        if self.tokenizer.get_cur_token() != ")":
            self.compile_expression()
            counter += 1
            while self.tokenizer.get_cur_token() == ",":
                self.validate_and_advance(",")
                self.compile_expression()
                counter += 1
        return counter

    def compile_string(self):
        """
        handles generation of String compilation
        Returns: None
        """
        string = self.tokenizer.string_val()
        self.writer.write_push("constant", len(string))
        self.writer.write_call("String.new", 1)
        for ch in string:
            self.writer.write_push("constant", ord(ch))
            self.writer.write_call("String.appendChar", 2)

    def compile_symbol(self):
        """
        handles compilation of a symbol
        Returns: None
        """
        if self.tokenizer.get_cur_token() == "(":
            self.validate_and_advance("(")
            self.compile_expression()
            self.validate_and_advance(")")
        else:
            curSymbol = self.tokenizer.get_cur_token()
            self.next_token()
            self.compile_term()
            self.writer.write_unary(curSymbol)

    def compile_array(self, arrayName:str, arrayFlag=True):
        """
        Handles compilation of array
        Args:
            arrayName: the array's name
            arrayFlag: indicates whether we currently handle array. required for the compile_expression function

        Returns: None

        """
        self.validate_and_advance("[")
        self.compile_expression(arrayFlag)
        self.validate_and_advance("]")
        self.writer.write_push(self.symbolTable.kind_of(arrayName), self.symbolTable.index_of(arrayName))
        self.writer.write_arithmetic("+")

    def validate_and_advance(self, expectedTerminal):
        """processes a terminal - prints the line with the needed tabs and throws an error upon mismatch
         with the grammar rule"""
        if self.tokenizer.get_cur_token() != expectedTerminal:
            raise SyntaxError(f"\nError in file '{self.fileName}'\nin line {self.tokenizer.get_cur_line_index()}\nExpected token: '{expectedTerminal}' "
                              f", Actual token: '{self.tokenizer.get_cur_token()}'")
        else:
            if self.tokenizer.has_more_tokens():
                self.tokenizer.advance()

    def next_token(self):
        """
        checks if there is a next token and if so- advance
        Returns: void
        """
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()

    def run(self):
        """
        runs the engine
        """
        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            self.compile_class()
