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
        [sg.Text('Specify the default image start folder')],
        [sg.Input(sg.user_settings_get_entry('imgfolder', Path.home()), key='-IMGFOLDER-'), sg.FolderBrowse()],
        [sg.CB('Always use the last opened folder', sg.user_settings_get_entry('CBlast_opened_folder', False),
               key='-CBlop-')],
    ]
    previewframelayout = [
        [sg.Text('Preview: pixel size of longest side'),
         sg.Combo(values=sorted(('480', '640', '800')), default_value=sg.user_settings_get_entry('last_size_chosen', '640'), size=(5, 1), key='-COMBO-')],
        [sg.Text('(The aspect ratio of the image is preserved)')]
    ]

    layout = [[sg.Text('Preferences', font = ('Calibri', 14, 'bold'))],
              #[sg.Input(sg.user_settings_get_entry('input', ''), k='-IN-')],
              [sg.Frame('Folder settings', folderframelayout)],
              [sg.Frame('Preview settings', previewframelayout)],
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
            sg.user_settings_set_entry('last_size_chosen', values['-COMBO-'])
            sg.popup("Preferences saved", icon=image_functions.get_icon(), auto_close=True, auto_close_duration=2)
            break

    window.Close()

