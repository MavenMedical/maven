read -p "Path to the rrf directory from RxNorm Download: " rrf
read -p "Path to the scripts directory from RxNorm Download: " scripts
su postgres -c 'psql -f drop.sql'
echo "\\connect maven;">/tmp/runnow.sql
echo "set search_path to terminology;">>/tmp.runnow.sql
cat $scripts/mysql/Table_scripts_mysql_rxn.sql >>/tmp/runnow.sql
perl -pi -e 's/ RXNCONSO/ terminology.RXNCONSO/' /tmp/runnow.sql
perl -pi -e 's/ RXNREL/ terminology.RXNREL/' /tmp/runnow.sql
perl -pi -e 's/ RXNSAT/ terminology.RXNSAT/' /tmp/runnow.sql
su postgres -c "psql -f /tmp/runnow.sql"
echo "\\connect maven;">/tmp/runnow.sql
echo "set search_path to terminology;">>/tmp.runnow.sql
cat $scripts/mysql/Indexes_mysql_rxn.sql >>/tmp/runnow.sql
perl -pi -e 's/ RXNCONSO/ terminology.RXNCONSO/' /tmp/runnow.sql
perl -pi -e 's/ RXNREL/ terminology.RXNREL/' /tmp/runnow.sql
perl -pi -e 's/ RXNSAT/ terminology.RXNSAT/' /tmp/runnow.sql
su postgres -c "psql -f /tmp/runnow.sql"
echo "\\connect maven;">/tmp/runnow.sql
echo "set search_path to terminology;">>/tmp.runnow.sql
echo " \\copy terminology.RXNCONSO from '$rrf/RXNCONSO.RRF' DELIMITER '|'  null as ''">>/tmp/runnow.sql
echo " \\copy terminology.RXNSAT from '$rrf/RXNSAT.RRF' DELIMITER '|'  null as ''">>/tmp/runnow.sql
echo " \\copy terminology.RXNREL from '$rrf/RXNREL.RRF' DELIMITER '|'  null as ''">>/tmp/runnow.sql
perl -pi -e 's/\|\n/\n/' $rrf/RXNCONSO.RRF 
perl -pi -e 's/\|\n/\n/' $rrf/RXNREL.RRF
perl -pi -e 's/\|\n/\n/' $rrf/RXNSAT.RRF
perl -pi -e 's/\\/\//' $rrf/RXNCONSO.RRF 
perl -pi -e 's/\\/\//' $rrf/RXNREL.RRF
perl -pi -e 's/\\/\//' $rrf/RXNSAT.RRF
#su postgres -c "psql -f addDummyCol.sql"
su postgres -c "psql -f /tmp/runnow.sql"
su postgres -c "psql -f prepDrugClassAPI.sql"
cd nadac
./importNADAC.sh
cd ../mdd
./importMDD.sh
