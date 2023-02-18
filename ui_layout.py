# -*- coding: utf-8 -*-

# ui_layout.py - This python helper scripts holds the user interface functions

# Copyright (c) 2022-2023, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import PySimpleGUI as sg

import os, platform

import ui_actions
import file_functions
import image_functions
import program_texts

#----------------------------------------------------------------------------------------------
#------------------------------------- Graph Contstants ---------------------------------------
BAR_WIDTH = 1  # width of each bar
BAR_SPACING = 1  # space between each bar
EDGE_OFFSET = 3  # offset from the left edge for first bar
GRAPH_SIZE = DATA_SIZE = (200, 100)  # size in pixels

#----------------------------------------------------------------------------------------------
#---------------------------------------- Menu ------------------------------------------------
menu_def = [
               ['&File', ['&Load images', '---', '&Preferences', 'E&xit']],
               ['&Help', ['&About...',
                          '&Credits',
                          'Program buttons',
                          'Alignment' ,
                          'Why exposure fuse?',
                          'Examples',
                          '---',
                          'System Info']],
           ]

#----------------------------------------------------------------------------------------------
#-------Main function that builds the whole gui and listens tot the commands ------------------
#----------------------------------------------------------------------------------------------
def create_and_show_gui(tmpfolder, startFolder):
# This creates the complete gui and then returns the gui
# to pyimagefuser where the events are evaluated
# ----------------------------------------------------------------------------------------------
# ---------------- Main tab for the default settings to make an enfused image  -----------------

    layoutMainGeneralCheckBoxes = [
        #[sg.Checkbox('Use OpenCV (instead of enfuse/AIS', key='_align_', default=True)],
        [sg.Text("Defaults")],
        [sg.Checkbox('Align the images', key='_always_align_', default=True)],
        #[sg.Checkbox('Use Align_image_stack', key='_useAIS_', default=True)],
        [sg.Checkbox('Display image after enfusing', key='_dispFinalIMG_', default=True)],
        [sg.Checkbox('Save final image to source folder', key='_saveToSource_', default=True)],
        [sg.Checkbox('Show intermediate output from functions', key='_showOutput_', default=False, enable_events=True)]
        #[sg.Checkbox('Use OpenCV instead of Enfuse', key='_useOpenCV_', default=False, enable_events=True)]
    ]
    layoutTab_SaveAs = [
        [sg.Text('Save final Image as:')],
        [sg.Radio('.jpg (Default)', "RADIOSAVEAS", default=True, key='_jpg_'), sg.Spin([x for x in range(1, 100)], initial_value="90", key='_jpgCompression_', readonly=True)],
        [sg.Radio('.tiff', "RADIOSAVEAS", default=False, key='_tiff_')],
        [sg.Radio('.png', "RADIOSAVEAS", default=False, key='_png_')]
    ]

    layoutMainPresets = [
        [sg.Text('What do you want to do?')],
        [sg.Radio('Exposure fusion', "RADIOPRESETTYPE", default=True, key='_exposurefusion_', enable_events=True)],
        [sg.Radio('Reduce noise from stack of photos', "RADIOPRESETTYPE", default=False, key='_noisereduction_', enable_events=True)],
        [sg.Radio('Focus Stacking', "RADIOPRESETTYPE", default=False, key='_focusstacking_', enable_events=True)],
    ]
    layoutMainText = [
        [sg.Text('In most cases you can simply stay on this main tab. '
                      'In case your alignment or the final exposure is not correct, please check the other tabs'
                      ' or read some of the Help topics.', size=(30,6),)]
    ]

    layoutMainTab = [
        [sg.Column(layoutMainPresets, vertical_alignment='top'), sg.VSeperator(), sg.Column(layoutMainGeneralCheckBoxes, vertical_alignment='top'), ],
        #[sg.Column(layoutMainPresets, vertical_alignment='top'), sg.VSeperator(), sg.Column(layoutMainGeneralCheckBoxes, vertical_alignment='top'), sg.VSeperator(), sg.Column(layoutMainText, vertical_alignment='top'),],
        [sg.VPush()],
        [sg.Text('Processing time: --', key='_proc_time_', ), sg.Text('', key='_STATUS_')]
    ]


