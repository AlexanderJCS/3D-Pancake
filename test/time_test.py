import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

import accuracy

import csv


def plot_times(name, times) -> None:
    """
    Plots the times of the algorithm for each file.
    :param name: The names of each file for the x-axis
    :param times: The time to run the algorithm for the file
    """

    fig, ax = plt.subplots()

    ax.bar(name, times)
    ax.set_xlabel("PSD")
    ax.set_ylabel("Time (s)")
    plt.xticks(rotation=20, ha="right")
    ax.set_title("Runtime for each PSD")
    plt.show()


def plot_times_vs_voxels(name, times, num_voxels) -> None:
    """
    Plots the times of the algorithm for each file.
    :param name: The names of each file for the x-axis
    :param times: The time to run the algorithm for the file
    :param num_voxels: The number of voxels in the file
    """

    fig, ax = plt.subplots()
    fig.set_size_inches(8.71, 6.6)

    # Create a color map
    colors = plt.cm.rainbow(np.linspace(0, 1, len(name)))

    # Add the name of the file to each point and color-code the points
    for i, txt in enumerate(name):
        ax.scatter(num_voxels[i], times[i], color=colors[i], label=txt)

    # Fit a line to the data
    slope, intercept, r_value, p_value, std_err = stats.linregress(num_voxels, times)

    # Plot the line of best fit
    x_values = [0, max(num_voxels)]
    y_values = [intercept, intercept + slope * max(num_voxels)]

    ax.plot(x_values, y_values, color="black")

    # Display the correlation statistics
    ax.text(0.05, 0.925, f'r = {r_value:.2f}', transform=ax.transAxes, fontsize=16, fontname="Calibri")
    ax.text(0.05, 0.875, f'P = {p_value:.4f}', transform=ax.transAxes, fontsize=16, fontname="Calibri")
    ax.text(0.05, 0.825, f'y = {slope:.6f}x + {intercept:.2f}', transform=ax.transAxes, fontsize=16, fontname="Calibri")

    ax.set_xlabel("Number of Voxels", fontname="Calibri", fontsize=16, fontweight="bold")
    ax.set_ylabel("Time (s)", fontname="Calibri", fontsize=16, fontweight="bold")
    ax.set_title("Runtime vs Number of Voxels", fontname="Calibri", fontsize=18, fontweight="bold")

    for label in ax.get_yticklabels() + ax.get_xticklabels():
        label.set_fontname("Calibri")
        label.set_fontsize(16)

    plt.legend(prop={"family": "Calibri", "size": 14})
    plt.show()


def main():
    alg_table = accuracy.algorithm_output(c_s=0.2, verbose=True)
    times = [output["time"] for output in alg_table.values()]

    with open("../data/test/areas.csv", "r") as f:
        ground_truths = list(csv.DictReader(f))

    filename_name_map = {row["filename"]: row["PSD name"] for row in ground_truths}
    names = [filename_name_map[file] for file in alg_table.keys()]

    num_voxels = [output["voxels"] for output in alg_table.values()]

    plot_times(names, times)

    # Reorder the points so names are in numerical order
    sort_by = [int(name.split()[-1]) for name in names]

    times = [time for _, time in sorted(zip(sort_by, times))]
    num_voxels = [voxels for _, voxels in sorted(zip(sort_by, num_voxels))]
    names = [name for _, name in sorted(zip(sort_by, names))]

    plot_times_vs_voxels(names, times, num_voxels)


if __name__ == "__main__":
    main()
