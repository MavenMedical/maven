pg_dump --clean -U postgres maven -N terminology -N transparent | gzip | openssl aes-256-cbc -a -salt > pg_dump_general.gz
pg_dump --clean -U postgres maven -n terminology | gzip | openssl aes-256-cbc -a -salt > pg_dump_terminology.gz
pg_dump --clean -U postgres maven -n transparent | gzip | openssl aes-256-cbc -a -salt > pg_dump_transparent.gz