# ----------------------------------------------------------------------------------------------
# --------------------------- OpenCV tabs -----------------

# ----------------------------------------------------------------------------------------------
# --------------------------- OpenCV alignment tab -----------------
    layoutOpenCVTab_align = [
        [sg.Text('Image alignment method', key='_cv_align_methods_')],
        [sg.Radio('ORB', "RADIOALIGN", default=True, key='_orb_', enable_events=True, tooltip='Fast and accurate. Less suited for huge exposure differences')],
        [sg.Radio('SIFT', "RADIOALIGN", default=False, key='_sift_', enable_events=True, tooltip='Accurate. No longer patented after 2020)')],
        [sg.Radio('ECC', "RADIOALIGN", default=False, key='_ecc_', enable_events=True,
              tooltip='Only use with huge exposure differences in the images.')],
        [sg.Radio('alignMTB', "RADIOALIGN", default=False, key='_alignmtb_', enable_events=True,
              tooltip='alignMTB is very fast but only delivers good results in simple situations.')],
    ]


    layoutOpenCVInputs = [
        [sg.Text('Calculation parameters')],
        [sg.InputText('500', key='_maxfeatures_', size=(5, 1), enable_events=True), sg.Text('ORB/ECC: max. Features/iterations')],
        [sg.InputText('0.3', key='_keeppercent_', size=(5, 1), enable_events=True), sg.Text('ORB/SIFT: Keep/Match percentage',
                                                                                 tooltip='ORB keep percentage defaults to 0.3. SIFT defaults to 0.65.')],
        [sg.InputText('1e-10', key='_termination_eps_', size=(5, 1), enable_events=True), sg.Text('ECC: Termination eps')],
    ]

    layoutOpenCVTab_ECC_options = [
        [sg.Text('ECC options', key='_cv_ecc_options_')],
        [sg.Radio('Euclidean (Default)', "RADIOECC", default=True, key='_euclidean_', disabled=True, tooltip='rotation and shift (translation)')],
        [sg.Radio('Affine', "RADIOECC", default=False, key='_affine_', disabled=True, tooltip='rotation, shift (translation), scale and shear.')],
        [sg.Radio('Homography', "RADIOECC", default=False, key='_homography_', disabled=True, tooltip='2D: (rotation, shift, scale and shear) and some 3D effects.')],
        [sg.Radio('Translation', "RADIOECC", default=False, key='_translation_', disabled=True, tooltip='Only shifted compared to other images')],
    ]
    layoutOpenCVTab_ORB_descriptors = [
        [sg.Text('ORB descriptors', key='_cv_orb_descriptor_')],
        [sg.Radio('ORB', "RADIOORBD", default=True, key='_orb_orb_desc_')],
        [sg.Radio('BEBLID', "RADIOORBD", default=False, key='_orb_beblid_desc_')],
    ]

    layoutOpenCV_descriptors_Inputs = [
        [sg.Text('ORB descriptors', key='_cv_orb_descriptor_', visible=False)],
        [sg.Radio('ORB', "RADIOORBD", default=True, key='_orb_orb_desc_', visible=False)],
        [sg.Radio('BEBLID', "RADIOORBD", default=False, key='_orb_beblid_desc_', visible=False)],
        #[sg.HSeparator()],
        [sg.Text('Calculation parameters')],
        [sg.InputText('500', key='_maxfeatures_', size=(5, 1), enable_events=True),
         sg.Text('ORB/ECC: max. Features/iterations')],
        [sg.InputText('0.3', key='_keeppercent_', size=(5, 1), enable_events=True),
         sg.Text('ORB/SIFT: Keep/Match percentage',
                 tooltip='ORB keep percentage defaults to 0.3. SIFT defaults to 0.65.')],
        [sg.InputText('1e-10', key='_termination_eps_', size=(5, 1), disabled=True, enable_events=True),
         sg.Text('ECC: Termination eps')],
    ]

    layoutAlignTab = [
        # [sg.Text("Align options")],
        [sg.Column(layoutOpenCVTab_align, vertical_alignment='top'), sg.VSeperator(),
         sg.Column(layoutOpenCV_descriptors_Inputs, vertical_alignment='top'), sg.VSeperator(),
         sg.Column(layoutOpenCVTab_ECC_options, vertical_alignment='top'),
         #sg.Column(layoutOpenCVInputs, vertical_alignment='top')
        ]
    ]
