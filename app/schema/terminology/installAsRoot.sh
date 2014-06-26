
sudo sudo -u postgres psql -f createTerminologyDb.sql
gzip DefaultProcedurePrices.csv
cat snomed/terminologySchema.data.gz | gzip -d | sudo sudo -u postgres psql -d maven
cat snomed/terminologySchema2.data.gz | gzip -d |  sudo sudo -u postgres psql -d maven



