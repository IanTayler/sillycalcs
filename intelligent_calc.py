"""Calculator script that pretty much solves general AI.

Trains machine learning models for operations every time you enter an expression.

Accuracy may vary but is pretty much guaranteed to be bad for multiplication and division."""
import random
import sys

from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures

import actual_parser


def random_float():
    """Get a random float, with a very high chance of it being close to 0."""
    return random.normalvariate(0, sys.float_info.min * 50) * sys.float_info.max


def get_fit_data(num_steps, combine_func, polynomial_degree=False, poly=None):
    """Produce data to fit a model."""
    training_data = [[random_float(), random_float()] for _ in range(num_steps)]
    if polynomial_degree:
        training_data = poly.fit_transform(training_data)
    labels = [combine_func(x[0], x[1]) for x in training_data]
    return training_data, labels


class MachineLearningInterpreter(actual_parser.TreeInterpreter):
    """Intepreter using trained models for operations."""

    def __init__(self, tree):
        super(MachineLearningInterpreter, self).__init__(tree)
        NUM_STEPS_LINEAR = 100_000
        NUM_STEPS_POLYNOMIAL = 100_000
        POLYNOMIAL_DEGREE = 20
        print("Training model for sum...")
        self.sum_model = linear_model.LinearRegression()
        self.sum_model.fit(*get_fit_data(NUM_STEPS_LINEAR, lambda x, y: x + y))
        print("Training model for subtraction...")
        self.sub_model = linear_model.LinearRegression()
        self.sub_model.fit(*get_fit_data(NUM_STEPS_LINEAR, lambda x, y: x - y))
        print("Training model for multiplication...")
        self.poly = PolynomialFeatures(degree=POLYNOMIAL_DEGREE)
        self.prod_model = linear_model.LinearRegression()
        self.prod_model.fit(
            *get_fit_data(
                NUM_STEPS_POLYNOMIAL,
                lambda x, y: x * y,
                polynomial_degree=20,
                poly=self.poly,
            )
        )
        print("Training model for division...")
        self.div_model = linear_model.LinearRegression()
        self.div_model.fit(
            *get_fit_data(
                NUM_STEPS_POLYNOMIAL,
                lambda x, y: x / y,
                polynomial_degree=20,
                poly=self.poly,
            )
        )

    def n_value(self, token):
        return float(token)

    def sum_value(self, lv, rv):
        return self.sum_model.predict([[lv, rv]])[0]

    def sub_value(self, lv, rv):
        return self.sub_model.predict([[lv, rv]])[0]

    def prod_value(self, lv, rv):
        return self.prod_model.predict(self.poly.fit_transform([[lv, rv]]))[0]

    def div_value(self, lv, rv):
        return self.div_model.predict(self.poly.fit_transform([[lv, rv]]))[0]


def _one_calc():
    # Receive input from the user.
    # Close the program when we get Ctrl+C or Ctrl+D.
    try:
        user_input = input()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    parser = actual_parser.Parser(user_input)
    ast = parser.parse()
    interpreter = MachineLearningInterpreter(ast)
    print(interpreter.eval())


if __name__ == "__main__":
    while True:
        _one_calc()
