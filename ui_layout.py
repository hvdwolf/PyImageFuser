# -*- coding: utf-8 -*-

# ui_layout.py.py - This python helper scripts holds the user interface functions

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

import io, os
from PIL import Image
from pathlib import Path

import image_functions
import program_texts


def which_folder():
    init_folder = ""
    sg.user_settings_filename(path=Path.home())
    start_folder = sg.user_settings_get_entry('imgfolder', Path.home())
    last_opened_folder = sg.user_settings_get_entry('last_opened_folder', Path.home())
    if last_opened_folder != Path.home():
        init_folder = last_opened_folder
    else:
        init_folder = start_folder

    return init_folder

def display_org_preview(imgfile):
    try:
        print("\n\nimgfile ", imgfile)
        image = Image.open(imgfile)
        sg.user_settings_filename(path=Path.home())
        longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
        image.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        return bio.getvalue()
    except:
        print("Something went wrong converting ", imgfile)
        pass
        return imgfile

def progress_window(message):
    global thread_done
    layout = [
        [sg.Text(message)],
        [sg.ProgressBar(max_value=100, size=(30, 10), key='bar', metadata=5)],
        [sg.Button('Close')]
    ]
    pwwindow = sg.Window('test', layout, finalize=True)

    pwwindow['bar'].Widget.config(mode='indeterminate')

    while True:
        event, values = pwwindow.Read(timeout=100)
        if pwwindow(timeout=100)[0] is None:
            break
        if event == 'Close':
            break
        if thread_done is True:
            break
        pwwindow['bar'].Widget['value'] += pwwindow['bar'].metadata
    pwwindow.close()
#----------------------------------------------------------------------------------------------
#---------------------------------------- Menu ------------------------------------------------
menu_def = [
               ['&File', ['!&Load files', '---', '&Preferences', 'E&xit']],
               ['&Help', ['&About...', '&Credits']],
           ]

#----------------------------------------------------------------------------------------------
#-------Main function that builds the whole gui and listens tot the commands ------------------
#----------------------------------------------------------------------------------------------
def create_and_show_gui(tmpfolder, startFolder):
# This creates the complete gui and then returns the gui
# to pyimagefuser where the events are evaluated
#----------------------------------------------------------------------------------------------
#---------------- Main tab for the default settings to make an enfused image  -----------------

    layoutMainGeneralCheckBoxes = [
        [sg.Checkbox('Always align images', key='_align_images_', default=True)],
        [sg.Checkbox('Display image after enfusing', key='_dispFinalIMG_', default=True)],
        [sg.Checkbox('Save final image to source folder', key='_saveToSource_', default=True)],
        [sg.Checkbox('Use ECC method for aligning', key='_eccMethod_', default=True, tooltip='ECC is more accurate than ORB, but 3-5x as slow')],
    ]
    layoutMain_SaveAs = [
        [sg.Text('Save Images as:')],
        [sg.Radio('.jpg (Default)', "RADIOSAVEAS", default=True, key='_jpg_'), sg.Spin([x for x in range(1,100)],initial_value="90", key='_jpgCompression_')],
        [sg.Radio('.Tiff 8bits', "RADIOSAVEAS", default=False, key='_tiff8_'), sg.Combo(['deflate', 'packbits', 'lzw', 'none'], default_value='deflate', key='_tiffCompression')],
    ]
    layoutMain_Presets = [
        [sg.Text('Presets')],
        [sg.Radio('None', "RADIOPRESET", default=True, key='_preset_none_')],
        [sg.Radio('OpenCV standards', "RADIOPRESET", default=False, key='_preset_opencv')],
        [sg.Radio('Enfuse standards', "RADIOPRESET", default=False, key='_preset_enfuse')],
    ]


#----------------------------------------------------------------------------------------------
#--------------------------- Exposure Fusion settings -----------------

    layoutExposureFusion_ExposureWeight = [
        [sg.Text('Exposure\nweight')],
        [sg.Slider(key = '_exposure_weight_', range=(0,1), resolution='0.1', default_value='0.0')] # enfuse 1.0
    ]
    layoutExposureFusion_SaturationWeight = [
        [sg.Text('Saturation\nweight')],
        [sg.Slider(key = '_saturation_weight_', range=(0,1), resolution='0.1', default_value='1.0')] # enfuse 0.2
    ]
    layoutExposureFusion_ContrastWeight = [
        [sg.Text('Contrast\nweight')],
        [sg.Slider(key = '_contrast_weight_', range=(0,1), resolution='0.1', default_value='1.0')] # enfuse 0
    ]
    layoutExposureFusion = [
          [sg.Column(layoutExposureFusion_ExposureWeight),
          sg.Column(layoutExposureFusion_SaturationWeight),
          sg.Column(layoutExposureFusion_ContrastWeight)],
    ]


    layoutMainFrame = [
        # [sg.Column(layoutMainGeneralCheckBoxes), sg.VSeperator(), sg.Column(layoutMain_SaveAs), sg.VSeperator(), sg.Column(layoutMain_Presets)]
        [sg.Column(layoutMainGeneralCheckBoxes), sg.VSeperator(), sg.Column(layoutMain_SaveAs), sg.VSeperator(), sg.Column(layoutExposureFusion),]
    ]
#----------------------------------------------------------------------------------------------
#--------------------------- Left and right panel -----------------
    layoutLeftPanel = [
        [sg.In(size=(1, 1), enable_events=True, key="-FILES-", visible=False),
            sg.FilesBrowse(button_text = 'Load Images', font = ('Calibri', 10, 'bold'), initial_folder=which_folder(), file_types = program_texts.image_formats, key='_btnLoadImages_'),
            sg.Button('Preferences', font = ('Calibri', 10, 'bold'), key='_btnPreferences_')],
        [sg.Text('Images Folder:')],
        [sg.Text(size=(60, 1), key='-FOLDER-', font = ('Calibri', 10, 'italic'))],
        [sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-"), sg.Output(size=(40, 20), visible=False, key = '_sgOutput_')],
        #[sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-"), ],
        [sg.Button('Select all', font = ('Calibri', 10, 'bold'), key='_select_all_'), sg.Checkbox('Display selected image when clicked on', key='_display_selected_')],
        [sg.Frame('Program Settings', layoutMainFrame, font = ('Calibri', 10, 'bold'),)],
    ]

    layoutRightPanel = [
        [sg.Image(display_org_preview(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','preview.png')), key='-IMAGE-')],
        [sg.Button('(Re)Create Preview', font = ('Calibri', 10, 'bold'), key='_create_preview_')],
    ]

#----------------------------------------------------------------------------------------------
#--------------------------- Final Window layout -----------------
    layout = [
        [sg.Menu(menu_def, tearoff=False)],
        [sg.Column(layoutLeftPanel), sg.VSeperator(), sg.Column(layoutRightPanel)],
        [sg.Push(), sg.Button('Create Exposure fused image', font = ('Calibri', 10, 'bold'), key='_CreateImage_', tooltip='Use this option for Exposure fusion'),
         sg.Button('Create noise reduced image', font = ('Calibri', 10, 'bold'), key='_noise_reduction_', tooltip='Use this option for improved noise reduction'),
         sg.Button('Close', font = ('Calibri', 10, 'bold'), key = '_Close_')]
    ]

    # Open the window and return it to pyimagefuser
    return sg.Window('PyImageFuser ' + program_texts.Version, layout, icon=image_functions.get_icon())
