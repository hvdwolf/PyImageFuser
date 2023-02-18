# -*- coding: utf-8 -*-

# ui_actions.py - This python helper scripts executes the ui actions coming from the other scripts

# Copyright (c) 2022-2023, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.
import platform

import PySimpleGUI as sg
import io, os, sys
from pathlib import Path
from PIL import Image
Image.LOAD_TRUNCATED_IMAGES = True

import histogram
import image_functions
import file_functions
import program_texts
import run_commands


def display_org_previewthumb(imgfile, type):
    '''
    This functions displays the embedded preview before any other
    preview image is created

    :param imgfile:    the path plus file of the preview image
    :type imgfile:     (str)
    :param type:       Is it the preview or the thumb
    :type type:        (str)
    '''
    try:
        #print("\n\nimgfile ", imgfile)

        if platform.system() == 'Linux' or platform.system() == 'Darwin':
            testpyinstaller = getattr(sys, '_MEIPASS', 'NotRunningInPyInstaller')
            prefix = os.path.realpath('.')
            #print("ui_actions HERE ", os.getenv('HERE'))
            #print('pyinstaller _MEIPASS pyinstonrnot ', pyinstornot)
            if testpyinstaller != 'NotRunningInPyInstaller':
                prefix = testpyinstaller;
            if type == 'preview':
                 #image = Image.open(os.path.join(os.getenv('HERE'), 'images', 'preview.png'))
                 image = Image.open(file_functions.resource_path(os.path.join(prefix, 'images', 'preview.png')))
            else:
                image = Image.open(file_functions.resource_path(os.path.join(prefix, 'images', 'thumb.png')))
        else:
            image = Image.open(imgfile)

        if type == 'preview':
            sg.user_settings_filename(path=Path.home())
            longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
        else: # we have the thumb
            longestSide = 240
        image.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        image.close()
        return bio.getvalue()
    except:
        print("Something went wrong converting ", imgfile)
        pass
        return imgfile

def display_org_thumb(imgfile):
    try:
        #print("\n\nimgfile ", imgfile)
        image = Image.open(imgfile)
        image.thumbnail((200, 200), Image.ANTIALIAS)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        image.close()
        return bio.getvalue()
    except:
        print("Something went wrong converting ", imgfile)
        pass
        return imgfile

def set_fuse_presets(window, values):
    '''
    This functions reacts on the event where the radiobutton for opencv or enfuse
    preset is chosen and sets Contrast weight, Exposure weight and Saturation
    weight accordingly

    :param window:          This is the main window which we need to set values
    :type window:           window
    :param values:          This is the dictionary containing all UI key variables
    :type values:           (Dict[Any, Any]) - {Element_key : value}
    '''
    if values['_preset_opencv_']:
        window['_cv_exposure_weight_'].update(value=0.0)
        window['_cv_saturation_weight_'].update(value=1.0)
        window['_cv_contrast_weight_'].update(value=1.0)
    else:  # enfuse defaults
        window['_cv_exposure_weight_'].update(value=1.0)
        window['_cv_saturation_weight_'].update(value=0.2)
        window['_cv_contrast_weight_'].update(value=0.0)


def set_preview_radiobuttons(window, values):
    if values['_display_selected_']:
        # This means that we use the preview to display one of the input images
        window['_fusepreview_'].update(disabled=True)
        window['_stackpreview_'].update(disabled=True)
    else:
        window['_fusepreview_'].update(disabled=False)
        window['_stackpreview_'].update(disabled=False)

def disable_elements(window, disable_elements):
    '''
    This function disables / enables some buttons on the screen
    and does the opposite action for the output element

    :param window:             main window where elements are acted upon
    :type window:              Window
    :param disable_elements:   True or False
    :type disable_elements:    (bool)
    '''

    if disable_elements:
        window['_btnLoadImages_'].update(disabled=True)
        window['_btnPreferences_'].update(disabled=True)
        window['_select_all_'].update(disabled=True)
        window['_create_preview_'].update(disabled=True)
        window['_CreateImage_'].update(disabled=True)
        window['_create_noise_reduced_'].update(disabled=True)
        window['_Close_'].update(disabled=True)
        ##window['_sgOutput_'].update(visible=True, disabled=False, echo_stdout_stderr=True) # When buttons are disabled, output window becomes visible
        #window['_sgOutput_'].update(visible=True)  # When buttons are disabled, output window becomes visible
    else:
        window['_btnLoadImages_'].update(disabled=False)
        window['_btnPreferences_'].update(disabled=False)
        window['_select_all_'].update(disabled=False)
        window['_create_preview_'].update(disabled=False)
        window['_CreateImage_'].update(disabled=False)
        window['_create_noise_reduced_'].update(disabled=False)
        window['_Close_'].update(disabled=False)
        ##window['_sgOutput_'].update(visible=False, disabled=True, echo_stdout_stderr=False) # When buttons are enabled, output window is hidden
        #window['_sgOutput_'].update(visible=False) # When buttons are enabled, output window is hidden

