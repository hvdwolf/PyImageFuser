# -*- coding: utf-8 -*-

# image_functions.py
# This helper file does image manipulation and display

# Copyright (c) 2022, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import io, os, math, platform, sys, tempfile
from pathlib import Path
import tkinter as tk
import PySimpleGUI as sg
from PIL import Image # to manipulate images and read exif
from PIL.ExifTags import TAGS
import cv2
import numpy as np
import file_functions

# Use 50 mm as stand for focal length
#fl35mm = 50
import PyImageFuser

image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)

# Dictionary holding the translation between tag and tag id
tag_translation = {
    ""
}

def reworkTag(tagtuple, precision):
    value = round (tagtuple[0] / tagtuple[1], precision)
    #print(v[0], ' # ', v[1], ' => ', value)
    return value

def reworkExposure(tagtuple):
    value = "1/" + str(tagtuple[1] // 10)
    return value

# Read all the exif info from the loaded images, if available
def get_all_exif_info(filename):
    exif_dictionary = {}

    img = Image.open(filename)
    exif = img.getexif()
    if exif is not None:
        exif_dictionary['filename'] = img.filename
        exif_dictionary['width x height'] = img.size
        for k, v in img.getexif().items():
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
    else:
        exif_dictionary['no exif'] = 'no exif'

    return exif_dictionary

# Read some basic exif info from a file
def get_basic_exif_info_from_file(filename, output):
    exif_dictionary={}
    correctedfocal = 50

    img=Image.open(filename)
    exifd = img.getexif()
    keys = list(exifd.keys())
    exif_dictionary['filename'] = img.filename
    exif_dictionary['width x height'] = img.size
    for k, v in img.getexif().items():
        if (TAGS.get(k) == 'ISOSpeedRatings'): #ID=0x8827
            #print(TAGS.get(k), " : ", v)
            tag=TAGS.get(k)
            exif_dictionary[tag]=v
        elif (TAGS.get(k) == 'DateTimeOriginal'): # id=0x9003
            #print(TAGS.get(k), " : ", v)
            tag=TAGS.get(k)
            exif_dictionary[tag]=v
        elif (TAGS.get(k) == 'MaxApertureValue'): # ID=0x9205
            #print(TAGS.get(k), " : ", reworkTag(v, 1))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkTag(v, 1)
        elif (TAGS.get(k) == 'FocalLength'): # id=0x920a
            #print(TAGS.get(k), " : ", reworkTag(v, 1))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkTag(v, 1)
        elif (TAGS.get(k)  == 'FocalLengthIn35mmFilm'): # id=0xa405
            #print(TAGS.get(k), " : ", v)
            tag=TAGS.get(k)
            exif_dictionary[tag]=v
            # Field of View (FOV) http://www.bobatkins.com/photography/technical/field_of_view.html
            # FOV(rectilinear) = 2 * arctan(framesize / (focal length * 2)) # framesize 36mm, focal length in 35 mm
            FOV = 2 * (math.atan(36 / (v * 2)))
            exif_dictionary['FOV'] = FOV
        elif (TAGS.get(k) == 'ExposureTime'): # id=0x829a
            #print(TAGS.get(k), " : ", reworkExposure(v))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkExposure(v)
        elif (TAGS.get(k) == 'ExposureBiasValue'): # id=0x9204
            #print("ExposureCompensation\t: ", reworkTag(v, 1))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkTag(v, 1)
        elif (TAGS.get(k) == 'FNumber'): # id=0x829d
            #print(TAGS.get(k), " : ", reworkTag(v, 1))
            tag=TAGS.get(k)
            exif_dictionary[tag]=reworkTag(v, 1)


    if (output == 'print'):
        print('\n\n',exif_dictionary)
        #print("\n\n",exif_dictionary['ExposureBiasValue'])

    return exif_dictionary


# This function resizes the original selected images when
# the user clicks on "create preview" or "create enfused image"
def resizetopreview(all_values, folder, tmpfolder):
    '''
    This function resizes the original selected images when
    the user clicks on "create preview" or "create fused image"

    :param all_values:    The values from the Gui elements
    :type all_values:     (Dict[Any, Any]) - {Element_key : value}
    :param folder:        The folder holding the original images
    :type folder:         (str)
    :param tmpfolder:     The dynamically created work folder in the OS temp folder
    :type tmpfolder:      (str)
    '''
    img = ""
    failed = ""
    images = []

    files = all_values['-FILE LIST-']
    for file in files:
        nfile = os.path.join(folder, file)
        #previewfile = os.path.join(tmpfolder, os.path.splitext(file)[0] + ".jpg")
        previewfile = os.path.join(tmpfolder,file)

        if not os.path.exists(previewfile): # This means that the preview file does not exist yet
            print("previewfile: ", previewfile, " does not exist yet")
            if platform.system() == 'Windows':
                img += "\"" + nfile.replace("/", "\\") + "\" "
            else:
                img += "\"" + nfile + "\" "
            try:
                preview_img = Image.open(nfile)
                exifd = preview_img.getexif() # Get all exif data from original image
                sg.user_settings_filename(path=Path.home())
                longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
                preview_img.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
                # Get necessary tags and write them to resized images
                #for k, v in preview_img.getexif().items():
                preview_img.save(previewfile, "JPEG", exif=exifd) # Save all exif data from original to resized image
            except Exception as e:
                failed += PyImageFuser.logger(e) + '\n' # get the error from the logger
                preview_img.save(previewfile, "JPEG")
                #pass
            images.append(previewfile)
        else: # They do exist but we still need to populate or images list
            images.append(previewfile)
    return failed, images

def resizesingletopreview(folder, tmpfolder, image):
    img = ""

    previewfile = os.path.join(tmpfolder, image)
    orgfile = os.path.join(folder, image)
    print('previewfile ' + previewfile + '; orgfile ' + orgfile)
    if not os.path.exists(previewfile):  # This means that the preview file does not exist yet
        print("previewfile: ", previewfile, " does not exist yet")
        if platform.system() == 'Windows':
            img += "\"" + orgfile.replace("/", "\\") + "\" "
        else:
            img += "\"" + orgfile + "\" "
        try:
            preview_img = Image.open(orgfile)
            exifd = preview_img.getexif()  # Get all exif data from original image
            sg.user_settings_filename(path=Path.home())
            longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
            preview_img.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
            # Get necessary tags and write them to resized images
            # for k, v in preview_img.getexif().items():
            preview_img.save(previewfile, "JPEG", exif=exifd)  # Save all exif data from original to resized image
        except Exception as e:
            PyImageFuser.logger(e)
            # pass

def get_curr_screen_geometry():
    """
    Get the size of the current screen in a multi-screen setup.

    Returns:
        geometry (str): The standard Tk geometry string.
            [width]x[height]+[left]+[top]

    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    geometry = root.winfo_geometry()
    root.destroy()
    return geometry
    """
    # Do not use above. It might function better in a multi window environment
    # but shows a gray full screen window for a moment
    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy() # do not forget to delete the tk window
    return int(width), int(height)

def display_preview(mainwindow, imgfile):
    try:
        #imgfile = os.path.join(folder, values['-FILE LIST-'][0])
        # image_functions.get_basic_exif_info(imgfile, 'print')
        #print("\n\nimgfile ", imgfile)
        image = Image.open(imgfile)
        sg.user_settings_filename(path=Path.home())
        longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
        image.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        mainwindow['-IMAGE-'].update(data=bio.getvalue())
    except:
        # print("Something went wrong converting ", imgfile)
        pass
    #exif_table = image_functions.get_basic_exif_info(imgfile, 'print')

# This displays the final image in the default viewer
def displayImage(imgpath):

    rawimgpath = str(imgpath)
    newImg = Image.open(rawimgpath)
    newImg.show()

def displayImageWindow(imgpath):

    rawimgpath = str(imgpath)
    print('displaying your image: ', rawimgpath, '\n')
    newImg = Image.open(rawimgpath)
    #imgsize = newImg.size
    scrwidth, scrheight = get_curr_screen_geometry()
    #print('scrwidth x scrheight: ' + str(scrwidth) + 'x' + str(scrheight))
    # 4k is 3840 x 2160, HD is 1920 x 18080
    if scrwidth >= 1920 and scrwidth < 3840:
        scrwidth = 1860
        scrheight = 1026
    newImg.thumbnail((scrwidth, scrheight), Image.ANTIALIAS)
    bio = io.BytesIO()
    newImg.save(bio, format='PNG')
    layout = [
        [sg.Image(bio.getvalue(),key='-IMAGE-')],
        [sg.Button('Exit', visible=False, key='-exit-')] # invisible button necessary to allow windows read
    ]
    window = sg.Window('Your image: ' + imgpath, layout, no_titlebar=False, location=(0,0), size=(scrwidth,scrheight), keep_on_top=True, icon=get_icon())

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED,'-exit-'):
            break
    window.close

