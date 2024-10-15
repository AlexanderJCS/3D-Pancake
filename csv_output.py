
def write_csv(csv_filepath: str, columns: dict[str, list]) -> None:
    """
    Writes the names and surface ares of the PSDs to a CSV file.
    
    :param csv_filepath: The path to the CSV file
    :param columns: Key: the column name, Value: the column data
    """

    with open(csv_filepath, "w") as f:
        column_headers = list(columns.keys())
        f.write(",".join(column_headers) + "\n")

        rows = zip(*columns.values())
        for row in rows:
            row = [str(item) for item in row]  # to play nicely with .join()
            f.write(",".join(row) + "\n")
