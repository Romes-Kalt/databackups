def is_binary(filename):
    """ 
    Return true if the given filename appears to be binary.
    File is considered to be binary if it contains a NULL byte.
    FIXME: This approach incorrectly reports UTF-16 as binary.
    """
    with open(filename, 'rb') as f:
        for block in f:
            if b'\0' in block:
                return True
    return False


def main():
    print(is_binary("flight_data.csv"))

    with open("flight_data.csv.bk", "rb") as f:
        data = f.read().splitlines()

    data_ = [_.decode('latin-1') for _ in data]

    for _ in data_[:50]:
        print(_)


if __name__ == "__main__":
    main()