def hide_show_buttons_options(window, values):
    if values['_exposurefusion_']:
        window['_CreateImage_'].update(visible=True)
        window['_create_noise_reduced_'].update(visible=False)
        window['_create_focus_stacked_'].update(visible=False)
        window['_alignmtb_'].update(disabled=False)
        window['_ecc_'].update(disabled=False)
    elif values['_noisereduction_']:
        window['_create_noise_reduced_'].update(visible=True)
        window['_CreateImage_'].update(visible=False)
        window['_create_focus_stacked_'].update(visible=False)
        window['_alignmtb_'].update(disabled=True)
        window['_ecc_'].update(disabled=False)
    elif values['_focusstacking_']:
        window['_create_focus_stacked_'].update(visible=True)
        window['_CreateImage_'].update(visible=False)
        window['_create_noise_reduced_'].update(visible=False)
        window['_alignmtb_'].update(disabled=True)
        window['_ecc_'].update(disabled=True)

def set_levels_status(window, values):
    '''
    This function reacts to events where OpenCV is chosen or enfuse "re-"chosen. It
    disables the enfuse options when OpenCV is chosen.
    OpenCV is currently not used. When it improves in the future it might.

    :param window:          This is the main window which we need to set values
    :type window:           window
    :param values:          This is the dictionary containing all UI key variables
    :type values:           (Dict[Any, Any]) - {Element_key : value}
    '''
    if values['_useOpenCV_']:
        window['layoutEnfuseTab_Mask_Wrap'].update(visible=False)
        window['_levels_'].update(disabled=True)
        window['_levels_'].update(visible=False)
        window['_masktext_'].update('')
        window['_softmask_'].update(disabled=True)
        window['_softmask_'].update(visible=False)
        window['_hardmask_'].update(disabled=True)
        window['_hardmask_'].update(visible=False)
    else:
        window['layoutEnfuseTab_Mask_Wrap'].update(visible=True)
        window['_levels_'].update(disabled=False)
        window['_levels_'].update(visible=True)
        window['_masktext_'].update('Mask')
        window['_softmask_'].update(disabled=False)
        window['_softmask_'].update(visible=True)
        window['_hardmask_'].update(disabled=True)
        window['_hardmask_'].update(visible=False)


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

def fill_images_listbox(window, values):
    filenames = []
    other_filenames = []
    pathnames = []
    read_errors = ""
    image_exif_dictionaries = {}
    window['-FILE LIST-'].update(filenames)
    #if len(files_tuple)>0:
    #print("fil " + values["-FILES-"])
    if values["-FILES-"]:  # or values["-FILES-"] == {}: #empty list returns False
        print("files read by user\n" + values["-FILES-"])
        file_list = values["-FILES-"].split(";")
        #file_list = files_chosen.split(",")
        #null_image = file_list[0]
        reference_image = ''
        for file in file_list:
            #file = file.strip()
            print("reading file: " + file)
            fname = os.path.basename(file)
            #print("fname = os.path.basename(file) " + fname)
            fname_extension = os.path.splitext(fname)[1]
            #print("fname_extension = os.path.splitext(fname)[1] " + fname_extension)
            if fname_extension.lower() in program_texts.str_raw_img_formats: # We are dealing with RAW images
                #sg.popup("Converting RAW to tiff using dcraw", icon=image_functions.get_icon(), auto_close=True, auto_close_duration=2)
                cmdstring, cmd_list = image_functions.create_dcraw_command(file)
                #print('cmdstring ' + cmdstring + " , cmd_list " + str(cmd_list))
                result = run_commands.run_shell_command(cmdstring, cmd_list, ' running dcraw on:\n\n' + file, False)
                fname = os.path.splitext(fname)[0] + ".tiff"
                file = os.path.splitext(file)[0] + ".tiff"

            filenames.append(fname)
            pathnames.append(file)
            null_image = pathnames[0]
            folder = os.path.dirname(os.path.abspath(file))
            # Now save this folder as "last opened folder" to our settings
            sg.user_settings_filename(path=Path.home())
            sg.user_settings_set_entry('last_opened_folder', folder)

            # get all exif date if available
            tmp_reference_image, image_exif_dictionaries[fname], read_error = image_functions.get_all_exif_info(file)
            #print("file " + file + "tmp_reference_image " + tmp_reference_image)
            if (len(read_error) > 0):
                read_errors += read_error + "\n"
            if tmp_reference_image != '':
                reference_image = tmp_reference_image
                print('reference_image', reference_image)
            else:
                other_filenames.append(file)
        window['-FILE LIST-'].update(filenames)
        window['-FOLDER-'].update(folder)
        # Check if we now have a reference image, in case the images do not contain (enough) exif info
        if reference_image == None or reference_image == "":
            reference_image = file_list[ int(len(file_list) / 2) ]

    return reference_image, folder, image_exif_dictionaries, other_filenames, file_list, read_errors

