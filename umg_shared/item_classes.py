class Frame:
    def __init__(self, name, pts, MV, AM, EG, special, slots):
        self.name = name
        self.pts = pts
        self.MV = MV
        self.AM = AM
        self.EG = EG
        self.special = special
        self.slots = slots


class Module:
    def __init__(self, name, pts, size, DM, RG, EC, special, module_type):
        self.name = name
        self.pts = pts
        self.size = size
        self.DM = DM
        self.RG = RG
        self.EC = EC
        self.special = special
        self.module_type = module_type

        self.tooltip = self.create_tooltip()

    def create_tooltip(self):
        tooltip = f'{self.module_type} ({self.size})<br/><br/>'
        tooltip += f'Energy cost: {self.EC}<br/>'
        if self.module_type == 'Weapon':
            tooltip += f'Range: {self.RG}<br/>'
            tooltip += f'Damage: {self.DM}<br/>'
        tooltip += f'<br/>{self.special}'
        return tooltip

    def use(self):
        print('Module used:', self.name)


# TODO: Add player class and set if for Mech objects

class Mech:
    def __init__(self, frame, name):
        self.player = None
        self.frame = frame
        self.frame_name = frame.name
        self.name = name
        self.pts = self.frame.pts
        self.MV = self.frame.MV
        self.AM = self.frame.AM
        self.EG = self.frame.EG
        self.energy = 0
        self.current_hp = self.AM
        self.remaining_mv = self.MV
        self.special = self.frame.special
        self.slots = self.frame.slots.copy()
        self.image = 'C:/Projects/umg_squad_creator/umg_shared/mech_images/resized/15310.png'
        # https://www.spriters-resource.com/ds_dsi/superrobotwarsw/

    def __print__(self):
        return str(f'Mech:\t {self.name}\n'
                   f'Player:\t {str(self.player)}\n'
                   f'AM:\t {self.AM}\n'
                   f'EG:\t {self.EG}\n'
                   f'Armor:\t {self.current_hp}\n'
                   f'Energy:\t {self.energy}\n'
                   f'')

    def update_frame(self, frame):
        self.frame = frame
        self.pts = self.frame.pts
        self.MV = self.frame.MV
        self.AM = self.frame.AM
        self.EG = self.frame.EG
        self.special = self.frame.special
        self.slots = self.frame.slots.copy()
        self.frame_name = frame.name
        self.current_hp = self.AM

    def update_slot(self, slot_name, new_module):
        if self.slots[slot_name]:
            self.pts -= self.slots[slot_name].pts
        self.slots[slot_name] = new_module
        if new_module:
            self.pts += self.slots[slot_name].pts
        self.pts = int(self.pts)


# class Weapon:
#     def __init__(self, name, pts, size, DM, RG, EC, special):
#         self.name = name
#         self.pts = pts
#         self.size = size
#         self.DM = DM
#         self.RG = RG
#         self.EC = EC
#         self.special = special
#
#
# class Support:
#     def __init__(self, name, pts, size, EC, special, type):
#         self.name = name
#         self.pts = pts
#         self.size = size
#         self.type = type
#         self.EC = EC
#         self.special = special
