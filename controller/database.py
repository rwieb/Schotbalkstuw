import sqlite3
from controller.initial_sql_database import sqlscript


class Database(object):
    def __init__(self, database='database.db'):
        self.database = database
        self.connect()
        self.checkexists()

    def connect(self):
        """Connect to the SQLite3 database."""
        self.conn = sqlite3.connect(self.database)
        self.cursor = self.conn.cursor()
        self.connected = True

    def close(self):
        """Close the SQLite3 database."""

        self.conn.commit()
        self.conn.close()
        self.connected = False

    def execute(self, statement, parameters = ''):
        """Execute SQL statements."""
        if not self.connected:
            # open a previously closed connection
            self.connect()
        try:
            self.cursor.execute(statement, parameters)
            self.conn.commit()
        except Exception as e:
            print('An SQL execute error occurred:', e)

    def insert_parcel(self, values):
        sql = '''INSERT INTO parcels(parcel_id, landgebruik, GWT, deelgebied, hellingperc, helling_deg, l_parcel, buisdr,
        sloot_greppel, max_l_tot_sloot, d_aquifer, kd_aquifer, spreidings_lengte)
                              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) '''
        self.execute(sql, values)

    def insert_year(self, values):
        sql = '''INSERT INTO years(year_parcel_id, year, parcel_id, m3_total, mm_total)
                              VALUES(?,?,?,?,?) '''
        self.execute(sql, values)

    def insert_day(self, values):
        sql = '''INSERT INTO days(day_number, year_parcel_id, m3_day, mm_day, water_height)
                              VALUES(?,?,?,?,?) '''
        self.execute(sql, values)


    def checkexists(self):  # check if database exists
        data = sqlscript()
        try:
            self.cursor.executescript(data)
        except Exception as e:
            print('Database creation error occurred:', e)

