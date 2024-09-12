

def write_csv(csv_filepath: str, names: list[str], areas: list[float]):
    with open(csv_filepath, "w") as f:
        f.write("Name (object title or label),Surface Area (microns^2)\n")

        for name, area in zip(names, areas):
            f.write(f"{name},{area if area > 0 else 'Error calculating area'}\n")
