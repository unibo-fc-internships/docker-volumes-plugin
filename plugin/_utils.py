import re


PATTERN_SNAKE_CASE = re.compile(r"^([a-z][a-z0-9]*)(?:_+([a-z][a-z0-9]*))*$")
PATTERN_PASCAL_CASE = re.compile(r"^([A-Z][a-z0-9]*)(?:([A-Z][a-z0-9]*))*$")
PATTERN_CAMEL_CASE = re.compile(r"^([a-z][a-z0-9]*)(?:([A-Z][a-z0-9]*))*$")
PATTERN_KEBAB_CASE = re.compile(r"^([a-z][a-z0-9]*)(?:-+([a-z][a-z0-9]*))*$")
PATTERN_CAPITALIZED_WORD = re.compile(r"[A-Z][a-z0-9]*")


class Sentence:
    def __init__(self, string: str):
        if not string:
            raise ValueError("Empty sentence")
        if PATTERN_SNAKE_CASE.fullmatch(string):
            self._tokens = string.split("_")
        elif PATTERN_KEBAB_CASE.fullmatch(string):
            self._tokens = string.split("-")
        elif PATTERN_PASCAL_CASE.fullmatch(string):
            self._tokens = [word.lower() for word in PATTERN_CAPITALIZED_WORD.findall(string)]
        else:
            camel = PATTERN_CAMEL_CASE.fullmatch(string)
            if camel:
                self._tokens = [camel.group(1).lower()]
                self._tokens.extend(PATTERN_CAPITALIZED_WORD.findall(camel.group(2)))
            else:
                self._tokens = [word.lower() for word in string.split()]

    def __str__(self):
        return str(self._tokens)

    def __repr__(self):
        return str(self)

    def __eq__(self, o: object) -> bool:
        return self._tokens == o._tokens

    def __hash__(self) -> int:
        return hash(self._tokens)

    def camel_case(self):
        if len(self._tokens) == 1:
            return self._tokens[0]
        return self._tokens[0] + "".join([word.capitalize() for word in self._tokens[1:]])
    
    def pascal_case(self):
        return "".join([word.capitalize() for word in self._tokens])

    def snake_case(self):
        return "_".join(self._tokens)
    
    def kebab_case(self):
        return "-".join(self._tokens)
