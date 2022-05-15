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
                          'Align_Image_stack parameters (man page)' ,
                          'Align_Image_stack tips',
                          'Enfuse parameters (man page)',
                          'Why exposure fuse?']],
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
        [sg.Checkbox('Use Align_image_stack', key='_useAIS_', default=True)],
        [sg.Checkbox('Display image after enfusing', key='_dispFinalIMG_', default=True)],
        [sg.Checkbox('Save final image to source folder', key='_saveToSource_', default=True)]
    ]
    layoutMain_SaveAs = [
        [sg.Text('Save final Image as:')],
        [sg.Radio('.jpg (Default)', "RADIOSAVEAS", default=True, key='_jpg_'), sg.Spin([x for x in range(1, 100)], initial_value="90", key='_jpgCompression_', readonly=True)],
        [sg.Radio('.Tiff 8bits', "RADIOSAVEAS", default=False, key='_tiff8_')],
        [sg.Radio('.Tiff 16 bits', "RADIOSAVEAS", default=False, key='_tiff16_'), sg.Combo(['deflate', 'packbits', 'lzw', 'none'], default_value='deflate', key='_tiffCompression')],
        [sg.Radio('.Tiff 32 bits', "RADIOSAVEAS", default=False, key='_tiff32_')],
        #[sg.Radio('.png', "RADIOSAVEAS", default=False, key='_png_')]
    ]
    layoutMainPresets = [
        [sg.Text('Presets')],
        [sg.Radio('None', "RADIOPRESET", default=True, key='_preset_none_')],
        [sg.Radio('Default (resets all settings to defaults)', "RADIOPRESET", default=False, key='_alltodefault_', enable_events=True)],
        [sg.Radio('Reduce noise in a stack of photos', "RADIOPRESET", default=False, key='_noisereduction_', enable_events=True)],
        [sg.Radio('Focus Stacking', "RADIOPRESET", default=False, key='_focusstacking_', enable_events=True)],
        [sg.Text('Simplest is: set to default, set to option', font = ('Any', 10, 'italic'))]
    ]
    layoutMainText = [
        [sg.Text('In most cases you can simply stay on this main tab. '
                      'In case your alignment or the final exposure is not correct, then check the other tabs'
                      ' or read some of the Help topics.', size=(30,6),)]
    ]

    layoutMainTab = [
        # [sg.Column(layoutMainGeneralCheckBoxes), sg.VSeperator(), sg.Column(layoutMain_SaveAs), sg.VSeperator(), sg.Column(layoutMain_Presets)]
        [sg.Column(layoutMainGeneralCheckBoxes, vertical_alignment='top'), sg.VSeperator(), sg.Column(layoutMain_SaveAs), sg.VSeperator(), sg.Column(layoutMainText, vertical_alignment='top'),],
        #[sg.Column(layoutMainGeneralCheckBoxes, vertical_alignment='top'), sg.VSeperator(), sg.Column(layoutMain_SaveAs), sg.VSeperator(), sg.Column(layoutMainPresets, vertical_alignment='top'),],
        [sg.VPush()],
        [sg.Text('Processing time: --', key='_proc_time_', )]
    ]

