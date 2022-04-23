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

################ Some Functions #################
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

def move_window_to_center(self):
    """
    Recenter your window after it's been moved or the size changed.

    This is a conveinence method. There are no tkinter calls involved, only pure PySimpleGUI API calls.
    """
    if not self._is_window_created('tried Window.move_to_center'):
        return
    screen_width, screen_height = self.get_screen_dimensions()
    print(screen_width, screen_height)
    win_width, win_height = self.size
    print(win_width, win_height)
    #x, y = (screen_width - win_width) // 2, (screen_height - win_height) // 2
    x, y = (1980 - win_width) // 2, (1080 - win_height) // 2
    print('x y ', x, y)
    self.move(x, y)
    #self.move(300, 50)
    #self['_updater_'].click()


def insert_newlines(string, every=64):
    return '\n'.join(string[i:i+every] for i in range(0, len(string), every))

def explain_parameters_popup():
    hfont = ('Calibri', 12, 'bold')
    tfont = ('Calibri', 10, 'normal')

    list_parameters = [(k, v) for k, v in Explain_parameters.items()]

    # this should be built dynamically, but leave it for now

    layout = [
        [sg.Text('Parameters', font = ('Calibri', 16, 'bold'))],

    ]
    paramwindow = sg.Window('Program parameters', layout, finalize=True, keep_on_top=True, icon=image_functions.get_icon(), location=(300, 50))

    max = len(list_parameters)
    blocks = range(max)
    for block in blocks:
        paramwindow.extend_layout(paramwindow, [[sg.Text(list_parameters[block][0], font=hfont,)]])
        paramwindow.extend_layout(paramwindow, [[sg.Text(list_parameters[block][1], font=tfont, )]])
    paramwindow.extend_layout(paramwindow, [[sg.Push(), sg.Button('OK'), sg.Button('_updater_', visible=False)]])
    #paramwindow.update(location=(100,100))
    #paramwindow.move_to_center()
    #paramwindow.finalize()
    paramwindow.refresh()
    paramwindow.move(100,50)
    #print(paramwindow.Size)
    move_window_to_center(paramwindow)
    #paramwindow.move_to_center()
    paramwindow['_updater_'].click()

    while True:
        event, values = paramwindow.Read()
        if event == sg.WIN_CLOSED or event == 'OK':
            break
        elif event == '_updater_':
            #paramwindow.move_to_center()
            paramwindow.move(100, 50)
            #paramwindow.finalize()
            paramwindow.refresh()
    paramwindow.close()



# Below are program texts
resize_warning_message = '''Something went wrong with resizing. Mostly this is due to missing exif info in your
images or due to incorrect exif info in your images.\n\n
The errors are displayed below:'''

resize_error_message = '''Something went really wrong with resizing.
The program can\'t continue. Please check your images carefully.'''

about_message = 'About PyImageFuser, Version ' + Version + '\n\n'
about_message += 'PyImageFuser can be used for exposure bracketing and noise reduction.\n\n'
about_message += 'PyImageFuser is built using Python3 and PySimpleGui.\n\n'
about_message += 'PyImageFuser is released under GPL v3.\n'
about_message += 'You should find the license with this software.\n\n'
about_message += 'Author: Harry van der Wolf.'

Credits =  '''Credits:\n\n
Used packages:
- Python3 (with included modules/packages)
- tkinter
- PySimpleGUI
- PIL (pillow)
- Python OpenCV
- NumPy
 
Used code (Thanks to the writers):
- Maitek: https://github.com/maitek/image_stacking
- Satya Mallick : https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
'''

# Add a \n every max. 78 characters
Explain_parameters = {
    "Always align images" : "Even on a tripod you might have minimal movement causing misalignment and \ntherefore unsharp blended images. Aligning them will improve sharpness, using \neither ECC or ORB.",
    "Use ECC method for aligning" : "Enhanced Correlation Coefficient image aligning is way more accurate than the \nORB (Oriented FAST and Rotated BRIEF) method, but also 2-5x slower. But \nsometimes ORB can perform just as well as ECC. Try for yourself.",
    "Display image after exposure fusing" : "After the image has been created and saved, it will be displayed in a python \ninternal viewer window.",
    "Save final image to source folder" : "Save the image to the source folder, e.g. only ask filename",
    "Exposure Weight" : "Sets the relative weight of the \"well exposed\" pixels. These pixels are considered \nbetter exposed as those with high or low luminance levels.",
    "Saturation Weight" : "The saturation criteria favors highly-saturated pixels. (Note that saturation \nis only defined for color pixels.)",
    "Contrast Weight" : "The contrast criteria favors pixels inside a high-contrast neighborhood",
    "Create exposure fused image" : "Merge the different exposures of the same scene into a nice output image using \nthe Mertens-Kautz-Van Reeth exposure fusion algorithm.",
    "Create noise reduced image" : "Noise is random. Blending a stack of multiple images into one will remove the \nrandom pixels. By default the ECC method is used but you can also use ORB.",
}

