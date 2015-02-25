PASSWORD=$1
DIR=`pwd`
su postgres -c "psql -f dropDb.sql" 
su postgres -c "psql -f createDb.sql -v pw=\'$PASSWORD\'"
su postgres -c "psql -f categories/createSchema.sql"
cd public/ && ./installAsRoot.sh
cd $DIR
su postgres -c "psql -f trees/createSchema.sql"
cd choosewisely/ && ./installAsRoot.sh
cd $DIR/transparent/ && ./installAsRoot.sh
cat pg_dump_terminology.gz | bzip2 -d | su postgres -c "psql maven"
