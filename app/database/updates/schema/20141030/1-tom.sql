ALTER TABLE trees.activity ALTER node_id TYPE varchar(32) USING to_char(node_id, '99999999');
