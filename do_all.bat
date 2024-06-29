ask_continue() {
    while true; do
        read -p "Continue (y/n)? " yn
        case $yn in
            [Yy]* ) break;;  # If the user inputs 'y' or 'Y', proceed
            [Nn]* ) echo "Exiting..."; exit;;  # If the user inputs 'n' or 'N', exit the script
            * ) echo "Please answer yes or no.";;  # Any other input, prompt again
        esac
    done
}

python /c/Users/roman/Python/PyCharmProjects/BER_arr_dep/main.py
python "/c/Users/roman/Python/PyCharmProjects/daily scraping RKI ezyBER allBER/main.py"
ask_continue
cp /c/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_data.csv /c/Users/roman/Documents/GitHub/databackups/flight_data.csv
git fetch
git pull
python save_in_utf8.py
git add .
git commit -m "%DATE% %TIME% %1"
git push
echo "flight_data.csv zail -20"
tail -10 flight_data.csv
cat last_run.txt

