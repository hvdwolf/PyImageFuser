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
    paramwindow.refresh()
    paramwindow.move(100,50)
    move_window_to_center(paramwindow)
    paramwindow['_updater_'].click()

    while True:
        event, values = paramwindow.Read()
        if event == sg.WIN_CLOSED or event == 'OK':
            break
        elif event == '_updater_':
            paramwindow.move(100, 50)
            paramwindow.refresh()
    paramwindow.close()



# Below are program texts
resize_warning_message = '''Something went wrong with resizing. Mostly this is due to missing exif info in your
images or due to incorrect exif info in your images.\n\n
The errors are displayed below:'''

resize_error_message = '''Something went really wrong with resizing.
The program can\'t continue. Please check your images carefully.'''

about_message = 'About PyImageFuser, Version ' + Version + '\n\n'
about_message += 'PyImageFuser can be used for exposure bracketing, noise reduction and focus stacking.\n\n'
about_message += 'PyImageFuser is built using Python3 and PySimpleGui.\n'
about_message += 'PyImageFuser uses the external tools enfuse and align_image_stack.\n\n'
about_message += 'PyImageFuser is released under GPL v3.\n'
about_message += 'enfuse and align_image_stack are released under GPL v2.\n'
about_message += 'You should find the license with this software.\n\n'
about_message += 'Author: Harry van der Wolf.'

Credits =  '''Credits:\n\n
Used packages:
- Python3 (with included modules/packages)
- tkinter
- PySimpleGUI
- PIL (pillow)

Used code (Thanks to the writers):
- align_image_stack by Pablo d'Angelo. Also contains contributions from:
  Douglas Wilkins, Ippei Ukai, Ed Halley, Bruno Postle, Gerry Patterson and Brent Townshend.  
  Stereo functionality added by Vladimir Nadvornik. 
  
- enfuse by by Andrew Mihal, Christoph Spiel and others.
'''

# Add a \n every max. 78 characters
Explain_parameters = {
    "Always align images" : "Even on a tripod you might have minimal movement causing misalignment and therefore unsharp blended images.\nAligning them will improve sharpness, using either alignMTB or ECC.",
    "Display image after exposure fusing" : "After the image has been created and saved, it will be displayed in a python internal viewer window.",
    "Save final image to source folder" : "Save the image to the source folder, e.g. only ask filename",
    "Create exposure fused image" : "Merge the different exposures of the same scene into a better exposed image",
}


### And just for reference
id_tag_dict = ([
    (0x36864, 'ExifVersion'),
    (0x37121, 'ComponentsConfiguration'),
    (0x37122, 'CompressedBitsPerPixel'),
    (0x36867, 'DateTimeOriginal'),
    (0x36868, 'DateTimeDigitized'),
    (0x37380, 'ExposureBiasValue'),
    (0x37381, 'MaxApertureValue'),
    (0x37383, 'MeteringMode'),
    (0x37384, 'LightSource'),
    (0x37385, 'Flash'),
    (0x37386, 'FocalLength'),
    (0x40961, 'ColorSpace'),
    (0x40962, 'ExifImageWidth'),
    (0x40965, 'ExifInteroperabilityOffset'),
    (0x41989, 'FocalLengthIn35mmFilm'),
    (0x41990, 'SceneCaptureType'),
    (0x37520, 'SubsecTime'),
    (0x37521, 'SubsecTimeOriginal'),
    (0x37522, 'SubsecTimeDigitized'),
    (0x40963, 'ExifImageHeight'),
    (0x11, 'ProcessingSoftware'),
    (0x270, 'ImageDescription'),
    (0x271, 'Make'),
    (0x41495, 'SensingMethod'),
    (0x272, 'Model'),
    (0x41728, 'FileSource'),
    (0x33434, 'ExposureTime'),
    (0x282, 'XResolution'),
    (0x531, 'YCbCrPositioning'),
    (0x33437, 'FNumber'),
    (0x41729, 'SceneType'),
    (0x33432, 'Copyright'),
    (0x283, 'YResolution'),
    (0x34850, 'ExposureProgram'),
    (0x34853, 'GPSInfo'),
    (0x41985, 'CustomRendered'),
    (0x34855, 'ISOSpeedRatings'),
    (0x296, 'ResolutionUnit'),
    (0x50341, 'PrintImageMatching'),
    (0x41986, 'ExposureMode'),
    (0x40960, 'FlashPixVersion'),
    (0x34864, 'None'),
    (0x41987, 'WhiteBalance'),
    (0x305, 'Software'),
    (0x306, 'DateTime'),
    (0x41988, 'DigitalZoomRatio'),
    (0x315, 'Artist'),
    (0x41991, 'GainControl'),
    (0x41992, 'Contrast'),
    (0x41993, 'Saturation'),
    (0x50898, 'None'),
    (0x41994, 'Sharpness'),
    (0x50899, 'None'),
    (0x274, 'Orientation'),
    (0x34665, 'ExifOffset'),
    (0x37500, 'MakerNote'),
])

