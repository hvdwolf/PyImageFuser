# -*- coding: utf-8 -*-

# ui_layout.py - This python helper scripts holds the user interface functions

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

import ui_actions
import image_functions
import program_texts


#----------------------------------------------------------------------------------------------
#---------------------------------------- Menu ------------------------------------------------
menu_def = [
               ['&File', ['!&Load files', '---', '&Preferences', 'E&xit']],
               ['&Help', ['&About...', '&Credits', 'Program buttons', 'Exposure fusion', 'Alignment', ]],
           ]

#----------------------------------------------------------------------------------------------
#-------Main function that builds the whole gui and listens tot the commands ------------------
#----------------------------------------------------------------------------------------------
def create_and_show_gui(tmpfolder, startFolder):
# This creates the complete gui and then returns the gui
# to pyimagefuser where the events are evaluated
#----------------------------------------------------------------------------------------------
#---------------- Main tab for the default settings to make a exposure fused image  -----------------

    layoutAlignmtbbitshift = [
        [sg.Text('Logarithm to the base of 2 of the maximal\nshift in each dimension.\n5 or 6 is usually good enough.', )],
        [sg.Combo(values=sorted((3, 4, 5, 6, 7, 8)), default_value=5, size=(2, 1), key='_bitshiftCombo_')],
    ]
    layoutAlignModels = [
        [sg.Radio('AlignMTB', "RadioAlign", default=True, key='_radio_alignmtb_', tooltip='General purpose good and fast alignment')],
        [sg.Radio('ECC', "RadioAlign", default=False, key='_radio_ecc_', tooltip='The most accurate one, but also the slowest')],
        [sg.Radio('ORB (stacks only)', "RadioAlign", default=False, key='_radio_orb_', tooltip='ORB is a fast keypoint dectector. Use ONLY with perfectly aligned stacks.')],
    ]
    layoutAlignmentMethods = [
        [sg.Frame('Methods to align your images', layoutAlignModels, font=('Calibri', '10', 'bold'))],
        [sg.VPush()],
        [sg.Frame("Maximum bit shift (alignMTB only)", layoutAlignmtbbitshift, font=('Calibri', '10', 'bold'))],
    ]

    layoutAlignECCMotionModels = [
        #[sg.Text('ECC motion model', font=('Calibri', '10', 'bold'))],
        [sg.Text('Top to bottom in decreasing accuracy\n but increasing speed')],
        [sg.Radio('HOMOGRAPHY', "RadioMM", default=True, key='_homography_',)],
        [sg.Radio('AFFINE', "RadioMM", default=False, key='_affine_', )],
        [sg.Radio('EUCLIDEAN', "RadioMM", default=False, key='_euclidean_', )],
        [sg.Radio('TRANSLATION', "RadioMM", default=False, key='_translation_', )],
    ]
    layoutAlignmentTab = [
        [sg.Column(layoutAlignmentMethods, vertical_alignment='top'), sg.VSeperator(), sg.Frame('Geometric image transformation models (ECC only)', layoutAlignECCMotionModels, font=('Calibri', '10', 'bold'), vertical_alignment='top')],
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
        [sg.Radio('OpenCV defaults', "RADIOPRESET", default=True, key='_preset_opencv_', enable_events=True, tooltip='Ew=0.0, Sw=1.0, Cw=1.0')],
        [sg.Radio('Enfuse defaults', "RADIOPRESET", default=False, key='_preset_enfuse_', enable_events=True, tooltip='Ew=1.0, Sw=0.2, Cw=0.0')],
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
            sg.FilesBrowse(button_text = 'Load Images', font = ('Calibri', 10, 'bold'), initial_folder=ui_actions.which_folder(), file_types = program_texts.image_formats, key='_btnLoadImages_'),
            sg.Button('Preferences', font = ('Calibri', 10, 'bold'), key='_btnPreferences_')],
        [sg.Text('Images Folder:')],
        [sg.Text( key='-FOLDER-', font = ('Calibri', 10, 'italic'), )],
        #[sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-"), sg.Multiline(size=(40, 20), visible=False, disabled=True, echo_stdout_stderr=False, key = '_sgOutput_')],
        [sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-"), sg.Output(size=(40, 20), visible=False, key = '_sgOutput_')],
        #[sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-"), ],
        [sg.Button('Select all', font = ('Calibri', 10, 'bold'), key='_select_all_'),
         sg.Checkbox('Display selected image when clicked on', key='_display_selected_'),],
        #[sg.Frame('Program Settings', layoutMainFrame, font = ('Calibri', 10, 'bold'),)],
        [sg.TabGroup([[sg.Tab('Main', layoutMainTab)], [sg.Tab('Align Options', layoutAlignmentTab), sg.Tab('Exposure fuse options', layoutExposureFusionAll)]])]
    ]

    layoutRightPanel = [
        [sg.Image(ui_actions.display_org_preview(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','preview.png')), key='-IMAGE-')],
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
         sg.Button('Create noise reduced image', font = ('Calibri', 10, 'bold'), key='_noise_reduction_', tooltip='Use this option for noise reduction'),
         sg.Button('Close', font = ('Calibri', 10, 'bold'), key = '_Close_')]
    ]

    # Open the window and return it to pyimagefuser
    return sg.Window('PyImageFuser ' + program_texts.Version, layout, icon=image_functions.get_icon())
