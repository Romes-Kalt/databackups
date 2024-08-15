# -*- coding: UTF-8 -*-
import datetime as dt
import selenium
from selenium import webdriver
from selenium import common
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
#         driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
import time
from flightdata import FlightData, IATAS_BY_COUNTRIES
from ch405_t00ls.ch405_tools import pretty_date, list_items_to_string
import codecs
import json
import random
from tqdm import tqdm

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def return_missing_dates():
    start_date = dt.date(2021, 6, 1)
    end_date = dt.datetime.now().date()
    delta = end_date - start_date   # returns timedelta
    all_d = []
    for _ in range(delta.days):
        this_day = start_date + dt.timedelta(days=_)
        all_d.append(dt.datetime.strftime(this_day, "%Y_%m_%d"))
    with codecs.open("C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_data.csv", encoding="latin1") as fi:
        these_lines = fi.readlines()
    dates_in_file = []
    for _ in these_lines[1:]:
        if _.split(",")[0] not in dates_in_file:
            dates_in_file.append(_.split(",")[0])
    missing_dates = [_ for _ in all_d if _ not in dates_in_file]
    if missing_dates:
        return f"Dates missing in between 1st of June 2021 and the yesterday: " \
               f"{list_items_to_string([pretty_date(_, 'YYYY_MM_DD') for _ in missing_dates], ending=' & ')}."
    else:
        return '\x1b[6;30;42m'+f"All dates in between 1st of June 2021 and yesterday " \
               f"({pretty_date(dt.datetime.strftime(dt.datetime.now() - dt.timedelta(1), '%Y_%m_%d'), 'YYYY_MM_DD')})" \
               f" are covered."+'\x1b[0m'


def num_of_flights_from_yesterday_json_project(this_date):
    with open("C:/Users/roman/Python/PyCharmProjects/DATA_BACKUPS/BERall_flights.json", "r", encoding="utf8") as f:
        data = json.load(f)
    try:
        return data[curr_date]["TOTAL"]
    except KeyError:
        return f"{curr_date} not found in keys of . C:/Users/roman/Python/PyCharmProjects/DATA_BACKUPS/BERall_flights.json"


def check_csv():
    """checks csv file for correct number of separators and incidences of ' ,', might hint to an error in CODESHARE"""
    with open("C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_data.csv", 'r') as fi:  # open as simple text file
        csv_lines = fi.read().splitlines()
    with open("C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/csv_checked_until_line.txt", "r") as fi:
        last_num_checked = int(fi.read())
    if last_num_checked == len(csv_lines):
        return print("no new data added, csv check is up to date")
    csv_lines_with_errors = []
    line_num = 0
    for line_num in range(last_num_checked, len(csv_lines)):
        if len(csv_lines[line_num].split(",")) != 13:
            csv_lines_with_errors.append((line_num + 1, "- separator error"))
        if " ," in csv_lines[line_num]:
            csv_lines_with_errors.append((line_num + 1, "- too many whitespaces"))
    if not csv_lines_with_errors:
        with open("C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/csv_checked_until_line.txt", "w") as fi:
            fi.write(str(line_num + 1))
        print('\x1b[6;30;42m'+"flight_data.csv file checked. No errors found."+'\x1b[0m')
    else:
        for error in csv_lines_with_errors:
            print(f"Line: {error[0]}, {error[1]}")


def iatas_without_country():
    """checks for all IATAs in .csv - file, whether all iata codes of destinations have a country assigned to them,
       returns list, if destination "is without" country, else None"""
    codes_w_country = []
    for v in IATAS_BY_COUNTRIES.values():
        codes_w_country += v

    if not len(codes_w_country) == len(set(codes_w_country)):
        print(f"Total codes ({len(codes_w_country)}) - codes with a country ({len(set(codes_w_country))}) = "
              f"{len(codes_w_country) - len(set(codes_w_country))}, please check for double assignment: ", end="")
        print([x for x in codes_w_country if codes_w_country.count(x) > 1])

    with open("C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_data.csv", 'r') as fi:  # open as simple text file
        lines = fi.read().splitlines()
    all_codes_in_flts = list()
    for line in lines:
        if line.split(",")[7] not in all_codes_in_flts:  # iata codes is in 8th position of every line
            all_codes_in_flts.append(line.split(",")[7])
    del (all_codes_in_flts[0])  # delete header entry of 8th position
    assigned = [c for c in all_codes_in_flts if c in codes_w_country]  # iatas with country
    not_assigned = [c for c in all_codes_in_flts if c not in codes_w_country]  # iatas without country

    if len(all_codes_in_flts) - len(assigned) == 0:
        return None
    else:
        return not_assigned


