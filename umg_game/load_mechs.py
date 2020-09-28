import PySimpleGUI as sg
import pickle

import umg_shared.item_classes

file_name = sg.popup_get_file('Choose squad file:')
if file_name:
    with open(file_name, 'rb') as f:
        loaded_vals = pickle.load(f)
        squad_name = loaded_vals[0]
        mech_list = loaded_vals[1]