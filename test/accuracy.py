import copy
import time
import csv
import os
from typing import Optional

import numpy as np
import tabulate

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from processing import processing
from processing.data import meta

from visual import figure_utils


def algorithm_output(c_s=0.67, dist_threshold: Optional[float] = None, verbose=False):
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
        file for file in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/test"))
        if file.endswith(".npy")
    ]

    for i, file in enumerate(files):
        if verbose:
            print(f"Processing file {i + 1}/{len(files)}: {file}")

        start = time.perf_counter()
        output = processing.get_area(
            np.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), f"../data/test/{file}")),
            meta.Scale(5.03, 42.017),
            c_s=c_s,
            dist_threshold=dist_threshold,
            visualize=False,
            visualize_end=False
        )
        end = time.perf_counter()

        algorithm_area = output.area_nm / 1e6

        algorithm_output_dict[file] = {"area": algorithm_area, "time": end - start, "voxels": len(output.points)}

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
    
    for file in os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/test")):
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


def display_percentage_bar_graph(alg_output, ground_truths, compare_to: str) -> None:
    """
    Displays a bar graph of the algorithm's output compared to the ground truth

    :param alg_output: The algorithm's output. Dictionary: {filename: {"area": algorithm_area, "time": time_taken}}
    :param ground_truths: The output of a csv.DictReader object
    :param compare_to: The column name to compare the algorithm output to
    """

    ground_truths = copy.deepcopy(ground_truths)

    alg_output_items = list(alg_output.items())

    # Code adapted from:
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html

    files = [file for file, _ in alg_output_items]
    bar_data = {}

    filename_by_row = [row["filename"] for row in ground_truths]
    names_by_row = [row["PSD name"] for row in ground_truths]

    for row_idx, file in enumerate(filename_by_row):
        row = ground_truths[row_idx]

        for key, item in [("Algorithm Output", alg_output[file]["area"])] + list(row.items()):
            if key.lower() in (compare_to.lower(), "filename", "psd num", "psd name"):
                continue

            # Set item to 0 if it is not a number
            try:
                item = float(item)
                comparison = float(row[compare_to])
            except ValueError:
                item = 0
                comparison = -1

            if comparison == -1:
                percent_diff = 0
            else:
                percent_diff = abs((item - comparison) / comparison * 100)

            key = key.capitalize()  # Capitalize the first letter of the key for aesthetics
            bar_data[key] = bar_data.get(key, [])
            bar_data[key].append(percent_diff)

    x = np.arange(len(files))  # the label locations
    width = 0.125  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout="constrained")
    fig.set_size_inches(9.75, 5.5)

    for attribute, measurement in bar_data.items():
        offset = width * multiplier
        ax.bar(x + offset, measurement, width, label=attribute, color=figure_utils.str_to_rgb(attribute))
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel(f"Absolute % difference to {compare_to.capitalize()}", fontname="Calibri", fontsize=18, fontweight="bold")
    ax.set_title("Algorithm Output Compared to Amira", fontname="Calibri", fontsize=22, fontweight="bold", pad=10)

    ax.set_xticks(x + width, names_by_row, fontname="Calibri", fontsize=18)

    for label in ax.get_yticklabels():
        label.set_fontname("Calibri")
        label.set_fontsize(18)

    ax.legend(prop={"family": "Calibri", "size": 16})

    plt.show()


def display_percent_box_plot(alg_output, ground_truths, compare_to) -> None:
    """
    Displays a box plot of each algorithm's performance (percent difference) compared to the ground truth

    :param alg_output: The algorithm's output. Dictionary: {filename: {"area": algorithm_area, "time": time_taken}}
    :param ground_truths: The output of a csv.DictReader object
    :param compare_to: The column name to compare the algorithm
    """

    ground_truths = copy.deepcopy(ground_truths)

    algorithms = {}

    for row in ground_truths:
        pancake_output = alg_output.get(row["filename"])

        if pancake_output is None:
            print(f"Warning: could not find algorithm output for file {row['filename']}")
            continue

        for key, item in [("Algorithm", pancake_output["area"])] + list(row.items()):
            if key in (compare_to, "filename", "PSD num", "PSD name"):
                continue

            # Skip item if it is not a number
            if isinstance(item, str) and not item.replace(".", "", 1).isdigit():
                continue

            item = float(item)
            percent_diff = abs((item - float(row[compare_to])) / float(row[compare_to]) * 100)

            key = key.capitalize()
            algorithms[key] = algorithms.get(key, [])
            algorithms[key].append(percent_diff)

    fig, ax = plt.subplots()
    fig.set_size_inches(9.75, 5.5)
    ax.set_title("Algorithm Performance Compared to Amira", fontname="Calibri", fontsize=22, fontweight="bold", pad=10)
    ax.set_ylabel("Absolute % Difference to Amira", fontname="Calibri", fontsize=18, fontweight="bold")

    df_data = {"Algorithm": [], "Percent Difference": []}

    for key, value in algorithms.items():
        for i in range(len(value)):
            df_data["Algorithm"].append(key)
            df_data["Percent Difference"].append(value[i])

    df = pd.DataFrame(df_data)

    palette = {
        key: figure_utils.str_to_rgb(key) for key in algorithms.keys()
    }

    sns.swarmplot(data=df, x="Algorithm", y="Percent Difference", ax=ax, color="black", alpha=0.75)
    sns.boxplot(
        data=df, x="Algorithm", y="Percent Difference", hue="Algorithm", ax=ax, palette=palette,
        showfliers=False, legend=False
    )

    for label in ax.get_yticklabels():
        label.set_fontname("Calibri")
        label.set_fontsize(18)

    for label in ax.get_xticklabels():
        label.set_fontname("Calibri")
        label.set_fontsize(16)

    ax.set_xlabel("Algorithms", fontname="Calibri", fontsize=18, fontweight="bold")

    plt.show()


