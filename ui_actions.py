# -*- coding: utf-8 -*-

# ui_actions.py - This python helper scripts executes the ui actions coming from the other scripts

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
import io, os, sys
from pathlib import Path
from PIL import Image


def display_org_preview(imgfile):
    '''
    This functions displays the embedded preview before any other
    preview image is created

    :param imgfile:    the path plus file of the preview image
    :type imgfile:     (str)
    '''
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
        window['_exposure_weight_'].update(value=0.0)
        window['_saturation_weight_'].update(value=1.0)
        window['_contrast_weight_'].update(value=1.0)
    else:  # enfuse defaults
        window['_exposure_weight_'].update(value=1.0)
        window['_saturation_weight_'].update(value=0.2)
        window['_contrast_weight_'].update(value=0.0)


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
