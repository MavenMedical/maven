wget http://www.epa.gov/ncct/dsstox/StructureDataFiles/FDAMDD_DownloadFiles/FDAMDD_v3b_1216_15Feb2008.zip
unzip FDAMDD*.zip
rm FDAMDD*.zip
python XL2CSV.py
rm *.xls*
rm *.sdf
rm *.pdf
perl -pi -e 's/\"\"//' MDD.csv
su postgres -c 'psql -f updateMDD.sql'
rm *.csv
