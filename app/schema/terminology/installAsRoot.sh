sudo sudo -u postgres psql maven -f createTerminologyDb.sql
cat snomed/terminologySchema.data.gz | gzip -d | sudo sudo -u postgres psql -d maven
cat snomed/terminologySchema2.data.gz | gzip -d |  sudo sudo -u postgres psql -d maven



