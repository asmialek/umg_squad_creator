import PySimpleGUI as sg
import xlrd
import random
import pickle
import re

from blueprints_reader import read_support, read_weapons, read_frames
from item_classes import Mech
from mech_editor import open_new_window


def create_table_list(local_mech_list):
    temp_table_list = []
    for mech in local_mech_list:
        new_row = [mech.name,
                   mech.frame.name,
                   mech.pts,
                   mech.MV,
                   mech.AM,
                   mech.EG,
                   mech.special]
        temp_table_list.append(new_row)
    return temp_table_list


def calculate_pts(local_mech_list):
    current_pts = 0
    for mech in local_mech_list:
        current_pts += mech.pts
    return int(current_pts)


if __name__ == '__main__':
    loc = "umg_spreadsheets.xlsx"

    random_mech_names = []
    with open('random_mech_names.txt') as f:
        for line in f.readlines():
            random_mech_names.append(line)
    random_mech_names = list(dict.fromkeys(random_mech_names))

    wb = xlrd.open_workbook(loc)
    frames_sheet = wb.sheet_by_name("Frames")
    weapons_sheet = wb.sheet_by_name("Weapons")
    support_active_sheet = wb.sheet_by_name("Support Active")
    support_passive_sheet = wb.sheet_by_name("Support Passive")

    frames_dict = read_frames(frames_sheet)
    weapons_dict = read_weapons(weapons_sheet)
    support_dict = read_support(support_active_sheet, support_passive_sheet)
    modules_dict = {}
    modules_dict.update(weapons_dict)
    modules_dict.update(support_dict)

    mech_list = []
    pts_total = 0
    pass

    # -------
    #   GUI
    # -------
    frames_list = list(frames_dict.keys())
    headings = ['name', 'frame', 'pts', 'MV', 'AM', 'EC', 'special']
    table_list = []

    sg.change_look_and_feel('Default1')

    squad_name = 'Alpha Squad'

    layout = [[sg.Text('Squad name:'),
               sg.Text(squad_name, justification='center', relief='sunken', size=(60, 1), key='NAME'),
               sg.Button('CHANGE', key='CHANGE', enable_events=True),
               sg.Text(''),
               sg.Text('Squad pts total:'),
               sg.Text(pts_total, size=(4, 1), justification='center', relief='sunken', key='PTS')],
              [sg.Text('New frame:'),
               sg.Combo(frames_list, default_value='Light', enable_events=True, key="Frame"),
               sg.Button('ADD', key="ADD", enable_events=True, focus=True),
               sg.Button('REMOVE', key="RM", enable_events=True),
               sg.Button('EDIT', key="EDIT", enable_events=True),
               sg.Button('SAVE SQUAD', key="SAVE", enable_events=True),
               sg.Button('LOAD SQUAD', key="LOAD", enable_events=True),
               sg.Button('NEW SQUAD', key="NEW", enable_events=True),
               ],
              [sg.Table(values=table_list,
                        headings=headings, max_col_width=25, background_color='lightblue',
                        auto_size_columns=False,
                        display_row_numbers=False,
                        vertical_scroll_only=False,
                        justification='center',
                        num_rows=10,
                        # row_height=50,
                        bind_return_key=True,
                        alternating_row_color='blue',
                        key='TABLE',
                        tooltip='This is a table',
                        # enable_events=True,
                        )],
              [sg.Text(' ', size=(70, 1)),
               sg.Button('GENERATE', key="-gen-", enable_events=True),
               sg.Text(' ', size=(2, 1)),
               sg.Button('FINISH', key="-fin-", enable_events=True)]
              ]

    window = sg.Window('Squad Rooster', layout, resizable=True)

    while True:             # Event Loop
        event, values = window.Read()
        print("event: ", event)
        print("values: ",  values)
        if event is None:
            break

        # try:
        if event == 'ADD':
            print('Adding frame')
            chosen_frame = frames_dict[values["Frame"]]
            random_name = random_mech_names.pop(random.randrange(len(random_mech_names))).strip('\n')
            mech_list.append(Mech(chosen_frame, random_name))
            table_list = create_table_list(mech_list)
            window.Element('TABLE').Update(values=table_list)
        elif event == 'RM':
            if values["TABLE"]:
                index = values["TABLE"][0]
            elif mech_list:
                index = 0
            else:
                continue
            mech_list.pop(index)
            table_list = create_table_list(mech_list)
            window.Element('TABLE').Update(values=table_list)
        elif event in ['EDIT', 'TABLE']:
            if values["TABLE"]:
                window.Hide()
                chosen_mech = mech_list[values["TABLE"][0]]
                open_new_window(chosen_mech, frames_dict, modules_dict, pts_total)
                table_list = create_table_list(mech_list)
                window.Element('TABLE').Update(values=table_list)
                window.UnHide()
        elif event == 'CHANGE':
            squad_name = sg.popup_get_text('Enter new name:', default_text=squad_name)
            if squad_name:
                window.Element('NAME').Update(value=squad_name)
        elif event == 'SAVE':
            def_path = squad_name.lower().replace(' ', '_')
            # def_path = "".join(x for x in def_path if x.isalnum())
            file_name = sg.popup_get_file('Choose squad file:', save_as=True,
                                          default_path=def_path, default_extension='.sqd')
            if file_name:
                with open(re.sub(r'\.sqd$', '', file_name) + '.sqd', 'wb') as f:
                    pickle.dump([squad_name, mech_list], f)
        elif event == 'LOAD':
            file_name = sg.popup_get_file('Choose squad file:')
            if file_name:
                with open(file_name, 'rb') as f:
                    loaded_vals = pickle.load(f)
                    squad_name = loaded_vals[0]
                    mech_list = loaded_vals[1]
                table_list = create_table_list(mech_list)
                window.Element('TABLE').Update(values=table_list)
                window.Element('NAME').Update(value=squad_name)
        elif event == 'NEW':
            table_list = []
            mech_list = []
            squad_name = "Alpha Squad"
            window.Element('TABLE').Update(values=table_list)
            window.Element('NAME').Update(value=squad_name)
        if event == "FIN":
            break
        pts_total = calculate_pts(mech_list)
        window.Element('PTS').Update(value=pts_total)
        # except:
        #     pass

    window.Close()
