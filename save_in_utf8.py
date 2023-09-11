# all_codecs = ['ascii', 'big5', 'big5hkscs', 'cp037', 'cp273', 'cp424', 'cp437', 
# 'cp500', 'cp720', 'cp737', 'cp775', 'cp850', 'cp852', 'cp855', 'cp856', 'cp857', 
# 'cp858', 'cp860', 'cp861', 'cp862', 'cp863', 'cp864', 'cp865', 'cp866', 'cp869', 
# 'cp874', 'cp875', 'cp932', 'cp949', 'cp950', 'cp1006', 'cp1026', 'cp1125', 
# 'cp1140', 'cp1250', 'cp1251', 'cp1252', 'cp1253', 'cp1254', 'cp1255', 'cp1256', 
# 'cp1257', 'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213', 'euc_kr', 
# 'gb2312', 'gbk', 'gb18030', 'hz', 'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2', 
# 'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext', 'iso2022_kr', 'latin_1', 
# 'iso8859_2', 'iso8859_3', 'iso8859_4', 'iso8859_5', 'iso8859_6', 'iso8859_7', 
# 'iso8859_8', 'iso8859_9', 'iso8859_10', 'iso8859_11', 'iso8859_13', 
# 'iso8859_14', 'iso8859_15', 'iso8859_16', 'johab', 'koi8_r', 'koi8_t', 'koi8_u', 
# 'kz1048', 'mac_cyrillic', 'mac_greek', 'mac_iceland', 'mac_latin2', 'mac_roman', 
# 'mac_turkish', 'ptcp154', 'shift_jis', 'shift_jis_2004', 'shift_jisx0213', 
# 'utf_32', 'utf_32_be', 'utf_32_le', 'utf_16', 'utf_16_be', 'utf_16_le', 'utf_7', 
# 'utf_8', 'utf_8_sig']

"""Resave file to UTF-8 if necessary."""
from os import path
import datetime as dt


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


def count_words(
    filepath: str = "./flight_data.csv",
    what: str = "München",
    encoding: str = "UTF-8"
) -> int:
    """check, count how many what are in lines in file and check against target.

    Parameters
    ----------
    filepath : str, optional
        file to check, by default "./flight_data.csv"
    what : str, optional
        what to count, by default "München"
    encoding : str, optional
        encoding of file, by default "UTF-8"

    Returns
    -------
    int
        number of occurences, -1 if UnicodeDecodeError
    """
    try:
        with open(filepath, "r", encoding=encoding) as file:
            file_c = file.read().splitlines()
        count = 0
        for line in file_c:
            if what in line:
                count += 1
    except UnicodeDecodeError:
        print("UnicodeDecodeError")
        return -1
    return count 


def ran_today(today_: str = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d")) -> bool:
    """Check in ./last_run.txt, whether today's run completed

    Parameters
    ----------
    today_ : str, optional
        Date to check, defaults today, format YYYY-MM-DD
    
    Returns
    -------
    bool
        True if today is in ./last_run.txt
    """
    with open("last_run.txt", "r", encoding="utf-8") as file:
        x = file.read().split(",")[0]
        return today_ == x


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
        if count_words(what = "München", encoding="UTF-8") > 14_000:
            print(f"{filepath} is saved in UTF-8 and more than 14_000 München found.")
            return
        else:
            print("Encoding is UTF-8, but numbers pf München seems to be to low, please check with source")
            return
    print(f"{filepath} is saved in cp1252 - resaving in UTF-8 ", end="")
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
        print("complete.")
    with open("last_run.txt", "w", encoding="utf8") as file:
        num_of_muc =  count_words(what = "München", encoding="UTF-8")
        file.write(dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d" + "," + str(num_of_muc)))


def main():
    """Run main function"""
    today = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d")
    if ran_today(today_=today):
        num_of_muc = count_words(what = "München", encoding="UTF-8")
        print(f"UTF-8 check already run for {today} with {num_of_muc} flights to and fro München.")
    else:
        rewrite_txt_file_utf8()

if __name__ == "__main__":
    main()

