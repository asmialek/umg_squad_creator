from umg_shared.item_classes import Weapon


class CompositePistol(Weapon):
    def define(self):
        self.name = 'Composite Pistol'
        self.pts = 1
        self.size = 'L'
        self.DM = 1
        self.RG = 2
        self.EC = '-'
        self.special = '-'
        self.module_type = 'Weapon'


def create_weapons_list():
    weapons = [CompositePistol(),
              ]
    weapons_dict = {}

    for item in weapons:
        weapons_dict[item.name] = item

    return weapons_dict


# print(create_weapons_list())
