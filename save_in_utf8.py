"""Resave file to UTF-8 if necessary."""

def determine_encoding(filepath: str = "") -> str:
    """Return utf8 or cp1252 according to encoding of fp.

    Parameters
    ----------
    fp : str, optional
        filepath, by default ""

    Returns
    -------
    str :
        utf8 or cp1252
    """
    if not filepath:
        return "No file provided."
    if not path.exists(filepath):
        return f"{filepath} not found."
    for enc in ["utf8", "cp1252"]:
        try:
            with open(filepath, "r", encoding=enc) as file:
                file.read().splitlines()
            if enc == "utf8":
                return "utf8"
        except UnicodeDecodeError:
            continue
    return "cp1252"


def rewrite_txt_file_utf8(
    filepath: str = "./flight_data.csv", new_fp: str = ""
) -> None:
    """If a file is cp1252, resave it to utf8 for clean pushing to git.

    Parameters
    ----------
    fp : str, optional
        filepath to file, by default "./flight_data.csv"
    new_fp : str, optional
        specify if supposed to save tonew file, by default ""
    """
    if determine_encoding(filepath=filepath) == "utf8":
        print(f"{filepath} is saved in UTF-8.")
        return
    print(f"{filepath} is saved in cp1252 - resaving in UTF-8 ... to ", end="")
    with open(filepath, "r", encoding="cp1252") as file:
        old_ = file.read().splitlines()
    if new_fp:
        with open(new_fp, "w", encoding="utf-8") as file:
            for _ in old_:
                file.write(f"{_}\n")
        print(f"{new_fp} complete.")
    else:
        with open(filepath, "w", encoding="utf-8") as file:
            for _ in old_:
                file.write(f"{_}\n")
        print(f"{filepath} complete.")


if __name__ == "__main__":
    rewrite_txt_file_utf8()
