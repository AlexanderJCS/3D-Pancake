import json
import time
import os

import numpy as np
import tabulate

from processing import processing
from processing.data import meta


def accuracy(filepath: str, c_s=0.67):
    """
    Calculates the accuracy of the algorithm.
    TODO: include other algorithms instead of just human/amira data

    :param filepath: The filepath to the .npy data
    :param c_s: The constant for the sigma formula
    :return: [algorithm_area, actual_area, time_taken]
    """

    data = np.load(filepath)

    # Calculate the algorithm's area
    start = time.time()
    algorithm_area = processing.get_area(data, meta.Scale(5.03, 42.017), c_s=c_s, visualize=False).area_nm
    algorithm_area /= 1e6  # Convert to um^2
    end = time.time()

    # Find the actual area
    with open("../data/test/areas.json", "r") as f:
        ground_truths = json.load(f)

    filename = os.path.basename(filepath)
    filename = filename[:filename.rfind(".")]  # remove file extension

    return algorithm_area, ground_truths.get(filename), end - start


def total_accuracy(c_s=0.67):
    """
    Calculate the total accuracy of the algorithm
    
    :return: [algorithm_area_sum, actual_area_sum, abs_diff, sum_time, table_rows]
    """
    
    table_rows = []
    
    alg_output_sum = 0
    ground_truth_sum = 0
    abs_diff = 0
    sum_time = 0
    
    for file in os.listdir("../data/test"):
        if not file.endswith(".npy"):
            continue
        
        alg_output, ground_truth, time_taken = accuracy(f"../data/test/{file}", c_s)
        
        alg_output_sum += alg_output
        ground_truth_sum += ground_truth
        abs_diff += abs(alg_output - ground_truth)
        sum_time += time_taken
        
        table_rows.append(
            [
                os.path.basename(file),
                f"{alg_output:.6f} μm²",
                f"{ground_truth:.6f} μm²",
                f"{alg_output - ground_truth:.6f} μm²",
                f"{(alg_output - ground_truth) / ground_truth * 100:.1f}%",
                f"{time_taken:.4f}s"
            ]
        )
    
    return alg_output_sum, ground_truth_sum, abs_diff, sum_time, table_rows


def main():
    table_header = ["File", "Algorithm Area", "Actual Area", "Difference", "% Difference", "Time Taken"]
    alg_output_sum, ground_truth_sum, abs_diff, sum_time, table_rows = total_accuracy()
    
    print(tabulate.tabulate(table_rows, headers=table_header, tablefmt="orgtbl"))
    
    print("\n")
    print(f"Total absolute difference: {abs_diff:.6f} μm²")
    print(f"Total relative difference: {abs_diff / ground_truth_sum:.6f} μm² "
          f"(positive = overshoot, negative = undershoot)")
    print(f"Total time: {sum_time:.4f}s")
    print(f"Average time: {sum_time / len(table_rows):.4f}s")


if __name__ == "__main__":
    main()