# ----------------------------------------------------------------------------------------------
# -------------------------------- Align_image_stack tab --------------------------------
    layoutAISInputs = [
        [ sg.InputText('50', key='_inHFOV_', size=(4, 1), disabled=True, enable_events=True, tooltip='Approximate horizontal field of view of input images, use if EXIF info not complete'), sg.Text("HFOV", tooltip='Approximate horizontal field of view of input images, use if EXIF info not complete'),sg.Checkbox('Auto HFOV', key='_autoHfov', default=True, enable_events=True, tooltip='Use exif info to determine HFOV. If not available, you can override the standard fallback value of 50'), ],
        [sg.InputText('0.9', key='_correlation_', size=(4, 1), enable_events=True), sg.Text('Correlation threshold')],
        [sg.InputText('8', key='_inNoCP_', size=(4, 1), enable_events=True), sg.Text('No. of Control points', tooltip='Default is 8. Increase to 20, 30 or 50 in case of not so good results.')],
        [sg.InputText('3', key='_removeCPerror_', size=(4, 1), enable_events=True), sg.Text('Remove Control points with error > than')],
        [sg.InputText('1', key='_inScaleDown_', size=(4, 1), enable_events=True), sg.Text('Scale down images by 2^ scale')],
        [sg.InputText('5', key='_inGridsize_', size=(4, 1), enable_events=True), sg.Text('Grid size (default: 5x5)')],
    ]

    layoutAIScheckboxes = [
        [sg.Checkbox('Autocrop images', key='_autoCrop_', default=True, tooltip='Important for hand held images. Autocrop to the area covered by all images.')],
        [sg.Checkbox('Use GPU for remapping', key='_useGPU_', default=True, tooltip='Be careful. Align_image_stack can crash without GPU support, even without warning')],
        [sg.Checkbox('Full Frame Fisheye images', key='_fffImages_', default=False)],
        [sg.Checkbox('Use given order', key='_usegivenorder_', default=False, tooltip='Use in stacks for noise reduction. NOT (!) for exposure bracketing')],
        #[sg.Checkbox('Assume linear input files', key='_linImages_', default=False,)],
    ]

    layoutAISadvanced = [
        [sg.Checkbox('Optimize Field of View for all images except first', key='_OptimizeFOV_', default=False, tooltip='Useful for aligning focus stacks with slightly different magnification. ')],
        [sg.Checkbox('Optimize image center for all images except first', key='_optimizeImgCenter_', default=False)],
        [sg.Checkbox('Optimize radial distortion for all images except first', key='_optimizeRadialDistortion_', default=False)],
        [sg.Checkbox('Optimize X coordinate of camera position', key='_optimixeXposition_', default=False)],
        [sg.Checkbox('Optimize Y coordinate of camera position', key='_optimixeYposition_', default=False)],
        [sg.Checkbox('Optimize Z coordinate of camera position', key='_optimixeZposition_', default=False)]
    ]

    layoutAISTab = [
        [sg.Column(layoutAIScheckboxes, vertical_alignment='top'), sg.VSeperator(), sg.Column(layoutAISInputs, vertical_alignment='top')]
    ]

# ----------------------------------------------------------------------------------------------
# --------------------------- Enfuse tab -----------------
    layoutEnfuseTab_Levels = [
        [sg.Text('Levels\n')],
        [sg.Slider(key='_levels_', range=(1, 29), resolution='1', default_value='29', size=(6, None))]
    ]
    layoutEnfuseTab_ExposureWeight = [
        [sg.Text('Exposure\nweight')],
        [sg.Slider(key='_exposure_weight_', range=(0, 1), resolution='0.1', default_value='1.0', size=(6, None), )]
    ]
    layoutEnfuseTab_SaturationWeight = [
        [sg.Text('Saturation\nweight')],
        [sg.Slider(key='_saturation_weight_', range=(0, 1), resolution='0.1', default_value='0.2', size=(6, None))]
    ]
    layoutEnfuseTab_ContrastWeight = [
        [sg.Text('Contrast\nweight')],
        [sg.Slider(key='_contrast_weight_', range=(0, 1), resolution='0.1', default_value='0', size=(6, None))]
    ]
    layoutEnfuseTab_EntropyWeight = [
        [sg.Text('Entropy\nweight')],
        [sg.Slider(key='_entropy_weight_', range=(0, 1), resolution='0.1', default_value='0', size=(6, None))]
    ]
    layoutEnfuseTab_ExposureOptimum = [
        [sg.Text('Exposure\noptimum')],
        [sg.Slider(key='_exposure_optimum_', range=(0, 1), resolution='0.1', default_value='0.5', size=(6, None))]
    ]

    layoutEnfuseTab_ExposureWidth = [
        [sg.Text('Exposure\nwidth')],
        [sg.Slider(key='_exposure_width_', range=(0, 1), resolution='0.1', default_value='0.2', size=(6, None))]
    ]
    layoutEnfuseTab_Mask = [
        [sg.Text('Mask')],
        [sg.Radio('Soft Mask (Default)', "RADIOMASK", default=True, key='_softmask_')],
        [sg.Radio('Hard Mask', "RADIOMASK", default=False, key='_hardmask_', tooltip='Blending with hard masks is ONLY useful with focus stacks.')]
    ]
    layoutEnfuseTab_Wrap = [
        [sg.Text('Wrap')],
        [sg.Radio('None (Default)', "RADIOWRAP", default=True, key='_none_')],
        [sg.Radio('Horizontal', "RADIOWRAP", default=False, key='_horizontal_')],
        [sg.Radio('Vertical', "RADIOWRAP", default=False, key='_vertical_')],
        [sg.Radio('Both', "RADIOWRAP", default=False, key='_both_')]
    ]
    '''
    layoutEnfuseTab = [
        [sg.Column(layoutEnfuseTab_Levels), sg.Column(layoutEnfuseTab_ExposureWeight),
         sg.Column(layoutEnfuseTab_SaturationWeight), sg.Column(layoutEnfuseTab_ContrastWeight),
         sg.Column(layoutEnfuseTab_EntropyWeight), sg.Column(layoutEnfuseTab_ExposureOptimum),
         sg.Column(layoutEnfuseTab_ExposureWidth), sg.VSeperator(),
         sg.Column(layoutEnfuseTab_Mask, vertical_alignment='top'), sg.Column(layoutEnfuseTab_Wrap, vertical_alignment='top')]
    ]
    '''
    layoutEnfuseTab = [
    [sg.Column(layoutEnfuseTab_Levels), sg.Column(layoutEnfuseTab_ExposureWeight), sg.Column(layoutEnfuseTab_SaturationWeight), sg.Column(layoutEnfuseTab_ContrastWeight),
     sg.Column(layoutEnfuseTab_Mask, vertical_alignment='top')],
    ]
    layoutEnfuseAdvanced = [
        [sg.Column(layoutEnfuseTab_EntropyWeight), sg.Column(layoutEnfuseTab_ExposureOptimum),
         sg.Column(layoutEnfuseTab_ExposureWidth), sg.VSeperator(),
         sg.Column(layoutEnfuseTab_Wrap, vertical_alignment='top'),],
    ]

