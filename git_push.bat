git add *.json  
git commit -m "%DATE% %TIME% %1"
git push && echo "JSONs pushed"
git config --global i18n.commitEncoding cp1252
git add *.csv  
git commit -m "%DATE% %TIME% %1"
git push && echo "csv pushed"
git config --global i18n.commitEncoding utf8