# This function adds the program icon to the top-left of the displayed windows and popups
def get_icon():
    if platform.system() == 'Windows':
        wicon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','logo.ico')
    else:
        wicon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','logo.png')

    return wicon


def get_filename_images(values, folder):
    if values['_saveToSource_']:
        folderFileName = file_functions.getFileName(folder)  # user wants to save image to same folder
    else:
        folderFileName = file_functions.getFileName('')  # user wants to select new folder
    if folderFileName[0] != '' and folderFileName[0] != folder:
        folder = folderFileName[0]
    if folderFileName[1] == '':
        sg.popup('Error! no filename provided!', 'You did not provide a filename.\n',
                 'The program can\'t create an image without a filename.', icon=get_icon())
    elif folderFileName[1] == 'Cancel':
        print('user Cancelled')
    else:
        full_images = []
        files = values['-FILE LIST-']
        for file in files:
            full_images.append(os.path.join(folder, file))

    return folderFileName[1], full_images

# Mostly copied from https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
def align_fuse(all_values, images, tmpfolder, filename_type, align_YN):
    """
    This function uses the opencv options to align (optionally, but default)
    and then exposure fuse the images
    the images are either the resized images for the preview, or the full images for the final result

    :param all_values:      This is the dictionary containing all UI key variables
    :type all_values:       (Dict[Any, Any]) - {Element_key : value}
    :param images:          The images to (optionally) align and fuse
    :type images:           (list)
    :param tmpfolder:       The dynamically created work folder in the OS temp folder
    :type tmpfolder:        (str)
    :param filename_type:   Either the real final filename or a string 'preview'
    :type filename_type:    (str)
    :param align_YN:        Determines whether the user wants to align (default) or not
    :type align_YN:         (bool)
    """
    work_images = []
    processed_images = None
    #processed_work_images = []
    for image in images:
        im = cv2.imread(image)
        work_images.append(im)

    if align_YN: # True
        if filename_type == 'preview':
            print("Aligning preview images ...\n")
        else:
            print("Aligning full size images ...\n")
        alignMTB = cv2.createAlignMTB()
        alignMTB.process(work_images, work_images)

    print("\nMerging using Exposure Fusion ...\n")
    mergeMertens = cv2.createMergeMertens()
    mergeMertens.setContrastWeight(all_values['_contrast_weight_'])
    mergeMertens.setExposureWeight(all_values['_exposure_weight_'])
    mergeMertens.setSaturationWeight(all_values['_saturation_weight_'])
    exposureFusion = mergeMertens.process(work_images)
    #exposureFusion = mergeMertens.process(processed_images)
    if filename_type == 'preview':
        print("\nSaving preview image ...\n")
        cv2.imwrite(os.path.join(tmpfolder, 'preview.jpg'), exposureFusion * 255, [int(cv2.IMWRITE_JPEG_QUALITY), int(all_values['_jpgCompression_'])]) # * 255 to get an 8-bit image
    else:
        print("\nSaving finale fused image ...\n")
        cv2.imwrite(str(filename_type), exposureFusion * 255, [int(cv2.IMWRITE_JPEG_QUALITY), int(all_values['_jpgCompression_'])]) # * 255 to get an 8-bit image; jpg_quality=(int)quality?

