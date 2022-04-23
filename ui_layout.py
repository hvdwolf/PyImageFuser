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
    if last_opened_folder != Path.home() and os.path.isdir(last_opened_folder):
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
               ['&Help', ['&About...', '&Credits', 'Program parameters',]],
           ]

#----------------------------------------------------------------------------------------------
#-------Main function that builds the whole gui and listens tot the commands ------------------
#----------------------------------------------------------------------------------------------
def create_and_show_gui(tmpfolder, startFolder):
# This creates the complete gui and then returns the gui
# to pyimagefuser where the events are evaluated
#----------------------------------------------------------------------------------------------
#---------------- Main tab for the default settings to make an enfused image  -----------------

    layoutAlignmentMethods = [
        [sg.Text('Methods to align your images', font=('Calibri', '10', 'bold'))],
        [sg.Radio('ECC', "RadioAlign", default=True, key='_radio_ecc_', tooltip='The most accurate one, but also the slowest')],
        [sg.Radio('AlignMTB', "RadioAlign", default=False, key='_radio_alignmtb_', tooltip='General purpose fast alignment')],
        [sg.Radio('ORB', "RadioAlign", default=False, key='_radio_orb_', tooltip='General purpose more "only stacking" oriented')],
    ]
    layoutAlignECCMotionModels = [
        [sg.Text('Select the motion model (only for ECC):', font=('Calibri', '10', 'bold'))],
        [sg.Text('Top to bottom in decreasing accuracy\n but increasing speed')],
        [sg.Radio('HOMOGRAPHY', "RadioMM", default=True, key='_homography_',)],
        [sg.Radio('AFFINE', "RadioMM", default=False, key='_affine_', )],
        [sg.Radio('EUCLIDEAN', "RadioMM", default=False, key='_euclidean_', )],
        [sg.Radio('TRANSLATION', "RadioMM", default=False, key='_translation_', )],
    ]
    layoutAlignmentTab = [
        [sg.Column(layoutAlignmentMethods, vertical_alignment='top'), sg.VSeperator(), sg.Column(layoutAlignECCMotionModels, vertical_alignment='top')],
        [sg.VPush()],
        [sg.Push(), sg.Button('Help', font=('Calibri', '10', 'bold'), key='_align_help_')]
    ]

    layoutMainGeneralCheckBoxes = [
        [sg.Checkbox('Always align images', key='_align_images_', default=True)],
        #[sg.Checkbox('Use ECC method for aligning', key='_eccMethod_', default=True, tooltip='ECC is more accurate than ORB, but 3-5x as slow')],
        [sg.Checkbox('Display image after exposure fusing', key='_dispFinalIMG_', default=True)],
        [sg.Checkbox('Save final image to source folder', key='_saveToSource_', default=True)],
        #[sg.Frame('Options to align your images', layoutAlignmentFrame, font=('Calibri', '10', 'bold'))]
    ]
    layoutMain_SaveAs = [
        [sg.Text('Save Images as:')],
        [sg.Radio('.jpg (Default)', "RADIOSAVEAS", default=True, key='_jpg_'), ],
        #[sg.Radio('.tiff', "RADIOSAVEAS", default=False, key='_tiff_'), sg.Combo(['deflate', 'packbits', 'lzw', 'none'], default_value='deflate', key='_tiffCompression')],
        [sg.Radio('.tiff', "RADIOSAVEAS", default=False, key='_tiff_')],
        [sg.Radio('.png', "RADIOSAVEAS", default=False, key='_png_')],
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

    layoutFusing_Presets = [
        [sg.Text('Presets')],
        #[sg.Radio('None', "RADIOPRESET", default=True, key='_preset_none_')],
        [sg.Radio('OpenCV defaults', "RADIOPRESET", default=True, key='_preset_opencv', enable_events=True, tooltip='Ew=0.0, Sw=1.0, Cw=1.0')],
        [sg.Radio('Enfuse defaults', "RADIOPRESET", default=False, key='_preset_enfuse', enable_events=True, tooltip='Ew=1.0, Sw=0.2, Cw=0.0')],
    ]
    layoutExposureFusionAll = [
        [sg.Column(layoutExposureFusion), sg.VSeperator(), sg.Column(layoutFusing_Presets, vertical_alignment='top')],
        [sg.VPush()],
        [sg.Push(), sg.Button('Help', font=('Calibri', '10', 'bold'), key='_expfuse_help_')]
    ]

    layoutMainTab = [
        [sg.Column(layoutMainGeneralCheckBoxes),],
        [sg.VPush()],
        [sg.Text('Processing time: --', key='_proc_time_', )]

    ]
#----------------------------------------------------------------------------------------------
#--------------------------- Left and right panel -----------------
    layoutLeftPanel = [
        [sg.In(size=(1, 1), enable_events=True, key="-FILES-", visible=False),
            sg.FilesBrowse(button_text = 'Load Images', font = ('Calibri', 10, 'bold'), initial_folder=which_folder(), file_types = program_texts.image_formats, key='_btnLoadImages_'),
            sg.Button('Preferences', font = ('Calibri', 10, 'bold'), key='_btnPreferences_')],
        [sg.Text('Images Folder:')],
        [sg.Text(size=(60, 1), key='-FOLDER-', font = ('Calibri', 10, 'italic'))],
        #[sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-"), sg.Multiline(size=(40, 20), visible=False, disabled=True, echo_stdout_stderr=False, key = '_sgOutput_')],
        [sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-"), sg.Output(size=(40, 20), visible=False, key = '_sgOutput_')],
        #[sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-"), ],
        [sg.Button('Select all', font = ('Calibri', 10, 'bold'), key='_select_all_'),
         sg.Checkbox('Display selected image when clicked on', key='_display_selected_'),],
        #[sg.Frame('Program Settings', layoutMainFrame, font = ('Calibri', 10, 'bold'),)],
        [sg.TabGroup([[sg.Tab('Main', layoutMainTab)], [sg.Tab('Align Options', layoutAlignmentTab), sg.Tab('Exposure fuse options', layoutExposureFusionAll)]])]
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
        [sg.Push(),
         #sg.Button('AlignMTB fused image', font = ('Calibri', 10, 'bold'), key='_AlignMTB_', tooltip='Use this option for Exposure fusion'),
         sg.Button('Create Exposure fused image', font = ('Calibri', 10, 'bold'), key='_CreateImage_', tooltip='Use this option for Exposure fusion'),
         sg.Button('Create noise reduced image', font = ('Calibri', 10, 'bold'), key='_noise_reduction_', tooltip='Use this option for improved noise reduction'),
         sg.Button('Close', font = ('Calibri', 10, 'bold'), key = '_Close_')]
    ]

    # Open the window and return it to pyimagefuser
    return sg.Window('PyImageFuser ' + program_texts.Version, layout, icon=image_functions.get_icon())
