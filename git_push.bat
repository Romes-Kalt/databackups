cp /c/Users/roman/Python/PyCharmProjects/BER_arr_dep/data/flight_data.csv /c/Users/roman/Documents/GitHub/databackups/flight_data.csv
git fetch
git pull
python save_in_utf8.py
git add .  
git commit -m "%DATE% %TIME% %1"
git push
echo "last_run.txt"
cat last_run.txt
