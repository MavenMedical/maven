CREATE SEQUENCE protocol_id_seq MINVALUE 1000;
ALTER TABLE trees.protocol ALTER protocol_id SET DEFAULT nextval('protocol_id_seq');
CREATE SEQUENCE canonical_protocol_id_seq MINVALUE 1000;
ALTER TABLE trees.canonical_protocol ALTER canonical_id SET DEFAULT nextval('canonical_protocol_id_seq');
UPDATE trees.canonical_protocol AS c SET customer_id = (SELECT p.customer_id FROM trees.protocol AS p WHERE p.protocol_id = c.current_id);
