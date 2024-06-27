import numpy as np


def string_to_color(input_string: str):
    """
    Convert a string to a random RGB color. Importantly, the same string will always return the same color.
    Used for consistent coloring of objects based on their name.

    :param input_string: The string to convert to a color
    :return: The RGB color as 3-element a numpy array
    """

    hash_value = hash(input_string)
    np.random.seed(hash_value)

    return np.random.randint(0, 256, 3)
