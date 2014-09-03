INSERT INTO layouts (layout_id, widget, template, element, priority) VALUES (3, 'customerList', 'customerList.html', 'contentRow', 2);
DELETE FROM layouts where widget='userList';
INSERT INTO layouts (layout_id, widget, template, element, priority) VALUES (2, 'userList', 'userScroll.html', 'contentRow', 2);
