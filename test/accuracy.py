import time
import csv
import os
from typing import Optional

import numpy as np
import tabulate

import matplotlib.pyplot as plt

from processing import processing
from processing.data import meta


def algorithm_output(c_s=0.67, dist_threshold: Optional[float] = None, downsample=False, verbose=False):
    """
    Calculates the algorithms output.
    :param c_s: The constant for the sigma formula
    :param dist_threshold: The distance threshold to clip each vertex in the final step. If None, the threshold is
                           equal to max(scale.xy, scale.z)
    :param verbose: Whether to print progress
    :return: Dictionary: {filename: {"area": algorithm_area, "time": time_taken}
    """

    algorithm_output_dict = {}

    files = [
        file for file in os.listdir("../data/test")
        if file.endswith(".npy")
    ]

    for i, file in enumerate(files):
        if verbose:
            print(f"Processing file {i + 1}/{len(files)}: {file}")

        start = time.time()
        algorithm_area = processing.get_area(
            np.load(f"../data/test/{file}"),
            meta.Scale(5.03, 42.017),
            c_s=c_s,
            dist_threshold=dist_threshold,
            downsample=downsample,
            visualize=False,
            visualize_end=False
        ).area_nm / 1e6
        end = time.time()

        algorithm_output_dict[file] = {"area": algorithm_area, "time": end - start}

    return algorithm_output_dict


def summary_stats(alg_output, ground_truths, compare_column_name):
    """
    Calculate the total accuracy of the algorithm

    :param alg_output: Dictionary: {filename: {"area": algorithm_area, "time": time_taken}}
    :param ground_truths: The output of a csv.DictReader object
    :param compare_column_name: The name of the column to compare the algorithm output to. Assumes the column is in μm²
                                and a "filename" column exists (case-sensitive, includes file extension)
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

        file = os.path.basename(file)

        for row_index, row in enumerate(ground_truths):
            if row["filename"] == file:
                break
        else:  # no break
            raise ValueError(f"File {file} not found in ground truth CSV")

        try:
            ground_truth = float(ground_truths[row_index][compare_column_name])
        except ValueError:
            raise ValueError(f"Column {compare_column_name} in CSV must contain numerical values")

        alg_area = alg_output[file]["area"]
        alg_time = alg_output[file]["time"]

        alg_output_sum += alg_area
        ground_truth_sum += ground_truth
        abs_diff += abs(alg_area - ground_truth)
        sum_time += alg_time
        
        table_rows.append(
            [
                file,
                f"{alg_area:.6f} μm²",
                f"{ground_truth:.6f} μm²",
                f"{alg_area - ground_truth:.6f} μm²",
                f"{(alg_area - ground_truth) / ground_truth * 100:.1f}%",
                f"{alg_time:.4f}s"
            ]
        )
    
    return alg_output_sum, ground_truth_sum, abs_diff, sum_time, table_rows


def display_bar_graph(alg_output, ground_truths) -> None:
    """
    Displays a bar graph of the algorithm's output compared to the ground truth

    :param alg_output: The algorithm's output. Dictionary: {filename: {"area": algorithm_area, "time": time_taken}}
    :param ground_truths: The output of a csv.DictReader object
    """

    alg_output_items = list(alg_output.items())

    # Code adapted from:
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html

    files = [file for file, _ in alg_output_items]
    bar_data = {"Algorithm Area": [output["area"] for _, output in alg_output_items]}

    for file in files:
        rows_by_filename = [row["filename"] for row in ground_truths]
        row_idx = rows_by_filename.index(file)

        if row_idx == -1:
            raise ValueError(f"File {file} not found in ground truth CSV")

        row = ground_truths[row_idx]

        for key, item in row.items():
            if key.lower() in ("filename", "psd num"):
                continue

            # Set item to 0 if it is not a number
            try:
                item = float(item)
            except ValueError:
                item = 0

            key = key.capitalize()  # Capitalize the first letter of the key for aesthetics

            bar_data[key] = bar_data.get(key, [])
            bar_data[key].append(item)

    x = np.arange(len(files))  # the label locations
    width = 0.15  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout="constrained")

    for attribute, measurement in bar_data.items():
        offset = width * multiplier
        ax.bar(x + offset, measurement, width, label=attribute)
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Output (μm²)")
    ax.set_title("Algorithm Output Compared to Other Techniques")

    # Remove .npy from the file names
    files = [file[:-len(".npy")] for file in files]

    ax.set_xticks(x + width, files)
    plt.xticks(rotation=20, ha="right")
    ax.legend()

    plt.show()


def main():
    with open("../data/test/areas.csv", "r") as f:
        ground_truths = list(csv.DictReader(f))

    alg_output = algorithm_output(c_s=0.2, dist_threshold=80, verbose=True)
    alg_output_sum, ground_truth_sum, abs_diff, sum_time, table_rows = summary_stats(alg_output, ground_truths, "amira")

    table_header = ["File", "Algorithm Area", "Actual Area", "Difference", "% Difference", "Time Taken"]
    print(tabulate.tabulate(table_rows, headers=table_header, tablefmt="orgtbl"))
    
    print("\n")
    print(f"Total absolute difference: {abs_diff:.6f} μm²")
    print(f"Total relative difference: {abs_diff / ground_truth_sum:.6f} μm² "
          f"(positive = overshoot, negative = undershoot)")
    print(f"Total time: {sum_time:.4f}s")
    print(f"Average time: {sum_time / len(table_rows):.4f}s")

    display_bar_graph(alg_output, ground_truths)


if __name__ == "__main__":
    main()
