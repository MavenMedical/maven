su postgres -c "psql -f dropDb.sql" 
su postgres -c "psql -f createDb.sql"
su postgres -c "psql -f categories/createSchema.sql"
./public/installAsRoot.sh
su postgres -c "psql -f trees/createSchema.sql"
./choosewisely/installAsRoot.sh
./transparent/installAsRoot.sh