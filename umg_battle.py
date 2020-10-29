import pathlib
from umg_game import load_mechs
from umg_shared import umg_logging, weapons_list


squad_path = pathlib.Path('./squads/alpha_squad.sqd')
logger = umg_logging.Logger(printer=True)
log = logger.log


# TODO: Deplete energy function
# TODO: Receive damage function
# TODO: Check distance?


def generate_energy(mech):
    mech.energy += mech.EG


def attack(attacker, target, slot_id):
    # print(attacker)
    # print(target)
    if slot_id >= len(list(attacker.slots.keys())):
        log('Wrong slot id!')
        return False

    slot_name = list(attacker.slots.keys())[slot_id]
    weapon = attacker.slots[slot_name]
    if weapon == None:
        log('Slot empty!')
        return False
    elif weapon.module_type != 'Weapon':
        log('Not a weapon!')
        return False

    # Energy depletion step
    energy_cost = weapon.EC
    if isinstance(energy_cost, int):
        if attacker.energy >= energy_cost:
            attacker.energy -= energy_cost
            # return True
        else:
            log('Not enough energy!')
            return False
    elif energy_cost == '-':
        # return True
        pass
    elif energy_cost == 'X':
        log('Function not yet implemented!')
        return False

    # Damege step
    damage = weapon.DM
    if isinstance(damage, int):
        target.current_hp -= damage
        # return True
    elif damage == '-':
        # return True
        pass
    elif damage == 'X':
        log('Function not yet implemented!')
        return False
    else:
        log(f'Unknown damage value: {damage}')

    log(f'{attacker.name} is attacking {target.name} with {weapon.name}! Cost: {energy_cost}, damage: {damage}.')

    if target.current_hp <= 0:
        log(f'{target.name} destroyed!')


    # EC = int(attacker.slots[slot_name].EC) if eval(EC_str)
    # if attacker.energy >= attacker.slots[slot_name].EC:
        # pass


if __name__ == '__main__':


    # mech_list = load_mechs.load_mech_list(squad_path)

    # player = mech_list[0]
    # opponent = mech_list[1]
    # print('\n-!!------- GAME START -------!!-\n')
    # print(player)
    # print(opponent)
    
    # while(player.current_hp > 0 and opponent.current_hp > 0):
    #     print('---------- NEW TURN ----------\n')
    #     generate_energy(player)
    #     chosen_id = input('Player1, choose your weapon: ')
    #     print('')
    #     attack(player, opponent, int(chosen_id))
    #     print('')
    #     print(player)
    #     print(opponent)
    #     chosen_id = input('Player2, choose your weapon: ')
    #     print('')
    #     attack(opponent, player, int(chosen_id))
    #     print('')
    #     print(player)
    #     print(opponent)
    pass