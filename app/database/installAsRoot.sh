PASSWORD=$1
DIR=`pwd`
su postgres -c "psql -f dropDb.sql" 
su postgres -c "psql -f createDb.sql"
su postgres -c "psql -f categories/createSchema.sql"
cd public/ && ./installAsRoot.sh -v pw=$PASSWORD
cd $DIR
su postgres -c "psql -f trees/createSchema.sql"
cd choosewisely/ && ./installAsRoot.sh
cd $DIR/transparent/ && ./installAsRoot.sh
