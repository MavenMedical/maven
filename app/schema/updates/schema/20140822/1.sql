create table audit (id serial primary key, datetime timestamp not null, username varchar not null, customer serial, patient varchar, action varchar not null, device varchar, details varchar, rows integer);

