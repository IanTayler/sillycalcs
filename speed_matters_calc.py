"""Calculator script that cares about speed.

Does a binary search on possible floating point values, because a binary search is
much faster than for-looping over all floating point values; and speed matters."""
import sys

import actual_parser


OP_FUNC = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}


class BinarySearchInterpreter(actual_parser.TreeInterpreter):
    """Interpret by getting continually closer to the result."""

    def n_value(self, token):
        # Nothing fancy here.
        return float(token)

    @staticmethod
    def _binary_search(diff_evaluator):
        def adjust_epsilon(initial_epsilon, value):
            # we need to find the appropriate epsilon for this
            # value size. For large numbers, a + epsilon == a,
            # which means we need to adjust epsilon
            epsilon = initial_epsilon
            while value + epsilon == value:
                epsilon *= 2
            return epsilon

        minv = -sys.float_info.max
        maxv = sys.float_info.max
        currv = minv
        base_epsilon = sys.float_info.epsilon
        epsilon = adjust_epsilon(base_epsilon, currv)
        while abs(diff_evaluator(currv)) > epsilon:
            diff = diff_evaluator(currv)
            if diff > 0:
                maxv = currv
            else:
                minv = currv
            currv = (minv + maxv) / 2
            # adjust epsilon for the new value.
            epsilon = adjust_epsilon(base_epsilon, currv)
        return currv

    def sum_value(self, lv, rv):
        def sum_diff(possible_result):
            return possible_result - lv - rv

        return self._binary_search(sum_diff)

    def sub_value(self, lv, rv):
        def sub_diff(possible_result):
            return possible_result - lv + rv

        return self._binary_search(sub_diff)

    def prod_value(self, lv, rv):
        def prod_diff(possible_result):
            return (possible_result / (lv * rv)) - 1

        return self._binary_search(prod_diff)

    def div_value(self, lv, rv):
        return lv / rv


def _one_calc():
    # Receive input from the user.
    # Close the program when we get Ctrl+C or Ctrl+D.
    try:
        user_input = input()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    parser = actual_parser.Parser(user_input)
    ast = parser.parse()
    interpreter = BinarySearchInterpreter(ast)
    print(interpreter.eval())


if __name__ == "__main__":
    while True:
        _one_calc()
