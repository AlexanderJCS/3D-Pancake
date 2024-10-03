import numpy as np


COLORS_MAP = {
    "algorithm output": "xkcd:cornflower blue",
    "algorithm": "xkcd:cornflower blue",
    "amira": "xkcd:pale orange",
    "convex hull / 2": "#52A55D",  # green
    "marching cubes / 2": "#D7E52C",  # a vibrant yellow but not too bright
    "lindblad / 2": "xkcd:pinkish red",
    "espina": "xkcd:light eggplant",
    "morales": "xkcd:light eggplant",
}


def str_to_rgb(input_string: str):
    """
    Convert a string to a random RGB color. Importantly, the same string will always return the same color.
    Used for consistent coloring of objects based on their name.

    Some colors are pre-defined for specific strings, accessible in the COLORS_MAP dictionary.

    :param input_string: The string to convert to a color.
    :return: A color recognizable by matplotlib
    """

    if input_string.lower() in COLORS_MAP:
        return COLORS_MAP[input_string.lower()]

    hash_value = hash(input_string)
    np.random.seed(hash_value % 2**32)

    return tuple(np.concatenate((np.random.rand(3), np.array([1]))))
