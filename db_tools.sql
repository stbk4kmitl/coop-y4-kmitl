CREATE TABLE IF NOT EXISTS hardwarenames (
    hw_ VARCHAR(100) NOT NULL,
    rack_ INTEGER NOT NULL,
    unit_ INTEGER NOT NULL
);

TRUNCATE TABLE hardwarenames;


SELECT *
FROM hardwarenames