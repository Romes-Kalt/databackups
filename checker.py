with open("flight_data.csv", "r", encoding="cp1252") as file:
    c = file.read().splitlines()
print("flight_data.csv has", len(c), "lines.")
c_ = [_ for _ in c if "München" in _]
print("flight_data.csv has", len(c_), "occurences of München.")
