CREATE TABLE trees.canonical_protocol (
       canonical_id integer PRIMARY KEY,
       name varchar(128) NOT NULL,
       customer_id integer,
       enabled boolean NOT NULL DEFAULT FALSE,
       current_id integer NOT NULL,
       deleted boolean NOT NULL DEFAULT FALSE,
       parent_id integer,
       folder varchar(1024));
ALTER TABLE trees.canonical_protocol OWNER TO maven; 
CREATE INDEX customerprotocols ON trees.canonical_protocol (customer_id, deleted, folder);
CREATE INDEX customerprotocolspriority ON trees.canonical_protocol (customer_id, deleted);

ALTER TABLE trees.protocol 
      ADD COLUMN canonical_id integer NOT NULL DEFAULT -1,
      ADD COLUMN deleted boolean NOT NULL DEFAULT FALSE,
      ADD COLUMN creator integer,
      ADD COLUMN parent_id integer,
      ADD COLUMN tags varchar(1024),
      ADD COLUMN creation_time timestamp NOT NULL DEFAULT LOCALTIMESTAMP;
CREATE INDEX canonicalprotocol on trees.protocol (canonical_id, deleted, creation_time);
UPDATE trees.protocol SET canonical_id = protocol_id WHERE canonical_id < 0;
INSERT INTO trees.canonical_protocol (canonical_id, name, current_id) select protocol_id, name, protocol_id from trees.protocol;
ALTER TABLE trees.protocol ALTER canonical_id DROP DEFAULT;
ALTER TABLE trees.protocol DROP name;

