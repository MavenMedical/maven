read -p "Restore general data? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo making a backup first, enter a password for this backup
    pg_dump -U postgres maven --clean -N terminology -N transparent | gzip | openssl aes-256-cbc -a -salt > pg_dump_general_overwritten.gz 
    echo restoring general data
    cat pg_dump_general.gz | openssl aes-256-cbc -d -a | gzip -d | psql -U postgres maven
else
    echo not restoring general data
fi 

read -p "Restore transparent data? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo restoring transparent data
    cat pg_dump_transparent.gz | openssl aes-256-cbc -d -a | gzip -d | psql -U postgres maven
else
    echo not restoring transparent data
fi 

read -p "Restore terminology data? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo restoring terminology data
    cat pg_dump_terminology.gz | openssl aes-256-cbc -d -a | gzip -d | psql -U postgres maven
else
    echo not restoring terminology data
fi 
