CREATE TYPE user_role AS ENUM ('provider', 'supervisor', 'mavensupport');

alter table users add roles user_role[];
