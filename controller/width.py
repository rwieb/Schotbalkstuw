from controller.formula import *


class Width:
    def __init__(self, constants):
        self.constants = constants

    def get_m3_per_width(self, data):
        # calculating distance between 100 x-values
        x = data['max_L_tot_sloot'] / self.constants['dividing']
        width_position = 0
        formula = Formula(self.constants)

        collection = {}
        # loop other x_as values
        for x_as in range(self.constants['dividing']):
            y_as = formula.get_peilverhoging(data, width_position)
            collection[x_as] = y_as
            width_position += x

        # m2 (area graph, convert to m3)
        m2 = get_m2(collection, x)
        if data['l_w'] > data['L_parcel']:
            m3 = m2 * data['L_parcel']
        else:
            m3 = m2 * data['l_w']

        return m3


# calculating area graph
def get_m2(collection, x):
    m2 = 0
    for x_as in collection:
        if x_as + 1 in collection:
            m2_square = x * collection[x_as + 1]
            m2_triangle = (x * (collection[x_as] - collection[x_as + 1])) / 2
            m2 += m2_square + m2_triangle
    return m2
