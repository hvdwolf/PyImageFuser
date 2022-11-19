# -*- coding: utf-8 -*-

# Settings.py - This python helper script displays a Settings/Preferences window

# Copyright (c) 2022, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.


import PySimpleGUI as sg
import os
from pathlib import Path

import image_functions

def make_window():
    """
    Create a settings window

    :return: (sg.Window)  The window that was created
    """
    folderframelayout = [
        [sg.Input(sg.user_settings_get_entry('imgfolder', Path.home()), key='-IMGFOLDER-'), sg.FolderBrowse()],
        [sg.CB('Always use the last opened folder', sg.user_settings_get_entry('CBlast_opened_folder', False), key='-CBlop-')],
        [sg.VPush()],
    ]
    dcrawframelayout = [
        [sg.Input(sg.user_settings_get_entry('dcrawlocation', ""), key='-DCRAW-'), sg.FileBrowse()],
        [sg.Input(sg.user_settings_get_entry('dcrawparams', '-v -w -H 2 -T'), key='-dcrawparams-')]
    ]
    ffframelayout = [
        [sg.Frame('Specify the default image start folder', folderframelayout)],
        [sg.VPush()],
        [sg.Frame('Specify the Path to the dcraw binary/.exe', dcrawframelayout)]
    ]
    previewframelayout = [
        [sg.Text('Preview: pixel size of longest side'),
         sg.Combo(values=sorted(('360', '480', '512', '640', '720', '800')), default_value=sg.user_settings_get_entry('last_size_chosen', '640'), size=(5, 1), key='-COMBO-')],
        [sg.Text('(The aspect ratio of the image is preserved)')]
    ]
    jpegframelayout = [
        [sg.Spin([x for x in range(1, 100)], initial_value=sg.user_settings_get_entry('jpgCompression', '90'), key='_jpgCompression_', size=3),
         sg.Text('Default jpg compression when jpg is chosen as output format')],
    ]

    imgprefslayout = [
        [sg.Frame('Preview settings', previewframelayout)],
        [sg.VPush()],
        [sg.Frame('jpeg compression', jpegframelayout)],
    ]

    layout = [[sg.Text('Preferences', font = ('Calibri', 14, 'bold'))],
              #[sg.Input(sg.user_settings_get_entry('input', ''), k='-IN-')],
              [sg.TabGroup([[sg.Tab('Folder & File', ffframelayout, key='_FFTab_'),
                             sg.Tab('Image preferences', imgprefslayout),
              ]])],
              [sg.T('\nPreferences file = ' + sg.user_settings_filename())],
              [sg.Button('Save'), sg.Button('Exit without saving', key='_Exit_')]]

    return sg.Window('Preferences Window', layout, icon=image_functions.get_icon())


def settings_window():
    """
    Create and interact with a "settings window". You can a similar pair of functions to your
    code to add a "settings" feature.
    """

    sg.user_settings_filename(path=Path.home())
    window = make_window()

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, '_Exit_'):
            break
        if event == 'Save':
            # Save some of the values as user settings
            sg.user_settings_set_entry('imgfolder', values['-IMGFOLDER-'])
            sg.user_settings_set_entry('CBlast_opened_folder', values['-CBlop-'])
            sg.user_settings_set_entry('dcrawlocation', values['-DCRAW-'])
            sg.user_settings_set_entry('dcrawparams', values['-dcrawparams-'])
            sg.user_settings_set_entry('last_size_chosen', values['-COMBO-'])
            sg.user_settings_set_entry('jpgCompression', values['_jpgCompression_'])
            sg.popup("Preferences saved", icon=image_functions.get_icon(), auto_close=True, auto_close_duration=2)
            break

    window.Close()