def date_to_ddmmyyyy(dat="1981_01_24", separator="."):
    """Takes the date in format YYYY_MM_DD from csv and transforms it into DD.MM.YYYY, separator default can be reset to
       different symbol, leading zeroes will be filled (1 -> 01)"""
    return f'{dat.split("_")[2]}{separator}{(str(int(dat.split("_")[1]))).zfill(2)}{separator}' \
           f'{(str(int(dat.split("_")[0]))).zfill(2)}'


def attach_cp_tofile_name(fp: str = "tester.txt", suffix: str = "_cp", incl_timestamp: bool = False):
    if incl_timestamp:
        suffix += dt.datetime.strftime(dt.datetime.now(), "_%Y-%m-%dT%H-%M-%S")
    return ".".join(fp.split(".")[:-1]) + suffix + "." + fp.split(".")[-1]


def rewrite_txt_file_utf8(fp: str = "C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_data.csv", new_fp: str = None):
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
    print(return_missing_dates())
    iatas_without_country()
    curr_date = (dt.datetime.now() - dt.timedelta(1)).strftime("%Y_%m_%d")
    # curr_date = "2024_05_31"   # FIX HERE
    curr_weekday = WEEKDAYS[dt.datetime.strptime(curr_date, "%Y_%m_%d").weekday()]
    # with open("C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_test.csv", 'r') as f:   # for testing purposes
    with open("C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_data.csv", 'r') as file:
        lines = file.read().splitlines()
        last_line = lines[-1]
    last_date = last_line.split(",")[0]

    if curr_date == last_date:
        print(f"Flight data for the "
              f"{pretty_date((dt.datetime.now() - dt.timedelta(1)).strftime('%d.%m.%Y'))} has already been saved "
              f"to flight_data.csv, please check file.")
    else:
        if last_date == (dt.datetime.now() - dt.timedelta(2)).strftime('%Y_%m_%d'):
            print('\x1b[6;30;42m' + f"Last date in flight_data.csv: "
                                    f"{pretty_date(last_date, date_pattern='YYYY_MM_DD')} (should be "
                  f"{(dt.datetime.now() - dt.timedelta(2)).strftime('%d.%m.%Y')}, otherwise update manually).\n"
                  f"Collecting data for the "
                  f"{pretty_date((dt.datetime.now() - dt.timedelta(1)).strftime('%d.%m.%Y'))}.\n" + '\x1b[0m')
        else:
            print(last_date)
            '''amend_date = dt.datetime.strftime(dt.datetime.strptime(last_date, "%Y_%m_%d"))
            print(
                '\x1b[0;37;41m' + f"Last date in flight_data.csv: {pretty_date(last_date, date_pattern='YYYY_MM_DD')} "
                                  f"(should be "
                                  f"{(dt.datetime.now() - dt.timedelta(2)).strftime('%d.%m.%Y')}, "
                                  f"otherwise update manually).\nCollecting data for the "
                                  f"{pretty_date((dt.datetime.now() - dt.timedelta(1)).strftime('%d.%m.%Y'))}.\n"
                + '\x1b[0m')'''

        # chrome_driver_path = "C:/Users/roman/Python/chromedriver/chromedriver_win32/chromedriver.exe"
        # chrome_driver_path = "C:/Users/roman/Python/chromedriver/chrome - win32/chrome.exe"
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # driver = webdriver.Chrome(executable_path=chrome_driver_path)

        #   ################
        #   ## DEPARTURES ##
        #   ################

        driver.get("https://ber.berlin-airport.de/de/fliegen/abfluege-ankuenfte.html")

        # Cookie window
        time.sleep(random.randint(4, 9))
        cook_wind = driver.find_elements("id", "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        time.sleep(random.randint(4, 9))
        if cook_wind:
            cook_wind[0].click()

        # Select previous day
        # input("ÄÄÄÄÄ")
        # driver.find_element_by_xpath("//div[@class='flightlist parbase aem-GridColumn aem-GridColumn--default--12']")
        time.sleep(random.randint(4, 9))
        driver.execute_script("window.scrollTo(0, 150)")
        time.sleep(random.randint(4, 9))
        driver.find_element("class name",  "previous").click()
        time.sleep(random.randint(4, 9))
        driver.find_element("class name",  "flight-search__button").click()
        time.sleep(random.randint(4, 9))

        # press "load more" until all flights are on one page
        # more_flights = True
        # while more_flights:
        #     time.sleep(random.randint(4, 9))
        #     try:
        #         if len(driver.find_elements("class name",  "cmp-flightlist__action-link")) > '0:
        #             driver.find_element("class name",  "cmp-flightlist__action-link").click()'
        #         # if len(driver.find_elements_by_xpath("/html/body/div[3]/div/div/div/div[7]/div[1]/a")) > 0:
        #         #     driver.find_element_by_xpath("/html/body/div[3]/div/div/div/div[7]/div[1]/a").click()
        #     except selenium.common.exceptions.ElementNotInteractableException:
        #         more_flights = False
        print("Loading page .", end="")
        more_flights = True
        while more_flights:
            time.sleep(1)
            try:
                if len(driver.find_elements("class name",  "cmp-flightlist__action-link")) >= 1:
                    butt = driver.find_element("class name",  "cmp-flightlist__action-link")
                    driver.execute_script("arguments[0].click();", butt)
                    time.sleep(3 + 2 * random.random())
                    if driver.find_elements("class name",  "cmp-flightlist__action-link.hide"):
                        print(" done")
                        more_flights = False
                    else:
                        print(".", end="")
            except selenium.common.exceptions.ElementNotInteractableException:
                more_flights = False
        # when all flights were loaded, create six lists with all relevant information
        dep_schedl_times = driver.find_elements("class name",  "cmp-flightlist__list__items__item--col.planned")
        dep_actual_times = driver.find_elements("class name",  "expected")
        destinations = driver.find_elements("class name",  "airport")
        flight_nums = driver.find_elements("class name",  "mainflight")
        flight_infos = driver.find_elements("class name",  "info")
        flight_status = driver.find_elements("class name",  "flight-status")

        # create updated status list pulled data
        flight_status_corrected = []
        for _ in range(0, len(flight_status)):
            if flight_status[_].text in ["Gestartet", "Planmäßig", "Ende Abfertigung", "Ende Einstieg", "Abfertigung"]:
                flight_status_corrected.append("departed")
            elif flight_status[_].text == "Gestrichen":
                flight_status_corrected.append("cancelled")

        # create updated list with on time / delayed information
        dep_actual_corr = []
        for _ in range(0, len(dep_actual_times)):
            if dep_actual_times[_].text == "":
                if flight_status_corrected[_] != "cancelled":
                    dep_actual_corr.append("on time")
                else:
                    dep_actual_corr.append(" --:-- Uhr")
            else:
                dep_actual_corr.append(dep_actual_times[_].text)

        # create list of airline operating
        airlines = []
        for _ in range(len(flight_infos)):
            airlines.append(flight_infos[_].text.split(" | ")[1])

        # create list of code shares (if applicable)
        codeshare = []
        for _ in range(len(flight_infos)):
            codes = flight_infos[_].text.replace(",", "").split(" | ")[0][3:]  # cut first 3 char's (airline code)
            # codes = codes.split(" ")[1:]                        # remove first (=MAIN)flight number
            if codes[0] == " ":  # catch 3 letter airline code with 3 digit flightnum
                codes = codes.split(" ")[2:]  # remove first (=MAIN)flight number
            else:
                codes = codes.split(" ")[1:]  # remove first (=MAIN)flight number
            these_codes = ""
            # if codes:
            #     for i in range(0, len(codes)-1, 2):
            #         these_codes += f"{codes[i]}_{codes[i+1][:-1]} "
            #     these_codes = these_codes[:-2]
            if codes:
                for i in range(0, len(codes) - 1, 2):
                    these_codes += f"{codes[i]}{codes[i + 1]} "
                these_codes = these_codes[:-1]
            else:
                these_codes = "---"
            codeshare.append(these_codes)

        # curr_date = (dt.datetime.now() - dt.timedelta(1)).strftime("%Y_%m_%d")
        # curr_weekday = WEEKDAYS[dt.datetime.strptime(curr_date, "%Y_%m_%d").weekday()]
        # # UNCOMMENT AND CHANGE FOR MANUALLY ADDING DATA
        # curr_date = "2022_09_07"
        # curr_weekday = "Wed"
        print(f"Number of departures recorded {curr_date} in json-project: "
              f"{num_of_flights_from_yesterday_json_project(curr_date)}.")
        # if int(num_of_flights_from_yesterday_json_project(curr_date) != len(flight_nums)): # TODO remove after testing
        if abs(int(num_of_flights_from_yesterday_json_project(curr_date))-len(flight_nums)) > len(flight_nums) * 0.025:
            input(f"Discrepancy between total numbers of both projects: "
                  f"{100 - round(abs(int(num_of_flights_from_yesterday_json_project(curr_date)))*100 / len(flight_nums), 3)}"
                  f" % ({num_of_flights_from_yesterday_json_project(curr_date)} : {len(flight_nums)}). "
                  f"Hit return to continue or terminate program.")
        print(f"Creating {len(flight_nums)} departures as FlightData objects: ")
        # DEParture: create list of FlightData objects combing all pulled data
        flights = []
        # for _ in range(0, len(dep_actual_times)):
        for _ in tqdm(range(0, len(dep_actual_times)), colour="cyan"):
            # if _ % 10 == 0:
            #     print(".", end="")
            flight = FlightData()
            flight.flight_date = curr_date
            # flight.flight_id = (dt.datetime.now() - dt.timedelta(1)).strftime("%Y%m%d")+flight_nums[_].text
            flight.flight_id = curr_date.replace("_", "") + flight_nums[_].text
            flight.dep_arr = "DEP"
            flight.flight_num = flight_nums[_].text
            flight.departure = dep_schedl_times[_].text
            flight.status = flight_status_corrected[_]
            flight.actual_time = dep_actual_corr[_]
            flight.dest_iata = destinations[_].text.split("(")[1].split(")")[0] # destinations[_].text[-3:] # version before 2022_12_21
            # flight.airline_code = airlines[_].split('(')[1][:-1] , is working except for Smartwings (Czechia) (QS) -> "(" used within airline text from website
            flight.airline_code = airlines[_].split('(')[-1][:-1]  # therefore changed to this
            # flight.destination = destinations[_].text[:-4]
            flight.destination = destinations[_].text.split(" (")[0].replace(",", "")  # some airports have a comma in the name
            # flight.airline = airlines[_].split(' (')[0]
            flight.airline = airlines[_].split(' (')[0].replace(",", ".")    # some airlines have a comma in the name
            flight.codeshare = codeshare[_]
            flight.weekday = curr_weekday
            flights.append(flight)

        driver.quit()
        time.sleep(5)

        #   ##############
        #   ## ARRIVALS ##
        #   ##############
        # driver = webdriver.Chrome(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get("https://ber.berlin-airport.de/de/fliegen/abfluege-ankuenfte.html")
        time.sleep(random.randint(4, 9))

        # Select previous day and Arrivals
        # input("ÄÄÄÄÄ")
        # driver.find_element_by_xpath("//div[@class='flightlist parbase aem-GridColumn aem-GridColumn--default--12']")
        cook_wind = driver.find_elements("id", "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        time.sleep(random.randint(4, 9))
        if cook_wind:
            cook_wind[0].click()
        time.sleep(random.randint(4, 9))
        driver.execute_script("window.scrollTo(0, 150)")
        time.sleep(random.randint(4, 9))
        driver.find_element("class name",  "previous").click()

        time.sleep(random.randint(4, 9))

        driver.find_element("class name",  "icon--arrival").click()

        time.sleep(random.randint(4, 9))
        driver.find_element("class name",  "flight-search__button").click()
        time.sleep(random.randint(4, 9))

        # press "load more" until all flights are on one page
        # more_flights = True
        # while more_flights:
        #     time.sleep(random.randint(2,4))
        #     try:
        #         if len(driver.find_elements("class name",  "cmp-flightlist__action-link")) > 0:
        #             driver.find_element("class name",  "cmp-flightlist__action-link").click()
        #     except selenium.common.exceptions.ElementNotInteractableException:
        #         more_flights = False
        #     except selenium.common.exceptions.ElementClickInterceptedException:
        #         more_flights = False
        # input("No More Flights?)")
        print("Loading page .", end="")
        more_flights = True
        while more_flights:
            time.sleep(1)
            try:
                if len(driver.find_elements("class name",  "cmp-flightlist__action-link")) >= 1:
                    butt = driver.find_element("class name",  "cmp-flightlist__action-link")
                    driver.execute_script("arguments[0].click();", butt)
                    time.sleep(3 + 2 * random.random())
                    if driver.find_elements("class name",  "cmp-flightlist__action-link.hide"):
                        print(" done")
                        more_flights = False
                    else:
                        print(".", end="")
            except selenium.common.exceptions.ElementNotInteractableException:
                more_flights = False
        # when all flights were loaded, create six lists with all relevant information
        dep_schedl_times = driver.find_elements("class name",  "cmp-flightlist__list__items__item--col.planned")
        dep_actual_times = driver.find_elements("class name",  "expected")
        destinations = driver.find_elements("class name",  "airport")
        flight_nums = driver.find_elements("class name",  "mainflight")
        flight_infos = driver.find_elements("class name",  "info")
        flight_status = driver.find_elements("class name",  "flight-status")

        # create updated status list of pulled data
        flight_status_corrected = []
        for _ in range(0, len(flight_status)):
            if flight_status[_].text in ["Gelandet", "Planmäßig", "Ende Ausstieg", "Ausstieg"]:
                flight_status_corrected.append("arrived")
            elif flight_status[_].text == "Gestrichen":
                flight_status_corrected.append("cancelled")
            elif flight_status[_].text == "Umgeleitet":
                flight_status_corrected.append("diverted")

        # create updated list with on time / delayed information
        dep_actual_corr = []
        for _ in range(0, len(dep_actual_times)):
            if dep_actual_times[_].text == "":
                if flight_status_corrected[_] not in ["cancelled", "diverted"]:
                    dep_actual_corr.append("on time")
                else:
                    dep_actual_corr.append(" --:-- Uhr")
            else:
                dep_actual_corr.append(dep_actual_times[_].text)

        # create list of airline operating
        airlines = []
        for _ in range(len(flight_infos)):
            airlines.append(flight_infos[_].text.split(" | ")[1])

        # create list of code shares (if applicable)
        codeshare = []
        for _ in range(len(flight_infos)):
            codes = flight_infos[_].text.replace(",", "").split(" | ")[0][3:]  # cut first 3 char's (airline code)
            # codes = codes.split(" ")[1:]                        # remove first (=MAIN)flight number
            if codes:
                if codes[0] == " ":  # catch 3 letter airline code with 3 digit flightnum
                    codes = codes.split(" ")[2:]  # remove first (=MAIN)flight number
                else:
                    codes = codes.split(" ")[1:]  # remove first (=MAIN)flight number
                these_codes = ""
                # if codes:
                #     for i in range(0, len(codes)-1, 2):
                #         these_codes += f"{codes[i]}_{codes[i+1][:-1]} "
                #     these_codes = these_codes[:-2]
                if codes:
                    for i in range(0, len(codes) - 1, 2):
                        these_codes += f"{codes[i]}{codes[i + 1]} "
                    these_codes = these_codes[:-1]
                else:
                    these_codes = "---"

        # for _ in range(len(flight_infos)):
        #     codes = flight_infos[_].text.split(" | ")[0][3:]    # cut first 3 char's to cope for EZY1234 w/o spacing
        #     if codes[0] == " ":  # catch 3 letter airline code with 3 digit flightnum
        #         codes = codes.split(" ")[2:]  # remove first (=MAIN)flight number
        #     else:
        #         codes = codes.split(" ")[1:]  # remove first (=MAIN)flight number
        #     # codes = codes.split(" ")[1:]                        # remove first (=MAIN)flight number
        #     these_codes = ""
        #     if codes:
        #         for i in range(0, len(codes)-1, 2):
        #             these_codes += f"{codes[i]}_{codes[i+1]} "
        #         # these_codes = these_codes[:-1]
        #     else:
        #         these_codes = "---"
                codeshare.append(these_codes)
            else:   # catches no flightnum provided
                print("Incorrect data on website:", flight_infos[_].text, dep_actual_times[_].text)
                codeshare.append("ERROR,ERROR")  # insert additional error two create error for csv-check
        # ARRivals: create list of FlightData objects combing all pulled data
        print(f"Creating {len(flight_nums)} arrivals as FlightData objects... ")
        # for _ in range(0, len(dep_actual_times)):
        #     if _ % 10 == 0:
        #         print(".", end="")
        for _ in tqdm(range(0, len(dep_actual_times)), colour="cyan"):
            flight = FlightData()
            flight.flight_date = curr_date
            # flight.flight_id = (dt.datetime.now() - dt.timedelta(1)).strftime("%Y%m%d")+flight_nums[_].text
            flight.flight_id = curr_date.replace("_", "") + flight_nums[_].text
            flight.dep_arr = "ARR"
            flight.flight_num = flight_nums[_].text
            flight.departure = dep_schedl_times[_].text
            flight.status = flight_status_corrected[_]
            flight.actual_time = dep_actual_corr[_]
            flight.dest_iata = destinations[_].text.split("(")[1].split(")")[0]  # olde version destinations[_].text[-3:]
            # flight.airline_code = airlines[_].split('(')[1][:-1] , is working except for Smartwings (Czechia) (QS) -> "(" used within airline text from website
            flight.airline_code = airlines[_].split('(')[-1][:-1]  # therefore changed to this
            flight.destination = destinations[_].text.split(" (")[0].replace(",", "")  # some airports have a comma in the name # old version flight.destination = destinations[_].text[:-4].replace(",", "")  # some airports have a comma in the name
            # flight.airline = airlines[_].split(' (')[0]
            flight.airline = airlines[_].split(' (')[0].replace(",", ".")    # some airlines have a comma in the name
            flight.codeshare = codeshare[_]
            flight.weekday = curr_weekday
            flights.append(flight)

        for f in flights:
            csv_line = f"{f.flight_date},{f.flight_id},{f.dep_arr},{f.flight_num},{f.departure},{f.status}," \
                       f"{f.actual_time},{f.dest_iata},{f.airline_code},{f.destination},{f.airline},{f.codeshare}," \
                       f"{f.weekday}\n"
            # with open("C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_test.csv", "a+") as file:
            #     file.write(csv_line)
            with open("C:/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_data.csv", "a+", encoding="utf8") as file:
                file.write(csv_line)
            with open("C:/Users/Roman/Documents/flight_data.csv", "a+", encoding="utf-8") as file:
                file.write(csv_line)
            with open("C:/Users/roman/Python/PyCharmProjects/DATA_BACKUPS/flight_data.csv", "a+",
                      encoding="utf-8") as file:
                file.write(csv_line)
            with open("C:/Users/roman/Documents/GitHub/databackups/flight_data.csv", "a+",
                      encoding="utf8") as file:
                      # encoding="utf-8") as file:
                file.write(csv_line)                    # for github

        print(f"csv data updated for the {pretty_date(date_to_ddmmyyyy(curr_date))}.")
        driver.quit()

        # rewrite_txt_file_utf8()
        # rewrite_txt_file_utf8(fp="C:/Users/roman/Documents/GitHub/databackups/flight_data.csv")

        check_csv()

        print(return_missing_dates())

        if dt.datetime.today().strftime("%A") in ["Saturday", "Sunday"]:
            not_assigned_codes = iatas_without_country()
            if not_assigned_codes:
                print(f"The following Airport Codes do not have a country assigned: {not_assigned_codes[0]}", end="")
                if len(not_assigned_codes) > 1:
                    for _ in not_assigned_codes[1:]:
                        print(f", {_}", end="")
                print(".")
            else:
                print("Weekend check of airport codes done, all airports are assigned to a country in the "
                      "IATAS_BY_COUNTRIES dictionary.")

# c:\Users\roman\Documents\GitHub\databackups\git_push.bat
