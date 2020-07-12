from controller.width import *


class Day:
    def __init__(self, constants, db):
        self.constants = constants
        self.db = db

    def get_m3_per_day(self, data):
        # constant for each day
        width = Width(self.constants)
        influx = data['influx']
        collection = {}

        # initiating
        water_height_yesterday = 0
        berging = 0
        l_w = 0
        every_day_reduction_collection = {}
        every_day_reduction = 0

        for day in range(self.constants['amount_days']):
            days_left = self.constants['amount_days'] - day

            # calculate berging
            berging = get_berging(berging, influx[day], every_day_reduction, data['max_berging'],data['L_parcel'], l_w, data['ditch_width'])

            # calculate l_w this day with berging (storage)
            l_w = get_l_w(data['helling_rad'], data['L_parcel'], berging, data['max_berging_schuin'], data['l_w_max'])

            # calculate water height with current berging, lw and data
            water_height_today = get_water_height(berging, l_w, data['ditch_width'], data['L_parcel'], data['helling_rad'], data['h_weir'])

            # compare all reduction_water_height with current water height
            for reduction_water_height in every_day_reduction_collection:
                if reduction_water_height > water_height_today:
                    every_day_reduction_collection[reduction_water_height] = {}

            # compare water_height with yesterday
            water_height_diff = water_height_today - water_height_yesterday

            required_data = {'days_left': days_left,
                             'water_height_diff': water_height_diff,
                             'kD_aquifer': data['kD_aquifer'],
                             'max_L_tot_sloot': data['max_L_tot_sloot'],
                             'L_parcel': data['L_parcel'],
                             'l_w': l_w,
                             'h_weir': data['h_weir'],
                             'berging':berging,
                             'parcel_current_m3': sum(collection.values())}

            if not data['dw'] == 0:
                if water_height_today > data['dw']:
                    if water_height_today - water_height_diff < data['dw']:
                        water_height_diff = water_height_today - data['dw']

            #if there is a water level increase, distinct between presence 'dw'
            if not data['dw'] == 0 and water_height_today < data['dw']:
                required_data['water_height_diff'] = 0
                m3_day = width.get_m3_per_width(required_data)
                every_day_reduction_collection = {} #removing remaining conserving, due to waterlevel lower than infiltration layer
            elif water_height_diff > 0:
                m3_day = width.get_m3_per_width(required_data)
            else:
                required_data['water_height_diff'] = 0
                m3_day = width.get_m3_per_width(required_data)

            # add every_day reduction
            if water_height_today > 0 and water_height_today > data['dw']:
                if m3_day > 0:
                    conserving_first_days = get_conserving_first_days(width, days_left, required_data)
                    conservering_left_days = {}
                    if days_left > 7:
                        conservering_left_days_value = (m3_day - sum(conserving_first_days.values())) / (days_left - 7)
                        for t_res in range(days_left - 8):
                            conservering_left_days[t_res] = conservering_left_days_value
                    conservering_future = {**conserving_first_days, **conservering_left_days}
                    every_day_reduction_collection = update_every_day_reduction(conservering_future, water_height_today, every_day_reduction_collection)
            else:
                required_data['water_height_diff'] = 0
                conserving_first_days = get_conserving_first_days(width, days_left, required_data)
                conservering_left_days = {}
                if days_left > 7:
                    conservering_left_days_value = (m3_day - sum(conserving_first_days.values())) / (days_left - 7)
                    for t_res in range(days_left - 8):
                        conservering_left_days[t_res] = conservering_left_days_value
                conservering_future = {**conserving_first_days, **conservering_left_days}
                every_day_reduction_collection = update_every_day_reduction(conservering_future, water_height_today, every_day_reduction_collection)

            every_day_reduction = get_m3_conserved_day(every_day_reduction_collection, days_left)
            #coservation can not be greater than available water:
            if every_day_reduction > berging:
                every_day_reduction = berging
            #if water is lower than dw, no conservation
            if water_height_today < data['dw']:
                every_day_reduction = 0
            m3_conserved_day = every_day_reduction

            # insert day values to database
            if self.constants['save_days_data']:
                mm_day = get_total_mm(m3_conserved_day, data['l_w_max'], data['L_parcel'], data['max_L_tot_sloot'])
                self.db.insert_day([day,
                                    data['year_parcel_id'],
                                    m3_conserved_day,
                                    mm_day,
                                    water_height_today])

            # set ready for next day
            water_height_yesterday = water_height_today
            # set to collection conserved
            collection[day + 1] = m3_conserved_day

        total_m3 = sum(collection.values())

        # returned list with days and its m3 conserved
        return total_m3


