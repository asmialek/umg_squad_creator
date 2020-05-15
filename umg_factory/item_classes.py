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


class Mech:
    def __init__(self, frame, name):
        self.frame = frame
        self.frame_name = frame.name
        self.name = name
        self.pts = self.frame.pts
        self.MV = self.frame.MV
        self.AM = self.frame.AM
        self.EG = self.frame.EG
        self.special = self.frame.special
        self.slots = self.frame.slots.copy()
        self.image = 'justin-spice-beta-mech-thumbs.jpg'

    def update_frame(self, frame):
        # self.pts -= self.frame.pts
        # self.MV -= self.frame.MV
        # self.AM -= self.frame.AM
        # self.EG -= self.frame.EG
        self.frame = frame
        # self.pts += self.frame.pts
        # self.MV += self.frame.MV
        # self.AM += self.frame.AM
        # self.EG += self.frame.EG
        self.pts = self.frame.pts
        self.MV = self.frame.MV
        self.AM = self.frame.AM
        self.EG = self.frame.EG
        self.special = self.frame.special
        self.slots = self.frame.slots.copy()
        self.frame_name = frame.name

    def update_slot(self, slot_name, new_module):
        if self.slots[slot_name]:
            self.pts -= self.slots[slot_name].pts
        self.slots[slot_name] = new_module
        if new_module:
            self.pts += self.slots[slot_name].pts
        self.pts = int(self.pts)