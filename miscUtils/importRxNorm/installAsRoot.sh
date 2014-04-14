read -p "Path to the rrf directory from RxNorm Download: " rrf
read -p "Path to the scripts directory from RxNorm Download: " scripts
su postgres -c 'psql -f drop.sql'
echo "\\connect maven;">/tmp/runnow.sql
cat $scripts/mysql/Table_scripts_mysql_rxn.sql >>/tmp/runnow.sql
su postgres -c "psql -f /tmp/runnow.sql"
echo "\\connect maven;">/tmp/runnow.sql
cat $scripts/mysql/Indexes_mysql_rxn.sql >>/tmp/runnow.sql
su postgres -c "psql -f /tmp/runnow.sql"
echo "\\connect maven;">/tmp/runnow.sql
echo " \\copy RXNCONSO from '$rrf/RXNCONSO.RRF' DELIMITER '|'  null as '' CSV">>/tmp/runnow.sql
echo " \\copy RXNSAT from '$rrf/RXNSAT.RRF' DELIMITER '|'  null as '' CSV">>/tmp/runnow.sql
echo " \\copy RXNREL from '$rrf/RXNREL.RRF' DELIMITER '|'  null as '' CSV">>/tmp/runnow.sql
perl -pi -e 's/\|\n/\n/' $rrf/RXNCONSO.RRF 
perl -pi -e 's/\|\n/\n/' $rrf/RXNREL.RRF
perl -pi -e 's/\|\n/\n/' $rrf/RXNSAT.RRF
su postgres -c "psql -f /tmp/runnow.sql"

