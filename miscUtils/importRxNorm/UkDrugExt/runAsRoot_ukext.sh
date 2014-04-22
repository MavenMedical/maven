sed 1d $1/sct1_Concept*.txt >Concept.tmp
sed 1d $1/sct1_Des*.txt>Desc.tmp
sed 1d $1/sct1_Rel*.txt>Rel.tmp
su postgres -c 'psql -f import_ukext.sql'
rm Concept.tmp
rm Desc.tmp
rm Rel.tmp
