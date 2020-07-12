from controller.perceel import *

class Year:
    def __init__(self, constants, db):
        self.constants = constants
        self.db = db
    def get_output(self, data, data_sub_region):
        parcel = Parcel(self.constants, self.db)
        for parcel_number in data:
            data_parcel = data[parcel_number]
            # insert data to database
            self.db.insert_parcel([int(data_parcel['perceelnr']),
                              data_parcel['Landgebruik'],
                              data_parcel['GWT'],
                              int(data_parcel['deelgebied']),
                             float(data_parcel['Hellingperc']),
                             float(data_parcel['helling_deg']),
                             float(data_parcel['L_parcel']),
                             int(data_parcel['Buisdr']),
                             data_parcel['Sloot_Greppel'],
                             float(data_parcel['max_L_tot_sloot']),
                             float(data_parcel['D_aquifer']),
                             float(data_parcel['kD_aquifer']),
                             float(data_parcel['spreidingslengte'])]
                             )
        for year in data_sub_region:
            m3_mm_all = parcel.get_parcel(data, data_sub_region[year], year)

            for parcel_id in m3_mm_all:
                year_parcel_id = int(f"{year}{parcel_id}")
                self.db.insert_year([year_parcel_id,
                                     int(year),
                                     int(parcel_id),
                                     m3_mm_all[parcel_id][0],  # m3_total
                                     m3_mm_all[parcel_id][1]
                                     ])
                year_parcel_id += 1
            print('output ' + str(m3_mm_all))
