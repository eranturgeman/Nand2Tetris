"""This file is part of nand2tetris, as taught in The Hebrew University,
and was written by Aviv Yaish according to the specifications given in  
https://www.nand2tetris.org (Shimon Schocken and Noam Nisan, 2017)
and as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0 
Unported License (https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

TYPE = 0
KIND = 1
INDEX = 2
CLASS_SCOPE = ["static", "field"]
SUBROUTINE_SCOPE = ["var", "arg"]

class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.classTable = dict()
        self.subroutineTable = dict()
        self.classRunner = {"static": 0, "field": 0}
        self.subroutineRunner = {"var": 0, "arg": 0}

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutineTable = dict()
        self.subroutineRunner["var"] = 0
        self.subroutineRunner["arg"] = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        # remember: type=0, kind=1, index = 2
        if kind.lower() in CLASS_SCOPE:
            self.classTable[name] = [type, kind, self.classRunner[kind.lower()]]
            self.classRunner[kind.lower()] += 1
        elif kind.lower() in SUBROUTINE_SCOPE:
            self.subroutineTable[name] = [type, kind, self.subroutineRunner[kind.lower()]]
            self.subroutineRunner[kind.lower()] += 1
        else:
            raise TypeError(f"\nERROR: unable to identify identifier {name}.\nGot: {kind}")

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        if kind.lower() in CLASS_SCOPE:
            return self.classRunner[kind]
        elif kind.lower() in SUBROUTINE_SCOPE:
            return self.subroutineRunner[kind]
        else:
            raise TypeError(f"\nERROR: incorrect kind for variable count.\nGot: {kind}")

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        # field, static ,arg, var

        if name in self.subroutineTable:
            return self.subroutineTable[name][KIND]
        elif name in self.classTable:
            return self.classTable[name][KIND]
        else:
            return None

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        # int, Point, char, boolean

        if name in self.subroutineTable:
            return self.subroutineTable[name][TYPE]
        elif name in self.classTable:
            return self.classTable[name][TYPE]
        else:
            raise TypeError(f"ERROR: unable to find '{name}' in any symbol table")

    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutineTable:
            return self.subroutineTable[name][INDEX]
        elif name in self.classTable:
            return self.classTable[name][INDEX]
        else:
            raise TypeError(f"ERROR: unable to find '{name}' in any symbol table")
