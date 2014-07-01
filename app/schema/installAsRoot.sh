cat createDb.sql | sudo sudo -u postgres psql
cd data
./loadData.sh
cd ..
cat populateFakeData.sql | sudo sudo -u postgres psql -d maven
