gunzip CostMapDefaults.csv.gz
su postgres -c "psql -f loadData.sql"
gzip CostMapDefaults.csv
source ~/.bash_profile
su postgres -c $PG_HOME'/bin/pg_restore -d maven --schema=rules rules.backup2'
su postgres -c "psql -f loadRules.sql"
