mkdir tmp
cp *.sql tmp
cd tmp
wget https://iu.box.com/shared/static/in8m28mq9urdwyzr141l.zip -O loinc.zip
unzip loinc.zip
sed '1d' loinc.csv>loinc2.csv
sed '1d' source_organization.csv>source_organization2.csv
sed '1d' map_to.csv>map_to2.csv
su postgres -c 'psql -f import.sql'
cd ..
rm -rf tmp
