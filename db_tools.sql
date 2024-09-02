CREATE TABLE IF NOT EXISTS hardwarenames (
    hw_ VARCHAR(100) NOT NULL,
    rack_ INTEGER NOT NULL,
    unit_ INTEGER NOT NULL
);

TRUNCATE TABLE hardwarenames;



DO $$
DECLARE
    rack_value INTEGER;
BEGIN
    FOR rack_value IN 1..4 LOOP  -- เปลี่ยนขอบเขตตามความต้องการ
        EXECUTE format('
            CREATE TABLE IF NOT EXISTS rack_%s (
                hw_ VARCHAR(100) NOT NULL,
    			unit_ INTEGER NOT NULL
            );
        ', rack_value);
    END LOOP;
END $$;




