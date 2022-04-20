# -*- coding: utf-8 -*-

# program_texts.py - This python helper scripts holds longer texts for popups and the like.
# It also contains a few functions to assist with this longer texts.

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

import image_functions

# Some program constants
Version = '0.2.0'
image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)

################ Some Function #################
def popup_text_scroll(title, message, scrollmessage):
    layout = [
        [sg.Text(message)],
        #[sg.ScrolledText(scrollmessage)],
        [sg.Multiline(scrollmessage, size=(80, 15), font='Courier 10', expand_x=True, expand_y=True, write_only=True,
                       autoscroll=True, auto_refresh=True)],
        [sg.Button('OK. Understood', key='-close_popup_text_scroll-')]
    ]
    ptswindow = sg.Window(title, layout, icon=image_functions.get_icon())

    while True:
        event, values = ptswindow.read()
        if event in (sg.WINDOW_CLOSED, 'OK. Understood', '-close_popup_text_scroll-'):
            break

    ptswindow.Close()



# Below are program texts
resize_warning_message = '''Something went wrong with resizing. Mostly this is due to missing exif info in your
images or due to incorrect exif info in your images.\n\n
The errors are displayed below:'''

resize_error_message = '''Something went really wrong with resizing.
The program can\'t continue. Please check your images carefully.'''

about_message = 'About PyImageFuser, Version ' + Version + '\n\n'
about_message += 'PyImageFuser is a graphical frontend for enfuse and align_image_stack.\n'
about_message += 'PyImageFuser is built using Python3 and PySimpleGui.\n\n'
about_message += 'PyImageFuser can be used for exposure bracketing and noise reduction.\n\n'
about_message += 'PyImageFuser is released under GPL v3.\n'
about_message += 'You should find the license with this software.\n\n'
about_message += 'Author: Harry van der Wolf.'

Credits =  '''Credits:\n\n
Used packages:
- Python3 + included modules/packages
- tkinter
- PySimpleGUI
- PIL (pillow)
- Python OpenCV
- NumPy
 
Used code (Thanks to the writers):
- Maitek: https://github.com/maitek/image_stacking
- Satya Mallick : https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
'''

