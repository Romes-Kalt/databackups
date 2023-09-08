def rewrite_txt_file_utf8(fp: str = "./flight_data.csv", new_fp: str = None):
    with open(fp, "r", encoding="cp1252") as f:
        old_ = f.read().splitlines()
    if new_fp:
        with open(new_fp, "w", encoding="utf-8") as f:
            for _ in old_:
                f.write(f"{_}\n")
    else:
        with open(fp, "w", encoding="utf-8") as f:
            for _ in old_:
                f.write(f"{_}\n")


if __name__ == "__main__":
    rewrite_txt_file_utf8()
