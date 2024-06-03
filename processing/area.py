import numpy as np
from . import data


def get_area(raw_data: np.ndarray) -> float:
    """
    Processes the data
    
    :param raw_data: The raw data to find the surface area of
    :return: Finds the surface area given the raw data
    """
    
    formatted = data.format_data(raw_data)
    print(formatted)
    
    return 0
    