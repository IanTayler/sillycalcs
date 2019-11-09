# Ian's very silly python calculators.

Each `*_calc.py` file in this repo is a calculator implemented in a very silly way.

All are meant to be used interactively and accept complex expressions involving floating point numbers, parenthesis, and operators `+`, `-`, `*` and `/`.

e.g. `12 * (5 + 4) * 9 / 4 - 15`

Some of them give the right answer, some don't.


## Implemented calculators

### Safety first calculator

This calculator runs an `eval()` of the user input, but first mangles the alphabetic characters in the input to be VERY SAFE from injection attacks.

Implemented on [safety\_first\_calc.py](/safety_first_calc.py).

### Speed matters calculator

This calculator searches the space of possible floating point values to find one that satisfies conditions to be called the result of the operation.

It does a binary search instead of a simple incrementing search to be VERY FAST.

Implemented on [speed\_matters\_calc.py](/speed_matters_calc.py).

### Intelligent calculator

This calculator trains machine learning models to do the basic arithmetic operations and then uses them to calculate the result.

This calculator is VERY INTELLIGENT, but it most likely won't get the right result for operations involving multiplication and division.

Implemented on [intelligent\_calc.py](/intelligent_calc.py).

## Inspiration

Inspired by [my\_first\_calculator.py](https://github.com/AceLewis/my_first_calculator.py).
