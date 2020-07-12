import math
from controller.day import *

class Parcel:
    def __init__(self, constants, db):
        self.constants = constants
        self.db = db

    def get_parcel(self, all_data, m_2_all_sub_regions, year):
        day = Day(self.constants, self.db)
        collection = {}
        for parcel_number in all_data:
            print(f"Processing Year: {year} Parcel: {parcel_number}")  #showing progress
            data_parcel = all_data[parcel_number]

            # calculate h_weir and ditch_width
            helling_rad = float(data_parcel['helling_deg']) * (math.pi / 180)
            if data_parcel['Sloot_Greppel'] == 'Sloot':
                h_weir = 1.2
                ditch_width = 1.45
            elif data_parcel['Sloot_Greppel'] == 'Greppel':
                h_weir = 0.8
                ditch_width = 0.85
            # calculate l_w_max
            if float(data_parcel['helling_deg']) == 0:
                l_w_max = 9999  #always bigger than L_parcel
            else:
                l_w_max = h_weir / math.tan(helling_rad)
            # calculate max berging(maximum storage)
            l_parcel = float(data_parcel['L_parcel'])
            if l_w_max > l_parcel:
                max_berging = (h_weir * l_parcel * ditch_width) - \
                              ((l_parcel * ditch_width * (math.tan(helling_rad) * l_parcel)) / 2)
                if float(data_parcel['helling_deg']) != 0:
                    max_berging_schuin = ((math.tan(helling_rad) * l_parcel) * ditch_width * l_parcel)/2
                else:
                    max_berging_schuin = -10000 #always much smaller than 0
            else:
                max_berging = (h_weir * l_w_max * ditch_width) / 2
                max_berging_schuin = max_berging
            #  calculate dw (Dikte weerstandlaag (aquitard))
            D_aquifer = float(data_parcel['D_aquifer'])
            if D_aquifer < h_weir:
                dw = h_weir - D_aquifer
            else:
                dw = 0

            # get influx
            sub_region = data_parcel['deelgebied']
            try:
                m_2_sub_region = m_2_all_sub_regions[sub_region]
            except Exception as e:
                print('Error: No sub region {} data!'.format(sub_region))
                exit(0)
            influx = get_influx(m_2_sub_region, float(data_parcel['max_L_tot_sloot']), l_w_max, l_parcel)

            # set to dictionary
            useful_data = {
                'max_L_tot_sloot': float(data_parcel['max_L_tot_sloot']),
                'kD_aquifer': float(data_parcel['kD_aquifer']),
                'D_aquifer': float(data_parcel['D_aquifer']),
                'helling_deg': float(data_parcel['helling_deg']),
                'L_parcel': float(data_parcel['L_parcel']),
                'ditch_width': ditch_width,
                'h_weir': h_weir,
                'helling_rad': helling_rad,
                'l_w_max': l_w_max,
                'max_berging': max_berging,
                'max_berging_schuin': max_berging_schuin,
                'dw': dw,
                'influx': influx,
                'year_parcel_id': int(f"{year}{parcel_number}")
            }

            total_m3 = day.get_m3_per_day(useful_data)
            total_mm = get_total_mm(total_m3, l_w_max, l_parcel, float(data_parcel['max_L_tot_sloot']))
            collection[int(data_parcel['perceelnr'])] = [total_m3, total_mm]
        return collection


def get_influx(m_2_sub_region, max_l_sloot, l_w_max, l_parcel):
    influx = []
    if l_w_max > l_parcel:
        for m_2_day in m_2_sub_region:
            influx.append(m_2_day * l_parcel * max_l_sloot)
    else:
        for m_2_day in m_2_sub_region:
            influx.append(m_2_day * l_w_max * max_l_sloot)
    return influx

#calculating total mm
def get_total_mm(total_m3, l_w_max, l_parcel, max_L_tot_sloot):
    if l_w_max > l_parcel:
        total_mm = (total_m3 / (l_parcel * max_L_tot_sloot)) * 1000
    else:
        total_mm = (total_m3 / (l_w_max * max_L_tot_sloot)) * 1000
    return total_mm