def display_absolute_bar_graph(alg_output, ground_truths, compare_to) -> None:
    """
    Displays a bar graph of the algorithm's output compared to the ground truth

    :param alg_output: The algorithm's output. Dictionary: {filename: {"area": algorithm_area, "time": time_taken}}
    :param ground_truths: The output of a csv.DictReader object
    :param compare_to: The column name to compare the algorithm output to
    """

    ground_truths = copy.deepcopy(ground_truths)
    ground_truths.sort(key=lambda row: row["filename"])  # sort ground truth rows by filename
    names_by_row = [row["PSD name"] for row in ground_truths]

    alg_output_items = list(alg_output.items())

    # Sort alg_output_items and names_by_row
    names_by_row, alg_output_items = zip(*sorted(zip(names_by_row, alg_output_items)))

    # Code adapted from:
    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html

    files = [file for file, _ in alg_output_items]
    bar_data = {
        compare_to: [],  # put the first algorithm name before this algorithm
        "Algorithm output": [output["area"] for _, output in alg_output_items]
    }

    # TODO: clean up the following spaghetti code triple-nested loop
    for file in files:
        for row in ground_truths:
            if row["filename"] != file:
                continue

            for key, item in row.items():
                if key in ("filename", "PSD num", "PSD name"):
                    continue

                # Set item to 0 if it is not a number
                try:
                    item = float(item)
                except ValueError:
                    item = 0

                key = key.capitalize()  # Capitalize the first letter of the key for aesthetics

                bar_data[key] = bar_data.get(key, [])
                bar_data[key].append(item)

            break

        else:  # no break, could not find file
            raise ValueError(f"File {file} not found in ground truth CSV")

    x = np.arange(len(files))  # the label locations
    width = 0.125  # the width of the bars
    multiplier = 0

    fig, ax = plt.subplots(layout="constrained")
    fig.set_size_inches(9.75, 5.5)

    for attribute, measurement in bar_data.items():
        offset = width * multiplier
        ax.bar(x + offset, measurement, width, label=attribute, color=figure_utils.str_to_rgb(attribute))
        multiplier += 1

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Output (μm²)", fontname="Calibri", fontsize=16, fontweight="bold")
    ax.set_title("Algorithm Output Compared to Other Techniques", fontname="Calibri", fontsize=22, fontweight="bold", pad=10)

    ax.set_xticks(x + width, names_by_row, fontname="Calibri", fontsize=18)

    for label in ax.get_yticklabels():
        label.set_fontname("Calibri")
        label.set_fontsize(18)

    ax.legend(prop={"family": "Calibri", "size": 16})

    plt.show()


def main():
    # TODO: the visualization code in this entire file is repeated and kind of messy

    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/test/areas.csv"), "r") as f:
        ground_truths = list(csv.DictReader(f))

    alg_output = algorithm_output(c_s=0.2, verbose=True)
    alg_output_sum, ground_truth_sum, abs_diff, sum_time, table_rows = summary_stats(alg_output, ground_truths, "amira")

    table_header = ["File", "Algorithm Area", "Actual Area", "Difference", "% Difference", "Time Taken"]
    print(tabulate.tabulate(table_rows, headers=table_header, tablefmt="orgtbl"))
    
    print("\n")
    print(f"Total absolute difference: {abs_diff:.6f} μm²")
    print(f"Total relative difference: {abs_diff / ground_truth_sum:.6f} μm² "
          f"(positive = overshoot, negative = undershoot)")
    print(f"Total time: {sum_time:.4f}s")
    print(f"Average time: {sum_time / len(table_rows):.4f}s")

    display_percentage_bar_graph(alg_output, ground_truths, "amira")
    display_percent_box_plot(alg_output, ground_truths, "amira")
    display_absolute_bar_graph(alg_output, ground_truths, "Amira")


if __name__ == "__main__":
    main()
