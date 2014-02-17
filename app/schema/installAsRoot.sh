chmod 777 .
su postgres -c 'psql -f createDb.sql'
mkfifo termData
gunzip < terminologySchema.data.gz > termData &
chmod 777 termData
su postgres -c 'psql -d maven -f termData'
rm termData
mkfifo termData
gunzip < terminologySchema2.data.gz > termData &
chmod 777 termData
su postgres -c 'psql -d maven -f termData'
rm termData

