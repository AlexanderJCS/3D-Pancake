import json
import os

import numpy as np

from processing import processing
from processing.data import meta


def accuracy(filepath: str):
    """
    Calculates the accuracy of the algorithm. Returns a tuple of two floats: the algorithm's area and the actual area.
    TODO: include other algorithms instead of just human/amira data

    :param filepath: The filepath to the .npy data
    :return: [algorithm_area, actual_area]
    """

    # Load the data
    data = np.load(filepath)

    # Calculate the algorithm's area
    algorithm_area = processing.get_area(data, meta.Scale(5.03, 42.017), c_s=0.67, visualize=False).area_nm
    algorithm_area /= 1e6  # Convert to um^2

    # Find the actual area
    with open("../data/test/areas.json", "r") as f:
        ground_truths = json.load(f)

    filename = os.path.basename(filepath)
    filename = filename[:filename.rfind(".")]  # remove file extension

    # Return the areas
    return [algorithm_area, ground_truths.get(filename)]


def main():
    print("Name\tAlg area\tActual area\tDifference")

    alg_output_sum = 0
    ground_truth_sum = 0
    abs_diff = 0

    for file in os.listdir("../data/test"):
        if not file.endswith(".npy"):
            continue

        alg_output, ground_truth = accuracy(f"../data/test/{file}")

        alg_output_sum += alg_output
        ground_truth_sum += ground_truth
        abs_diff += abs(alg_output - ground_truth)

        print(f"{os.path.basename(file)} {alg_output:.6f}\t{ground_truth:.6f}\t{alg_output - ground_truth:.6f}")

    print(f"Total: {alg_output_sum:.6f}\t{ground_truth_sum:.6f}\t{alg_output_sum - ground_truth_sum:.6f}")
    print(f"Abs diff: {abs_diff:.6f}")


if __name__ == "__main__":
    main()
