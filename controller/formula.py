import math

class Formula:
    def __init__(self, constants):
        self.constants = constants


    def get_peilverhoging(self, data, x):
        water_height_diff = data['water_height_diff']
        s = 0.30  # storage coefficient
        kd = data['kD_aquifer']
        t_res = data['days_left']    # days to come
        y = water_height_diff * math.erfc(x * (math.sqrt(s / (4 * kd * t_res))))
        return y