# ----------------------------------------------------------------------------------------------
# --------------------------- OpenCV exposure fusion tab -----------------
    layoutOpenCV_ExposureWeight = [
        [sg.Text('Exposure\nweight')],
        [sg.Slider(key='_cv_exposure_weight_', range=(0, 1), resolution='0.1', default_value='0', size=(6, None), )]
    ]
    layoutOpenCV_SaturationWeight = [
        [sg.Text('Saturation\nweight')],
        [sg.Slider(key='_cv_saturation_weight_', range=(0, 1), resolution='0.1', default_value='1.0', size=(6, None))]
    ]
    layoutOpenCV_ContrastWeight = [
        [sg.Text('Contrast\nweight')],
        [sg.Slider(key='_cv_contrast_weight_', range=(0, 1), resolution='0.1', default_value='1.0', size=(6, None))]
    ]

    layoutCVFusing_Presets = [
        [sg.Text('Presets')],
        [sg.Radio('OpenCV defaults', "RADIOPRESET", default=True, key='_preset_opencv_', enable_events=True,
              tooltip='Ew=0.0, Sw=1.0, Cw=1.0')],
        # [sg.Radio('None', "RADIOPRESET", default=True, key='_preset_none_')],
        [sg.Radio('Enfuse defaults', "RADIOPRESET", default=False, key='_preset_enfuse_', enable_events=True,
              tooltip='Ew=1.0, Sw=0.2, Cw=0.0')],
    ]

    layoutOpenCVTab_fuseoptions = [
        #[sg.Text('Exposure fusing options')],
        [sg.Column(layoutOpenCV_SaturationWeight,vertical_alignment='top'), sg.Column(layoutOpenCV_ContrastWeight,vertical_alignment='top'),
         sg.Column(layoutOpenCV_ExposureWeight,vertical_alignment='top'),
         sg.VSeperator(),
         sg.Column(layoutCVFusing_Presets, vertical_alignment='top')
         ]
    ]


