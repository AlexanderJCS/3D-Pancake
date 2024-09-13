

def write_csv(csv_filepath: str, names: list[str], areas: list[float]) -> None:
    """
    Writes the names and surface ares of the PSDs to a CSV file.
    
    :param csv_filepath: The path to the CSV file
    :param names: A list of the names of the PSDs
    :param areas: A list of the surface areas of the PSDs. Must be the same length as names. Any area <= 0 will show an
                    error message in the CSV file.
    """
    
    with open(csv_filepath, "w") as f:
        f.write("Name (object title or label),Surface Area (microns^2)\n")

        for name, area in zip(names, areas):
            f.write(f"{name},{area if area > 0 else 'Error calculating area'}\n")
