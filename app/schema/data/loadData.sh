su postgres -c "psql -f loadData.sql"
su postgres -c "/usr/pgsql-9.3/bin/pg_restore -d maven --schema=rules rules.backup2"
su postgres -c "psql -f loadRules.sql"
