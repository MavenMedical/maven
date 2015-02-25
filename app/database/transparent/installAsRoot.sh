su postgres -c "psql -f createSchema.sql"
gunzip data/CostMapDefaults.csv.gz
gunzip data/OrderableDefaults.csv.gz
su postgres -c "psql -f data/loadData.sql"
gzip data/CostMapDefaults.csv
gzip data/OrderableDefaults.csv