# Mostly copied from https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
# but removed the inferior createAlignMTB() and replaced that with the ECC method
def exposure_fuse(all_values, images, tmpfolder, filename_type):
    """
    This function uses the opencv options to exposure fuse the images
    the images are either the resized images for the preview, or the full images for the final result

    :param all_values:      This is the dictionary containing all UI key variables
    :type all_values:       (Dict[Any, Any]) - {Element_key : value}
    :param images:          The images to (optionally) align and fuse
    :type images:           (list)
    :param tmpfolder:       The dynamically create work folder in the OS temp folder
    :type tmpfolder:        (str)
    :param filename_type:   Either the real final filename or a string 'preview'
    :type filename_type:    (str)
    """
    work_images = []
    processed_images = None
    #processed_work_images = []
    for image in images:
        im = cv2.imread(image)
        work_images.append(im)

    print("\nMerging using Exposure Fusion ...\n")
    mergeMertens = cv2.createMergeMertens()
    mergeMertens.setContrastWeight(all_values['_contrast_weight_'])
    mergeMertens.setExposureWeight(all_values['_exposure_weight_'])
    mergeMertens.setSaturationWeight(all_values['_saturation_weight_'])
    exposureFusion = mergeMertens.process(work_images)
    #exposureFusion = mergeMertens.process(processed_images)
    if filename_type == 'preview':
        print("\nSaving preview image ...\n")
        cv2.imwrite(os.path.join(tmpfolder, 'preview.jpg'), exposureFusion * 255, [int(cv2.IMWRITE_JPEG_QUALITY), int(all_values['_jpgCompression_'])]) # * 255 to get an 8-bit image
    else:
        print("\nSaving finale fused image ...\n")
        cv2.imwrite(str(filename_type), exposureFusion * 255, [int(cv2.IMWRITE_JPEG_QUALITY), int(all_values['_jpgCompression_'])]) # * 255 to get an 8-bit image; jpg_quality=(int)quality?
