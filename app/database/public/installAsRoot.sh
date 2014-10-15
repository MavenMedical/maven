su postgres -c "psql -f createSchema.sql"
su postgres -c "psql -f data/loadData.sql"