cat createDb.sql | sudo sudo -u postgres psql
gzip DefaultProcedurePrices.csv
cat terminologySchema.data.gz | gzip -d | sudo sudo -u postgres psql -d maven 
cat terminologySchema2.data.gz | gzip -d |  sudo sudo -u postgres psql -d maven 



