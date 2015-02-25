sudo sudo -u postgres psql maven -f createSchema.sql
cat snomed/terminologySchema.data.gz | gzip -d | sudo sudo -u postgres psql -d maven
cat snomed/terminologySchema2.data.gz | gzip -d |  sudo sudo -u postgres psql -d maven