# Ian's very silly python calculators.

Each `*_calc.py` file in this repo is a calculator implemented in a very silly way.

All accept complex expressions involving floating point numbers, parenthesis, and operators `+`, `-`, `*` and `/`.

Inspired by [my\_first\_calculator.py](https://github.com/AceLewis/my_first_calculator.py).

## Safety first calculator

This calculator runs an `eval()` of the user input, but first mangles the alphabetic characters in the input to be VERY SAFE from injection attacks.

## Speed matters calculator

This calculator searches the space of possible floating point values to find one that satisfies conditions to be called the result of the operation.

It does a binary search instead of a simple incrementing search to be VERY FAST.

## Intelligent calculator

This calculator trains machine learning models to do the basic arithmetic operations and then uses them to calculate the result.

This calculator is VERY INTELLIGENT, but it most likely won't get the right result for operations involving multiplication and division.
