import PySimpleGUI as sg
import pickle

# from ...umg_shared import item_classes

def load_mech_list(file_name=None):
    if not file_name:
        file_name = sg.popup_get_file('Choose squad file:')
    if file_name:
        with open(file_name, 'rb') as f:
            loaded_vals = pickle.load(f)
            squad_name = loaded_vals[0]
            mech_list = loaded_vals[1]

    return mech_list

if __name__ == '__main__':
    mech_list = load_mech_list()