#----------------------------------------------------------------------------------------------
#--------------------------- Left and right panel -----------------
    thumb_column = [
        [sg.Text("Thumb")],
        [sg.Image(ui_actions.display_org_previewthumb(os.path.join(os.path.realpath('.'), 'images', 'thumb.png'), 'thumb'), key='-THUMB-',)],
        [sg.Table(values=[(' ' * 15, ' '), (' ' * 15, ' '), (' ' * 15, ' '), (' ' * 15, ' ')], headings=['tag', 'value'], justification='left', alternating_row_color='lightgrey',num_rows=4, hide_vertical_scroll=True, key='_exiftable_', size=(240, 150))]
    ]

    graph_column = [[sg.Text('Histograms')],
                   [sg.Graph(GRAPH_SIZE, (0, 0), DATA_SIZE, k='-RGRAPH-')],
                   [sg.Graph(GRAPH_SIZE, (0, 0), DATA_SIZE, k='-GGRAPH-')],
                   [sg.Graph(GRAPH_SIZE, (0, 0), DATA_SIZE, k='-BGRAPH-')],
    ]

    layoutLeftPanel = [
        [sg.In(size=(1, 1), enable_events=True, key="-FILES-", visible=False),
            sg.FilesBrowse(button_text = 'Load Images', font = ('Calibri', 10, 'bold'), initial_folder=ui_actions.which_folder(), file_types = program_texts.image_formats, key='_btnLoadImages_'),
            #sg.Button('Load Images', font = ('Calibri', 10, 'bold'), key='_btnLoadImages_'),
            sg.Button('Preferences', font = ('Calibri', 10, 'bold'), key='_btnPreferences_')],
        [sg.Text('Images Folder:'), sg.Text( key='-FOLDER-', font = ('Calibri', 10, 'italic'), )],
        [sg.Listbox(values=[], enable_events=True, size=(35, 15), select_mode='multiple', key="-FILE LIST-"), sg.Column(thumb_column,vertical_alignment="top"), sg.Column(graph_column,vertical_alignment="top")],
        [sg.Button('Select all', font = ('Calibri', 10, 'bold'), key='_select_all_'),
         sg.Checkbox('Display selected image as preview when clicked on', key='_display_selected_', enable_events=True),],
    ]

    layoutRightPanel = [
        [sg.Image(ui_actions.display_org_previewthumb(os.path.join(os.path.realpath('.'), 'images', 'preview.png'), 'preview'),  key='-IMAGE-')],
        [sg.Button('(Re)Create Preview', font=('Calibri', 10, 'bold'), key='_create_preview_'),
         sg.Checkbox('Align preview', key='_align_preview_', default=True),
         ],
    ]


#----------------------------------------------------------------------------------------------
#--------------------------- Final Window layout -----------------
    layoutCloseButton = [
       [sg.Button('Close', font = ('Calibri', 10, 'bold'), key = '_Close_'),],
    ]

    layoutActionbuttons = [
        [sg.Button('Create Exposure fused image', font=('Calibri', 10, 'bold'), key='_CreateImage_',
                  tooltip='Use this option for Exposure fusion'),
        sg.Button('Create noise reduced image from stack', font=('Calibri', 10, 'bold'), key='_create_noise_reduced_',
                  tooltip='Use this option for noise reduction in a stack of images', visible=False),
        sg.Button('Create focus stacked image', font=('Calibri', 10, 'bold'), key='_create_focus_stacked_',
                  tooltip='Use this option for greater depth of field (DOF) from a stack of images', visible=False),
        ]
    ]

    layoutTabLogging = [
        [sg.Text("Program and function INFO output"), sg.Checkbox('Also show Debug info', key='-DEBUG-', enable_events=True),],
        [sg.Multiline(size=(140,35), key="-MLINE-" , enable_events=True, reroute_cprint=True, autoscroll=True, reroute_stdout=True)],
    ]
    layoutTabImages = [
        [sg.Column(layoutLeftPanel, vertical_alignment='top'), sg.VSeperator(),
         sg.Column(layoutRightPanel, vertical_alignment='top')],
        [sg.TabGroup([[sg.Tab('Main', layoutMainTab, key='_MainTab_'),
            #sg.Tab('OpenCV', layoutOpenCVTab),
            sg.Tab('Image alignment', layoutAlignTab),
            sg.Tab('Exposure Fusing options', layoutOpenCVTab_fuseoptions),
            sg.Tab('Output image type', layoutTab_SaveAs),
        ]])],
    ]

    layout = [
        [sg.Menu(menu_def, tearoff=False)],
        [sg.TabGroup([[sg.Tab(' Main Tab ', layoutTabImages, key='_layoutTabImages_', ),
            sg.Tab(' Logging / Program output ', layoutTabLogging, key='_layoutTabLogging_',),
        ]])],
        [sg.Push(),
            sg.Column(layoutActionbuttons), sg.Column(layoutCloseButton),
        ]
    ]

    # Open the window and return it to pyimagefuser
    return sg.Window('PyImageFuser ' + program_texts.Version, layout, icon=image_functions.get_icon(), finalize=True)
