INSERT INTO user_pref
(SELECT customer_id, user_name, 'desktop', 'ehrinbox' from users);
