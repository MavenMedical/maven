gzip -d DefaultProcedurePrices.csv.gz
sudo sudo -u postgres psql -f createDb.sql
gzip DefaultProcedurePrices.csv
cat terminologySchema.data.gz | gzip -d | sudo sudo -u postgres psql -d maven 
cat terminologySchema2.data.gz | gzip -d |  sudo sudo -u postgres psql -d maven 



