CREATE TEXT SEARCH DICTIONARY maven (
    TEMPLATE = pg_catalog.simple,
    STOPWORDS = english
);

CREATE TEXT SEARCH CONFIGURATION maven ( COPY = pg_catalog.english );

alter text search configuration maven ALTER MAPPING FOR asciiword with maven;

create index ftixTermDescMavenDict on terminology.descriptions using gin(to_tsvector('maven',term));