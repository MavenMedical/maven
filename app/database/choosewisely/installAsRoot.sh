gunzip data/loadSchema.sql.gz
su postgres -c "psql -f data/loadSchema.sql"
gzip data/loadSchema.sql