def get_berging(berging, influx, reduction, max_berging, L_parcel, l_w, ditch_width):
    # calculating evaporation  (2mm):
    if l_w > L_parcel:
        evap = 0.002 * L_parcel * ditch_width
    else:
        evap = 0.002 * l_w * ditch_width

    berging += influx - (reduction) - evap
    if berging > max_berging:
        return max_berging
    if berging < 0:
        berging = 0
    return berging


def get_water_height(berging, l_w, ditch_width, l_parcel, helling_rad, h_weir):
    if berging > 0:
        if l_w == l_parcel and helling_rad != 0:
            water_height = ((berging - ((l_parcel * ditch_width * math.tan(helling_rad) * l_parcel) / 2)) / (l_parcel * ditch_width)) + (math.tan(helling_rad) * l_parcel)
        elif l_w == l_parcel and helling_rad == 0:
            water_height = berging / (l_parcel * ditch_width)
        else:
            water_height = (berging * 2) / (l_w * ditch_width)
        if water_height < 0:
            water_height = 0
        if water_height > h_weir:
            water_height = h_weir
    else:
        water_height = 0
    return water_height


def get_l_w(helling_rad, l_parcel, berging, max_berging_schuin, l_w_max):
    if berging > 0:
        if helling_rad != 0:
            if l_w_max < l_parcel:
                l_w = l_w_max * (math.sqrt(berging / max_berging_schuin))
            elif l_w_max > l_parcel and berging < max_berging_schuin:
                l_w = l_parcel * (math.sqrt(berging / max_berging_schuin))
            else:
                l_w = l_parcel
        else:
            l_w = l_parcel
    else:
        l_w = 0
    return l_w


def get_total_mm(m3_conserved_day, l_w_max, l_parcel, max_L_tot_sloot):
    if l_w_max > l_parcel:
        total_mm = (m3_conserved_day / (l_parcel * max_L_tot_sloot)) * 1000
    else:
        total_mm = (m3_conserved_day / (l_w_max * max_L_tot_sloot)) * 1000
    return total_mm


def get_conserving_first_days(width, days_left, required_data):
    if days_left > 7:
        first_days_amount = 7
    else:
        first_days_amount = days_left
    conserving_first_days = {}
    for t_res in range(1, first_days_amount + 1):
        required_data['days_left'] = t_res
        m3_conserved = (width.get_m3_per_width(required_data) - sum(conserving_first_days.values()))
        conserving_first_days[days_left - t_res] = m3_conserved
    return conserving_first_days


def update_every_day_reduction(conservering_future, water_height_today, every_day_reduction_collection):
    if water_height_today in every_day_reduction_collection.keys():
        for day in conservering_future:
            if day in every_day_reduction_collection[water_height_today].keys():
                every_day_reduction_collection[water_height_today][day] += conservering_future[day]
            else:
                every_day_reduction_collection[water_height_today][day] = conservering_future[day]
    else:
        every_day_reduction_collection[water_height_today] = conservering_future
    return every_day_reduction_collection


def get_m3_conserved_day(every_day_reduction_collection, days_left):
    m3_conserved = 0
    for reduction_water_height in every_day_reduction_collection:
        if days_left in every_day_reduction_collection[reduction_water_height].keys():
            m3_conserved += every_day_reduction_collection[reduction_water_height][days_left]
    return m3_conserved


