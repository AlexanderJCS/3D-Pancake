"""
Converts a binary tif file (with multiple layers) into a .npy file that can be parsed by quick_run.py or
any of the tests in the test/ directory.
"""

import numpy as np
from skimage import io


def tif_to_npy(tif_path: str, output_path: str) -> None:
    """
    Converts a binary tif file (with multiple layers) into a .npy file that can be parsed by quick_run.py or
    any of the tests in the test/ directory.

    :param tif_path: The path to the tif file
    :param output_path: The path to the output .npy file
    """

    tif = io.imread(tif_path)
    tif = tif.astype(bool)
    np.save(output_path, tif)


def main():
    tif_to_npy("../data/binary_tifs/10/PSD01.tif", "../data/test/10as100n1.npy")
    tif_to_npy("../data/binary_tifs/10/PSD05.tif", "../data/test/10as111n2.npy")
    tif_to_npy("../data/binary_tifs/10/PSD04.tif", "../data/test/10as071n3.npy")
    tif_to_npy("../data/binary_tifs/10/PSD02.tif", "../data/test/10as086n4.npy")
    tif_to_npy("../data/binary_tifs/10/PSD03.tif", "../data/test/10as065n5.npy")

    tif_to_npy("../data/binary_tifs/23/PSD04.tif", "../data/test/23as020p1.npy")
    tif_to_npy("../data/binary_tifs/23/PSD02.tif", "../data/test/23as076p2.npy")
    tif_to_npy("../data/binary_tifs/23/PSD03.tif", "../data/test/23as053p3.npy")
    tif_to_npy("../data/binary_tifs/23/PSD01.tif", "../data/test/23as065p4.npy")


if __name__ == "__main__":
    main()