def exif_table(window, exif_dict):
    table_data = []
    exif_list = list(exif_dict.items())
    headings = ['tag', 'value']
    keys_to_extract = {'ExposureTime', 'ExposureBiasValue', 'FNumber', 'ISOSpeedRatings'}
    sub_dict = { key:value for key,value in exif_dict.items() if key in keys_to_extract}
    #print('sub_dict: ', sub_dict)
    table_data = list(sub_dict.items())
    window['_exiftable_'].update(values=table_data)


def clean_screen_after_file_loading(window):
    window['-THUMB-'].update(display_org_previewthumb(os.path.join(os.path.realpath('.'), 'images', 'thumb.png'), 'thumb'))
    window['-IMAGE-'].update(display_org_previewthumb(os.path.join(os.path.realpath('.'), 'images', 'preview.png'), 'preview'))
    empty_dict = {"": "", "": "", "": "", "": "",}
    exif_table(window, empty_dict)
    #if graph_ids[0] != None:
    histogram.clean_histogram(window)



# Maybe later
def set_align_options(window, values):
    if values['_orb_'] or values['_sift_'] or values['_alignmtb_']:
        window['_euclidean_'].update(disabled=True)
        window['_affine_'].update(disabled=True)
        window['_homography_'].update(disabled=True)
        window['_translation_'].update(disabled=True)
        window['_maxfeatures_'].update(disabled=True)
        window['_termination_eps_'].update(disabled=True)
        if values['_orb_']:
            window['_maxfeatures_'].update(disabled=False)
            window['_keeppercent_'].update(value='0.3', disabled=False)
            window['_orb_orb_desc_'].update(disabled=False)
            window['_orb_beblid_desc_'].update(disabled=False)
        elif values['_sift_']:
            window['_maxfeatures_'].update(disabled=False)
            window['_keeppercent_'].update(value='0.65', disabled=False)
            window['_orb_orb_desc_'].update(disabled=True)
            window['_orb_beblid_desc_'].update(disabled=True)
        elif values['_alignmtb_']:
            window['_maxfeatures_'].update(disabled=True)
            window['_keeppercent_'].update(disabled=True)
    elif values['_ecc_']:
        window['_euclidean_'].update(disabled=False)
        window['_affine_'].update(disabled=False)
        window['_homography_'].update(disabled=False)
        window['_translation_'].update(disabled=False)
        window['_termination_eps_'].update(disabled=False)
        window['_maxfeatures_'].update(disabled=True)
        window['_keeppercent_'].update(disabled=True)
        window['_orb_orb_desc_'].update(disabled=True)
        window['_orb_beblid_desc_'].update(disabled=True)

"""
BaseException
 +-- SystemExit
 +-- KeyboardInterrupt
 +-- GeneratorExit
 +-- Exception
     +-- Everything else
"""
def logger(e):
    e = sys.exc_info()
    print('Error Return Type: ', type(e))
    print('Error Class: ', e[0])
    print('Error Message: ', e[1])
    return str(e[1])
