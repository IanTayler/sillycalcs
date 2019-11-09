"""This is an actual recursive-descent parser.

I'm sorry I didn't find something funnier to do here."""
from abc import ABC, abstractmethod
from collections import namedtuple
import typing as T


def is_number_char(c: str) -> bool:
    """Check if char c is part of a number."""
    return c.isdigit() or c == "."


def is_char_token(c: str) -> bool:
    """Return true for single character tokens."""
    return c in ["+", "-", "*", "/", "(", ")"]


class ExprSyntaxError(Exception):
    """Error parsing the expression."""


class UnexpectedChar(ExprSyntaxError):
    """Syntax error due to unexpected character."""


Token = namedtuple("Token", ["tok_type", "tok"])

SyntaxNode = namedtuple("SyntaxNode", ["token", "children"])


class Tokenizer:
    """Tokenizer for calculator expressions.

    It's an iterable, and it can also be used by calling next_token repeatedly.

    Args:
        s: string to tokenize.
    """

    def __init__(self, s: str):
        self.s = s
        self.pos = 0

    @property
    def current(self) -> str:
        """Return char being pointed."""
        return self.s[self.pos]

    def consume(self) -> str:
        """Advance to next char, returning current one."""
        c = self.current
        self.pos += 1
        return c

    def has_finished(self) -> bool:
        """Check if we've analyzed the entire string."""
        return self.pos >= len(self.s)

    def __iter__(self):
        self.pos = 0
        return self

    def __next__(self) -> Token:
        tok = self.next_token()
        if tok is None:
            raise StopIteration
        return tok

    def next_token(self) -> T.Optional[Token]:
        """Returns the next token in the string, or None if there are no more."""
        if self.has_finished():
            return None
        token_type = None
        token_chars = []
        if is_number_char(self.current):
            token_type = "N"
            while not self.has_finished() and is_number_char(self.current):
                token_chars.append(self.consume())
        elif is_char_token(self.current):
            if self.current in ["(", ")"]:
                token_type = self.current
            elif self.current in ["+", "-"]:
                token_type = "S"
            elif self.current in ["*", "/"]:
                token_type = "M"
            else:
                raise ExprSyntaxError
            token_chars.append(self.consume())
        elif self.current.isspace():
            self.consume()
            return self.next_token()
        else:
            raise UnexpectedChar
        return Token(token_type, "".join(token_chars))


class Parser:
    """Used to get an AST for a calculator expression.

    Args:
        s: string to parse.
    """

    def __init__(self, s):
        tokenizer = Tokenizer(s)
        self.tokens = list(iter(tokenizer))
        # We store the tokens reverse to make the simple LL
        # parsers work.
        self.tokens.reverse()
        self.pos = 0

    def ahead(self, k):
        """Read k tokens ahead of the current one.

        For this implementation, k should always be 1."""
        assert k == 1
        if self.pos + k < len(self.tokens):
            return self.tokens[self.pos + k]
        return None

    @property
    def current(self) -> Token:
        """Return token under consideration."""
        return self.tokens[self.pos]

    def has_finished(self) -> bool:
        """Check if the parser has finished parsing."""
        return self.pos >= len(self.tokens)

    def consume_if(self, tok_type: str) -> Token:
        """Advance the pointer if the current token is of the right type.

        Otherwise, raise ExprSyntaxError."""
        curr = self.current
        if curr.tok_type != tok_type:
            raise ExprSyntaxError
        self.pos += 1
        return curr

    def _parse_cat_binary(
        self, expected_type: str, next_parse_func: T.Callable
    ) -> SyntaxNode:
        ahead = self.ahead(1)
        if ahead and ahead.tok_type == expected_type:
            first_tok = self.parse_value()
            op_tok = self.consume_if(expected_type)
            second_tok = self._parse_cat_binary(expected_type, next_parse_func)
            # reverse order to make up for our reverse token order.
            return SyntaxNode(token=op_tok, children=[second_tok, first_tok])
        first_tok = next_parse_func()
        if not self.has_finished() and self.current.tok_type == expected_type:
            op_tok = self.consume_if(expected_type)
            second_tok = self._parse_cat_binary(expected_type, next_parse_func)
            # reverse order to make up for our reverse token order.
            return SyntaxNode(token=op_tok, children=[second_tok, first_tok])
        return first_tok

    def parse_value(self) -> SyntaxNode:
        """Parse a value (i.e. a factor in this case).

        Handles parenthesised expressions and direct numeric values."""
        if self.current.tok_type == ")":
            self.consume_if(")")
            node = self.parse_expr()
            self.consume_if("(")
            return node
        token = self.consume_if("N")
        return SyntaxNode(token=token, children=[])

    def parse_term(self) -> SyntaxNode:
        """Parse a term to get the corresponding SyntaxNode.

        Handles multiplication and division."""
        return self._parse_cat_binary("M", self.parse_value)

    def parse_expr(self) -> SyntaxNode:
        """Parse a calculator expression.

        Handles sum and subtraction."""
        return self._parse_cat_binary("S", self.parse_term)

    def parse(self) -> T.Optional[SyntaxNode]:
        """Parse the string with which we initialized the calculator.

        Returns a SyntaxNode or None if there is no expression."""
        if self.tokens:
            return self.parse_expr()
        return None


class EvalError(Exception):
    """Interpreter error. Something in the AST is malformed for interpretation."""


class TreeInterpreter(ABC):
    """Abstract class for SyntaxNode direct interpreters.

    Overriding the *_value methods and calling eval is all that
    is needed to get a working AST interpreter."""

    def __init__(self, syntax_tree: SyntaxNode):
        self.syntax_tree = syntax_tree

    @abstractmethod
    def n_value(self, token):
        """Method that returns a value from an N token."""

    @abstractmethod
    def sum_value(self, lv, rv):
        """Method that returns a value from a sum tree.

        It takes the left and right values, already computed."""

    @abstractmethod
    def sub_value(self, lv, rv):
        """Method that returns a value from a subtract tree.

        It takes the left and right values, already computed."""

    @abstractmethod
    def prod_value(self, lv, rv):
        """Method that returns a value from a prod tree.

        It takes the left and right values, already computed."""

    @abstractmethod
    def div_value(self, lv, rv):
        """Method that returns a value from a division tree.

        It takes the left and right values, already computed."""

    def _eval_node(self, node: SyntaxNode):
        tok_type = node.token.tok_type
        tok = node.token.tok
        if tok_type == "N":
            return self.n_value(tok)
        assert len(node.children) == 2
        try:
            left_val = self._eval_node(node.children[0])
            right_val = self._eval_node(node.children[1])
        except IndexError:
            raise EvalError
        if tok == "+":
            return self.sum_value(left_val, right_val)
        if tok == "-":
            return self.sub_value(left_val, right_val)
        if tok == "*":
            return self.prod_value(left_val, right_val)
        if tok == "/":
            return self.div_value(left_val, right_val)
        # If we got here, it's an unknown operation.
        raise EvalError

    def eval(self):
        """Returns the value of the AST as per the implementation of abstract methods.

        It evaluates the ast that was set in the creation of the interpreter."""
        return self._eval_node(self.syntax_tree)


class ExampleInterpreter(TreeInterpreter):
    """This is an example of an interpreter. It computes operations directly."""

    def n_value(self, token):
        return float(token)

    def sum_value(self, lv, rv):
        return lv + rv

    def sub_value(self, lv, rv):
        return lv - rv

    def prod_value(self, lv, rv):
        return lv * rv

    def div_value(self, lv, rv):
        return lv / rv
