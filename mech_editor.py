import PySimpleGUI as sg
import random


def update_values(mech, window):
    window.Element('-mv-').Update(value=mech.MV)
    window.Element('-am-').Update(value=mech.AM)
    window.Element('-eg-').Update(value=mech.EG)
    window.Element('-pts-').Update(value=int(mech.pts))
    window.Element('-special-').Update(value=mech.special)


def read_slots(mech, modules_dict):
    i = 0
    dicts_collected = []
    types_collected = []
    bool_collected = []
    # print('---')
    for slot in mech.slots.keys():
        # print(slot)
        i += 1
        j = str(i)
        if slot[0] == 'S':
            combo_choices_dict = dict(filter(lambda elem: elem[1].module_type in ['Support Active', 'Support Passive'],
                                             modules_dict.items()))
            slot_type = 'Support'
        elif slot[0] == 'W':
            combo_choices_dict = dict(filter(lambda elem: elem[1].module_type == 'Weapon', modules_dict.items()))
            slot_type = 'Weapon'
        else:
            combo_choices_dict = modules_dict
            slot_type = 'Multi'
        if slot[1] == 'L':
            combo_choices_dict = dict(filter(lambda elem: elem[1].size == 'L', combo_choices_dict.items()))
            slot_type += ' [Light]'
        else:
            slot_type += ' [Heavy]'
        combo_choices_list = list(combo_choices_dict.keys())
        combo_choices_list.insert(0, 'None')
        dicts_collected.append(combo_choices_list)
        types_collected.append(slot_type)
        bool_collected.append(True)
    for k in range(i, 6):
        dicts_collected.append(['None',])
        types_collected.append('Not Available')
        bool_collected.append(False)

    return dicts_collected, types_collected, bool_collected


def read_first_slots(mech, modules_dict):
    i = 0
    default_values_collected = []
    DM_collected = []
    RG_collected = []
    EC_collected = []
    pts_collected = []
    special_collected = []
    for slot in mech.slots.keys():
        i += 1
        j = str(i)
        if mech.slots[slot]:
            default_values_collected.append(mech.slots[slot].name)
            DM_collected.append(mech.slots[slot].DM)
            RG_collected.append(mech.slots[slot].RG)
            EC_collected.append(mech.slots[slot].EC)
            pts_collected.append(int(mech.slots[slot].pts))
            special_collected.append(mech.slots[slot].special)
        else:
            default_values_collected.append('None')
            DM_collected.append('-')
            RG_collected.append('-')
            EC_collected.append('-')
            pts_collected.append('-')
            special_collected.append('-')
    for k in range(i + 1, 7):
        default_values_collected.append('None')
        DM_collected.append('-')
        RG_collected.append('-')
        EC_collected.append('-')
        pts_collected.append('-')
        special_collected.append('-')

    return default_values_collected, DM_collected, RG_collected, EC_collected, pts_collected, special_collected


def update_slots(mech, modules_dict, window):
    dicts_collected, types_collected, bool_collected = read_slots(mech, modules_dict)
    for i in range(0, 6):
        j = str(i+1)
        window.Element('slot_type_' + j).Update(value=types_collected[i])
        window.Element('slot_list_' + j).Update(values=dicts_collected[i], disabled=not bool_collected[i])


def update_slots_values(mech, modules_dict, window):
    _, DM_collected, RG_collected, EC_collected, pts_collected, special_collected = read_first_slots(mech, modules_dict)
    for i in range(0, 6):
        j = str(i+1)
        window.Element('slot_EC_' + j).Update(value=EC_collected[i])
        window.Element('slot_DM_' + j).Update(value=DM_collected[i])
        window.Element('slot_RG_' + j).Update(value=RG_collected[i])
        window.Element('slot_pts_' + j).Update(value=pts_collected[i])
        window.Element('slot_special_' + j).Update(value=special_collected[i])


