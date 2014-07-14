cat dropDb.sql | sudo sudo -u postgres psql -d maven
cat createDb.sql | sudo sudo -u postgres psql -d maven
cat createRulesDb.sql | sudo sudo -u postgres psql -d maven
cd data
./loadData.sh
cd ..
cat populateFakeData.sql | sudo sudo -u postgres psql -d maven
