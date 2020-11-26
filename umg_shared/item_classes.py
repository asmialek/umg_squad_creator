from umg_shared import umg_logging


logger = umg_logging.Logger(printer=True)
log = logger.log


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
    def __init__(self):
        self.name = None
        self.pts = None
        self.size = None
        self.DM = None
        self.RG = None
        self.EC = None
        self.special = None
        self.module_type = None

        self.define()

        self.tooltip = self.create_tooltip()

    def define(self):
        pass

    def create_tooltip(self):
        tooltip = f'{self.module_type} ({self.size})<br/><br/>'
        tooltip += f'Energy cost: {self.EC}<br/>'
        if self.module_type == 'Weapon':
            tooltip += f'Range: {self.RG}<br/>'
            tooltip += f'Damage: {self.DM}<br/>'
        tooltip += f'<br/>{self.special}'
        return tooltip

    def use(self, *args):
        print('Module used:', self.name)


class Weapon(Module):
    def use(self, user, target):
        if not user.spend_energy(self.EC):
            return False

        if not target.receive_damage(self.DM):
            return False

        log(f'{user.name} is attacking {target.name} with {self.name}! Cost: {self.EC}, damage: {self.DM}.')
        
        return True


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
        self.has_acted = False
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

    def spend_energy(self, energy_cost):
        if isinstance(energy_cost, int):
            if self.energy >= energy_cost:
                self.energy -= energy_cost
                return True
            else:
                log('Not enough energy!')
                return False    
        elif energy_cost == '-':
            return True
        elif energy_cost == 'X':
            log('Function not yet implemented!')
            return False
        else:
            raise ValueError(f'Unexpected energy cost: {energy_cost}')

    def receive_damage(self, damage):
        if isinstance(damage, int):
            self.current_hp -= damage
            return True
        elif damage == '-':
            return True
        elif damage == 'X':
            log('Function not yet implemented!')
            return False
        else:
            log(f'Unknown damage value: {damage}')

        if self.current_hp <= 0:
            log(f'{self.name} destroyed!')


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
