wget http://www.medicaid.gov/Medicaid-CHIP-Program-Information/By-Topics/Benefits/Prescription-Drugs/FUL-NADAC-Downloads/xxxGoLive-NADAC-WeeklyFiles.zip
unzip xxxGoLive*.zip
rm xxx*.zip
python XL2CSV.py
rm *.xls*
perl -pi -e 's/\"\"//' NADAC.csv
su postgres -c 'psql -f updateNadac.sql'
#rm *.csv