# ----------------------------------------------------------------------------------------------
# --------------------------- Advanced tab -----------------
    layoutAdvanced = [
        [sg.Frame('Align_image_stack',layoutAISadvanced, vertical_alignment='top'), sg.Frame('Enfuse',layoutEnfuseAdvanced)],
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
            sg.Button('Preferences', font = ('Calibri', 10, 'bold'), key='_btnPreferences_')],
        [sg.Text('Images Folder:'), sg.Text( key='-FOLDER-', font = ('Calibri', 10, 'italic'), )],
        #[sg.Listbox(values=[], enable_events=True, size=(40, 20), select_mode='multiple', key="-FILE LIST-"), sg.Multiline(size=(40, 20), visible=False, disabled=True, echo_stdout_stderr=False, key = '_sgOutput_')],
        #[sg.Listbox(values=[], enable_events=True, size=(40, 15), select_mode='multiple', key="-FILE LIST-"), sg.Output(size=(40, 15), visible=False, key = '_sgOutput_')],
        #[sg.Listbox(values=[], enable_events=True, size=(40, 15), select_mode='multiple', key="-FILE LIST-"), sg.Image(ui_actions.display_org_previewthumb(os.path.join(os.path.realpath('.'), 'images', 'thumb.png'), 'thumb'), key='-THUMB-',)],
        [sg.Listbox(values=[], enable_events=True, size=(35, 15), select_mode='multiple', key="-FILE LIST-"), sg.Column(thumb_column,vertical_alignment="top"), sg.Column(graph_column,vertical_alignment="top")],
        [sg.Button('Select all', font = ('Calibri', 10, 'bold'), key='_select_all_'),
         sg.Checkbox('Display selected image as preview when clicked on', key='_display_selected_', enable_events=True),],
    ]

    layoutRightPanel = [
        [sg.Image(ui_actions.display_org_previewthumb(os.path.join(os.path.realpath('.'), 'images', 'preview.png'), 'preview'),  key='-IMAGE-')],
        [sg.Button('(Re)Create Preview', font=('Calibri', 10, 'bold'), key='_create_preview_'),
         sg.Checkbox('Use Align_image_stack', key='_useAISPreview_', default=True)],
    ]


#----------------------------------------------------------------------------------------------
#--------------------------- Final Window layout -----------------
    layout = [
        [sg.Menu(menu_def, tearoff=False)],
        [sg.Column(layoutLeftPanel, vertical_alignment='top'), sg.VSeperator(), sg.Column(layoutRightPanel, vertical_alignment='top')],
        [sg.TabGroup([[sg.Tab('Main', layoutMainTab,),
            sg.Tab('Align_image_stack', layoutAISTab),
            sg.Tab('Enfuse', layoutEnfuseTab, ),
            sg.Tab('Advanced', layoutAdvanced,),
        ]])],
        [sg.Push(),
            sg.Button('Create Exposure fused image', font = ('Calibri', 10, 'bold'), key='_CreateImage_', tooltip='Use this option for Exposure fusion'),
            #sg.Button('Create noise reduced image', font = ('Calibri', 10, 'bold'), key='_noise_reduction_', tooltip='Use this option for noise reduction'),
            sg.Button('Close', font = ('Calibri', 10, 'bold'), key = '_Close_')]
    ]

    # Open the window and return it to pyimagefuser
    return sg.Window('PyImageFuser ' + program_texts.Version, layout, icon=image_functions.get_icon())
