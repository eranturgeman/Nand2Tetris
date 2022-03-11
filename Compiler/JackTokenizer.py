"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

KEYWORDS = {'class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void',
            'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return'}

SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~'}

SPACIAL_SYMBOLS = {"<": "&lt;", ">": "&gt;", "&": "&amp;"}

SEPARATORS = {' ', '\n', '//', '/*', '/**', '\t'}

INTEGER_LOWER_BOUND = 0
INTEGER_UPPER_BOUND = 32767

class JackTokenizer:
    def __init__(self, inputStream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            inputStream (typing.TextIO): input stream.
        """
        self.__inputLines = inputStream.read().splitlines()
        self.__curToken = None
        self.__curLineIndex = 0

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        while self.__curLineIndex < len(self.__inputLines):
            if self.__hasTokenInCurrentLine():
                return True
            self.__curLineIndex += 1
        return False



    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        self.__inputLines[self.__curLineIndex] = self.__inputLines[self.__curLineIndex].lstrip()
        curLine = self.__inputLines[self.__curLineIndex]

        if curLine.startswith("\""):
            token = "\""
            endIndex = 1
            for i, ch in enumerate(curLine[1:]):
                if ch != "\"":
                    token += ch
                else:
                    token += ch
                    endIndex += i
                    break
            self.__curToken = curLine[:endIndex + 1]
            self.__inputLines[self.__curLineIndex] = self.__inputLines[self.__curLineIndex][endIndex + 1:]
            return

        if curLine[0].isdigit():
            self.__curToken = ""
            endingIndex = 0
            for i, ch in enumerate(curLine):
                if ch.isdigit():
                    self.__curToken += ch
                else:
                    endingIndex = i
                    break
            self.__inputLines[self.__curLineIndex] = self.__inputLines[self.__curLineIndex][endingIndex:]
            return

        if curLine[0] in SYMBOLS:
            self.__curToken = curLine[0]
            self.__inputLines[self.__curLineIndex] = self.__inputLines[self.__curLineIndex][1:]
            return

        self.__curToken = ""
        endIndex = 0
        for i, ch in enumerate(curLine):
            if ch not in SEPARATORS and ch not in SYMBOLS:
                self.__curToken += ch
                endIndex = i + 1
            else:
                endIndex = i
                break
        self.__inputLines[self.__curLineIndex] = self.__inputLines[self.__curLineIndex][endIndex:]
        return

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # keyword
        if self.__curToken in KEYWORDS:
            return "keyword"

        # symbol
        if self.__curToken in SYMBOLS:
            return "symbol"

        # string constant
        if re.search("^\".*\"", self.__curToken) or re.search("^\'.*\'", self.__curToken):
            return "stringConstant"

        # int
        if re.search("^[0-9][0-9]*", self.__curToken):
            return "integerConstant"

        # identifier
        if re.search("^[a-zA-Z_]\w*", self.__curToken):
            return "identifier"

        return ""

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.__curToken

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
        """
        if self.__curToken in SPACIAL_SYMBOLS:
            return SPACIAL_SYMBOLS[self.__curToken]
        return self.__curToken

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
        """
        return self.__curToken

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
        """
        return int(self.__curToken)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
        """
        return self.__curToken.strip("\"")

    def get_cur_token(self):
        return self.__curToken

    def get_cur_line_index(self):
        return self.__curLineIndex

# ==================== helper functions ======================
    def __hasTokenInCurrentLine(self):
        curTrimmedLine = self.__inputLines[self.__curLineIndex].strip().replace("\n", "")
        if not curTrimmedLine:
            return False

        if curTrimmedLine.startswith("//") or curTrimmedLine.startswith("/*") or curTrimmedLine.startswith("/**"):
            self.__removeComment()
            return self.has_more_tokens()
        return True


    def __removeComment(self):
        leftTrimmedLine = self.__inputLines[self.__curLineIndex].lstrip()
        if leftTrimmedLine.startswith("//"):
            self.__curLineIndex += 1
            return

        if leftTrimmedLine.startswith("/*") or leftTrimmedLine.startswith("/**"):
            while not re.search("\*/", leftTrimmedLine):
                self.__curLineIndex += 1
                leftTrimmedLine = self.__inputLines[self.__curLineIndex]
            endIndex = re.search("\*/", self.__inputLines[self.__curLineIndex]).end()
            self.__inputLines[self.__curLineIndex] = self.__inputLines[self.__curLineIndex][endIndex:]
            return

