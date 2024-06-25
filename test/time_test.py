import matplotlib.pyplot as plt
import numpy as np

import accuracy


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

    # Create a color map
    colors = plt.cm.rainbow(np.linspace(0, 1, len(name)))

    # Add the name of the file to each point and color-code the points
    for i, txt in enumerate(name):
        ax.scatter(num_voxels[i], times[i], color=colors[i], label=txt)

    # Fit a line to the data
    coefficients = np.polyfit(num_voxels, times, 1)
    polynomial = np.poly1d(coefficients)
    xs = np.linspace(min(num_voxels), max(num_voxels), 1000)
    ys = polynomial(xs)

    # Plot the line of best fit
    ax.plot(xs, ys, color='red')

    # Calculate the R-squared value
    correlation_matrix = np.corrcoef(num_voxels, times)
    correlation_xy = correlation_matrix[0, 1]
    r_squared = correlation_xy**2

    # Display the correlation statistics
    ax.text(0.05, 0.925, f'R² = {r_squared:.2f}', transform=ax.transAxes, fontsize=12)
    ax.text(0.05, 0.875, f'y = {coefficients[0]:.2f}x + {coefficients[1]:.2f}', transform=ax.transAxes, fontsize=12)

    ax.set_xlabel("Number of Voxels")
    ax.set_ylabel("Time (s)")
    ax.set_title("Runtime vs Number of Voxels")

    plt.legend()
    plt.show()


def main():
    alg_table = accuracy.algorithm_output(c_s=0.2, verbose=True)
    times = [output["time"] for output in alg_table.values()]
    names = [file[:-len(".npy")] for file in alg_table]
    num_voxels = [output["voxels"] for output in alg_table.values()]

    plot_times(names, times)
    plot_times_vs_voxels(names, times, num_voxels)


if __name__ == "__main__":
    main()
