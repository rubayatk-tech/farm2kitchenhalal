INSERT INTO "user" (zelle_name, phone) VALUES ('Rachel Black', '5504321141');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '5504321141'), 'Full Goat: 1', 450.0, 'Pending', 'regular');

INSERT INTO "user" (zelle_name, phone) VALUES ('Jessica Rivera', '0085652722');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '0085652722'), 'Full Goat: 2', 900.0, 'Pending', 'regular');

INSERT INTO "user" (zelle_name, phone) VALUES ('Derek Diaz', '6502353579');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '6502353579'), 'Full Goat: 2', 900.0, 'Pending', 'regular');

INSERT INTO "user" (zelle_name, phone) VALUES ('Jennifer Matthews', '9837379755');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '9837379755'), 'Cow Size 2 (Small) - 1/7 Share: 2', 571.42, 'Pending', 'regular');

INSERT INTO "user" (zelle_name, phone) VALUES ('Mark Robertson', '0261697303');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '0261697303'), 'Cow Size 1 (Large) - 1/7 Share: 2', 1142.86, 'Pending', 'regular');

INSERT INTO "user" (zelle_name, phone) VALUES ('Monica Robles', '0900545501');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '0900545501'), 'Cow Size 1 (Large) - 1/7 Share: 2', 1142.86, 'Pending', 'regular');

INSERT INTO "user" (zelle_name, phone) VALUES ('Alexandria Christensen', '0798151911');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '0798151911'), 'Cow Size 2 (Small) - 1/7 Share: 1', 285.71, 'Pending', 'regular');

INSERT INTO "user" (zelle_name, phone) VALUES ('Sophia Johnson', '0976421688');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '0976421688'), 'Full Goat: 2', 900.0, 'Pending', 'regular');

INSERT INTO "user" (zelle_name, phone) VALUES ('John Sanchez', '1639825753');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '1639825753'), 'Cow Size 2 (Small) - 1/7 Share: 1', 285.71, 'Pending', 'regular');

INSERT INTO "user" (zelle_name, phone) VALUES ('Kristina Boyd', '3559424910');
INSERT INTO "order" (user_id, items_ordered, total_price_usd, status, source)
VALUES ((SELECT id FROM "user" WHERE phone = '3559424910'), 'Cow Size 2 (Small) - 1/7 Share: 2', 571.42, 'Pending', 'regular');