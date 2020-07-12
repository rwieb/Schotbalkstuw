def sqlscript():  # sql for database
    sql = """
    DROP TABLE IF EXISTS parcels;
    DROP TABLE IF EXISTS years;
    DROP TABLE IF EXISTS days;
    CREATE TABLE `parcels` (
	`parcel_id`	INTEGER UNIQUE,
	`landgebruik`	TEXT,
	`GWT`	TEXT,
	`deelgebied`	INTEGER,
	`hellingperc`	INTEGER,
	`helling_deg`	INTEGER,
	`l_parcel`	INTEGER,
	`buisdr`	INTEGER,
	`sloot_greppel`	TEXT,
	`max_l_tot_sloot`	INTEGER,
	`d_aquifer`	INTEGER,
	`kd_aquifer`	INTEGER,
	`spreidings_lengte`	INTEGER,
	PRIMARY KEY(`parcel_id`)
);
CREATE TABLE `years` (
	`year_parcel_id`	INTEGER UNIQUE,
	`year`	INTEGER,
	`parcel_id`	INTEGER,
	`m3_total`	INTEGER,
	`mm_total`	INTEGER,
	PRIMARY KEY(`year_parcel_id`)
);
CREATE TABLE `days` (
	`day_number`	INTEGER,
	`year_parcel_id` INTEGER,
	`m3_day`	INTEGER,
	`mm_day`	INTEGER,
	`water_height`	INTEGER
);
"""
    return sql