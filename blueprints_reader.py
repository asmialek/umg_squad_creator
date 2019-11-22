import xlrd
import string
from collections import OrderedDict

from item_classes import Frame, Module


def read_slots(sheet, i):
    slots = OrderedDict()
    if sheet.cell_value(i, 5) != '-':
        for j in range(int(sheet.cell_value(i, 5))):
            slots['WL'+str(j)] = None
    if sheet.cell_value(i, 6) != '-':
        for j in range(int(sheet.cell_value(i, 6))):
            slots['WH'+str(j)] = None
    if sheet.cell_value(i, 7) != '-':
        for j in range(int(sheet.cell_value(i, 7))):
            slots['SL'+str(j)] = None
    if sheet.cell_value(i, 8) != '-':
        for j in range(int(sheet.cell_value(i, 8))):
            slots['SH'+str(j)] = None
    if sheet.cell_value(i, 9) != '-':
        for j in range(int(sheet.cell_value(i, 9))):
            slots['ML'+str(j)] = None
    if sheet.cell_value(i, 10) != '-':
        for j in range(int(sheet.cell_value(i, 10))):
            slots['MH'+str(j)] = None
    return slots


def read_frames(sheet):
    frames = {}
    for i in range(2, sheet.nrows):
        name = sheet.cell_value(i, 0)
        if name:
            pts = int(sheet.cell_value(i, 1))
            MV = int(sheet.cell_value(i, 2))
            AM = int(sheet.cell_value(i, 3))
            EG = int(sheet.cell_value(i, 4))
            special = sheet.cell_value(i, 11)
            slots = read_slots(sheet, i)
            frames[name] = Frame(name, pts, MV, AM, EG, special, slots)
    return frames


def read_weapons(sheet):
    weapons = {}
    for i in range(2, sheet.nrows):
        name = sheet.cell_value(i, 0).replace('\n', ' ')
        pts = int(sheet.cell_value(i, 1))
        size = sheet.cell_value(i, 2)
        DM = int(sheet.cell_value(i, 3))
        try:
            RG = int(sheet.cell_value(i, 4))
        except ValueError:
            RG = sheet.cell_value(i, 4)
        if sheet.cell_value(i, 5) == '-':
            EC = '-'
        else:
            EC = int(sheet.cell_value(i, 5))
        special = sheet.cell_value(i, 6)
        if name:
            weapons[name] = Module(name, pts, size, DM, RG, EC, special, 'Weapon')
    return weapons


def read_support(active_sheet, passive_sheet):
    support = {}
    sheet = active_sheet
    for i in range(2, sheet.nrows):
        name = sheet.cell_value(i, 0).replace('\n', ' ')
        pts = sheet.cell_value(i, 1)
        # pts = int(sheet.cell_value(i, 1))
        size = sheet.cell_value(i, 2)
        if sheet.cell_value(i, 3) == '-':
            EC = '-'
        else:
            EC = sheet.cell_value(i, 3)
            # EC = int(sheet.cell_value(i, 3))
        special = sheet.cell_value(i, 4)
        module_type = "Support Active"
        if name:
            support[name] = Module(name, pts, size, '-', '-', EC, special, module_type)
    sheet = passive_sheet
    for i in range(2, sheet.nrows):
        name = sheet.cell_value(i, 0)
        pts = sheet.cell_value(i, 1)
        # pts = int(sheet.cell_value(i, 1))
        size = sheet.cell_value(i, 2)
        if sheet.cell_value(i, 3) == '-':
            EC = '-'
        else:
            EC = sheet.cell_value(i, 3)
            # EC = int(sheet.cell_value(i, 3))
        special = 'Passive: ' + sheet.cell_value(i, 4)
        module_type = "Support Passive"
        if name:
            support[name] = Module(name, pts, size, '-', '-', EC, special, module_type)
    return support
