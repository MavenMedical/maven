su postgres -c "psql -f dropDb.sql" 
su postgres -c "psql -f createDb.sql"
su postgres -c "psql -f categories/createSchema.sql"
cd public/
./installAsRoot.sh
cd ..
su postgres -c "psql -f trees/createSchema.sql"
cd choosewisely/
./installAsRoot.sh
cd ..
cd transparent/
./installAsRoot.sh