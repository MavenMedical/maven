su postgres -c "psql -f dropDb.sql" 
su postgres -c "psql -f createDb.sql"
su postgres -c "psql -f categories/createSchema.sql"
su postgres -c "psql -f public/createSchema.sql"
su postgres -c "psql -f trees/createSchema.sql"
cd choosewisely
./installAsRoot.sh
cd ../transparent
./installAsRoot.sh