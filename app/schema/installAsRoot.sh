cat createDb.sql | sudo sudo -u postgres psql
cat createRulesDb.sql | sudo sudo -u postgres psql -d maven
cd data
./loadData.sh
cd ..
cat populateFakeData.sql | sudo sudo -u postgres psql -d maven