def create_slots(mech, modules_dict):
    slots_lists_left = []
    slots_lists_right = []
    dicts_collected, types_collected, bool_collected = read_slots(mech, modules_dict)
    default_values_collected, DM_collected, RG_collected, EC_collected, pts_collected, special_collected\
        = read_first_slots(mech, modules_dict)
    for i in range(6):
        j = str(i+1)
        # k = str(i+4)
        if i % 2:
            slots_lists = slots_lists_right
        else:
            slots_lists = slots_lists_left
        slots_lists.append([sg.Text(text='Slot ' + j + ':', size=(6, 1)),
                     sg.Text(text=types_collected[i], size=(34, 1), justification='center',
                             relief='sunken', key=str('slot_type_' + j)),
                     sg.Text(text='pts', size=(4, 1), justification='right'),
                     sg.Text(text=pts_collected[i], size=(3, 1),
                             justification='center', relief='sunken', key=str('slot_pts_' + j))
                     ])
        slots_lists.append([sg.Combo(values=dicts_collected[i], enable_events=True, size=(21, 1),
                              key='slot_list_' + j, disabled=not bool_collected[i],
                              default_value=default_values_collected[i]),
                     sg.Text(text='EC', size=(3, 1)),
                     sg.Text(text=EC_collected[i], size=(3, 1), justification='center',
                             relief='sunken', key=str('slot_EC_' + j)),
                     sg.Text(text='DM', size=(3, 1)),
                     sg.Text(text=DM_collected[i], size=(3, 1), justification='center',
                             relief='sunken', key=str('slot_DM_' + j)),
                     sg.Text(text='RG', size=(3, 1)),
                     sg.Text(text=RG_collected[i], size=(3, 1), justification='center',
                             relief='sunken', key=str('slot_RG_' + j)),
                     ])
        slots_lists.append([sg.Multiline(default_text=special_collected[i], size=(51, 2), disabled=True,
                                         background_color='#d7d7d7', key='slot_special_' + j),
                            ])
    return slots_lists_left, slots_lists_right


def open_new_window(mech, frames_dict, modules_dict, pts_total):
    frames_list = list(frames_dict.keys())
    modules_list = list(modules_dict.keys())

    slots_elements_left, slots_elements_right = create_slots(mech, modules_dict)
    slots_elements_right = [*slots_elements_right]

    new_layout = [[sg.Text('Name:', size=(6, 1)),
                   sg.InputText(mech.name, enable_events=True, size=(45, 1), key="-name-"),
                   sg.Text('', size=(5, 1)),
                   sg.Text('Squad pts total:', size=(15, 1)),
                   sg.Text(text=pts_total, size=(3, 1), justification='center',
                           relief='sunken', key=str('-pts_total-'))
                   ],
                  [sg.Text('Frame:', size=(6, 1)),
                   sg.Combo(frames_list, default_value=mech.frame.name, size=(43, 1),
                            enable_events=True, key="-frame-"),
                  sg.Text('MV'),
                  sg.InputText(default_text=mech.MV, size=(3, 1), justification='center',
                               disabled=True, key='-mv-'),
                  sg.Text('    '),
                  sg.Text('AM'),
                  sg.InputText(default_text=mech.AM, size=(3, 1), justification='center',
                               disabled=True, key='-am-'),
                  sg.Text('    '),
                  sg.Text('EG'),
                  sg.InputText(default_text=mech.EG, size=(3, 1), justification='center',
                               disabled=True, key='-eg-'),
                  sg.Text('        '),
                  sg.Text('pts'),
                  sg.InputText(default_text=int(mech.pts), size=(3, 1), justification='center',
                                disabled=True, key='-pts-')
                   ],
                  [sg.Text('Special', size=(6, 1)),
                   sg.Text(text=mech.special, size=(107, 1), background_color='#d7d7d7',
                           relief='sunken' , key='-special-')
                   ],
                  [sg.Text('')],
                  [
                   sg.Column(slots_elements_left),
                   sg.Column(slots_elements_right),
                   ],
                  [sg.Text(' ', size=(90, 1)),
                   sg.Button('FINISH', key="-fin-", enable_events=True)]
                  ]

    sub_window = sg.Window('Mech Factory', new_layout, resizable=True)
    pts_total = pts_total-mech.pts

    slot_events = ['slot_list_' + str(i) for i in range(1, 7)]

    while True:
        event, values = sub_window.Read()
        print("event: ", event)
        print("values: ",  values)
        if event in [None, '-fin-']:
            break
        elif event == '-name-':
            mech.name = values['-name-']
        elif event == '-frame-':
            mech.update_frame(frames_dict[values['-frame-']])
            update_values(mech, sub_window)
            # sub_window.Element('-test-').Update(mech.frame.name)
            update_slots(mech, modules_dict, sub_window)
            update_slots_values(mech, modules_dict, sub_window)
        elif event in slot_events:
            # print('>>>', modules_dict[values[event]])
            keys_list = list(mech.slots.keys())
            slot_name = keys_list[int(event[-1])-1]
            if values[event] != 'None':
                new_module = modules_dict[values[event]]
            else:
                new_module = None
            mech.update_slot(slot_name, new_module)
            update_slots_values(mech, modules_dict, sub_window)
        sub_window.Element('-pts-').Update(value=int(mech.pts))
        sub_window.Element('-pts_total-').Update(value=int(pts_total+mech.pts))
    sub_window.Close()
