"""Calculator script that cares about safety.

Runs an eval on the user input, but first mangles alphabetic characters, to prevent
arbitrary python code from running on input, which is safer than just running it
without mangling; and we should always think about safety first."""
import random
import sys


def _one_calc():
    # Receive input from the user.
    # Close the program when we get Ctrl+C or Ctrl+D.
    try:
        user_input = input()
    except (KeyboardInterrupt, EOFError):
        sys.exit(0)
    # Mangle the input so that alphabetic characters in the input are shifted
    # by a random int to a different unicode character.
    # Non-alphabetic chatacters stay the same.
    mangled_input = "".join(
        [chr(ord(c) + random.randint(1, 10)) if c.isalpha() else c for c in user_input]
    )
    # Now eval the mangled input, hoping that shifting alphabetic characters
    # has rendered any malicious code unusable.
    # Despite the name of the script, this isn't very safe.
    try:
        print(eval(mangled_input))
    except ZeroDivisionError:
        print("Don't divide by 0!")
    except:  # pylint: disable=bare-except
        # Silently exit with error because user might be trying to run malicious code.
        sys.exit(1)


if __name__ == "__main__":
    while True:
        _one_calc()
