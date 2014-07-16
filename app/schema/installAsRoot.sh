su postgres -c "psql -f dropDb.sql" 
su postgres -c "psql -f createDb.sql"
cat createRulesDb.sql | sudo sudo -u postgres psql -d maven
cd data
./loadData.sh
cd ..
cat populateFakeData.sql | sudo sudo -u postgres psql -d maven
