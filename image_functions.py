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
from PIL import Image, ExifTags  # to manipulate images and read exif
from PIL.ExifTags import TAGS

import file_functions

# Use 50 mm as stand for focal length
# fl35mm = 50
import PyImageFuser

image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)

# Dictionary holding the translation between tag and tag id
tag_translation = {
    ""
}


def reworkTag(tagtuple, precision):
    '''
    This function returns the value but reformatted in the
    desired numbers after the decimal point

    :param tagtuple:     tuple containing the key and value of the exif tag
    :type tagtuple:      (tuple)
    :param precision:    defines the numbers after the decimal point
    :type precision:     (int)
    '''
    value = round(tagtuple[0] / tagtuple[1], precision)
    # print(v[0], ' # ', v[1], ' => ', value)
    return value


def reworkExposure(tagtuple):
    value = "1/" + str(tagtuple[1] // 10)
    return str(value)


# Read all the exif info from the loaded images, if available
def get_all_exif_info(filename):
    '''
    This function reads all the exif info from the loaded images, if available

    :param filename:   the full path of the filename to retrieve the info from
    :type filename:    (str)
    '''
    exif_dictionary = {}
    reference_image = ""

    img = Image.open(filename)
    exif = img.getexif()
    if exif is not None:
        print('image: ', filename)
        exif_dictionary['filename'] = img.filename
        exif_dictionary['width x height'] = img.size
        for k, v in img.getexif().items():
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
            if (tag == 'ExposureBiasValue'):
                print(TAGS.get(k), ' : ', v)
                #print(tag, ' : ', v)
                if v == '0.0' or v == '0' or v == 0.0 or v == 0:
                   reference_image = filename
                   print('reference_image: ', reference_image)
    else:
        exif_dictionary['no exif'] = 'no exif'

    return reference_image, exif_dictionary


# Read some basic exif info from a file
def get_basic_exif_info_from_file(filename, output):
    exif_dictionary = {}
    reference_image =""   # This image contains the image with Exposure bias value/Exposure compensation 0

    img = Image.open(filename)
    exifd = img.getexif()
    keys = list(exifd.keys())
    exif_dictionary['filename'] = img.filename
    exif_dictionary['width x height'] = img.size
    for k, v in img.getexif().items():
        if (TAGS.get(k) == 'ISOSpeedRatings'):  # ID=0x8827
            # print(TAGS.get(k), " : ", v)
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
        elif (TAGS.get(k) == 'DateTimeOriginal'):  # id=0x9003
            # print(TAGS.get(k), " : ", v)
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
        elif (TAGS.get(k) == 'MaxApertureValue'):  # ID=0x9205
            # print(TAGS.get(k), " : ", reworkTag(v, 1))
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
        elif (TAGS.get(k) == 'FocalLength'):  # id=0x920a
            # print(TAGS.get(k), " : ", reworkTag(v, 1))
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
        elif (TAGS.get(k) == 'FocalLengthIn35mmFilm'):  # id=0xa405
            # print(TAGS.get(k), " : ", v)
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
            # Field of View (FOV) http://www.bobatkins.com/photography/technical/field_of_view.html
            # FOV(rectilinear) = 2 * arctan(framesize / (focal length * 2)) # framesize 36mm, focal length in 35 mm
            FOV = 2 * (math.atan(36 / (v * 2)))
            exif_dictionary['FOV'] = FOV
        elif (TAGS.get(k) == 'ExposureTime'):  # id=0x829a
            # print(TAGS.get(k), " : ", reworkExposure(v))
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
        elif (TAGS.get(k) == 'ExposureBiasValue'):  # id=0x9204
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
            #print("ExposureCompensation\t: ", v)
            if v == '0.0' or v == '0':
                reference_image = filename
                print('reference_image ', reference_image)
        elif (TAGS.get(k) == 'FNumber'):  # id=0x829d
            # print(TAGS.get(k), " : ", reworkTag(v, 1))
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
        elif (TAGS.get(k) == 'Orientation'):  # id=0x274d
            tag = TAGS.get(k)
            exif_dictionary[tag] = v
            #print(TAGS.get(k), " : ", v)

    if (output == 'print'):
        print('\n\n', exif_dictionary)
        # print("\n\n",exif_dictionary['ExposureBiasValue'])

    return reference_image, exif_dictionary


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
        # previewfile = os.path.join(tmpfolder, os.path.splitext(file)[0] + ".jpg")
        previewfile = os.path.join(tmpfolder, file)

        if not os.path.exists(previewfile):  # This means that the preview file does not exist yet
            print("previewfile: ", previewfile, " does not exist yet")
            if platform.system() == 'Windows':
                img += "\"" + nfile.replace("/", "\\") + "\" "
            else:
                img += "\"" + nfile + "\" "
            try:
                preview_img = Image.open(nfile)
                exifd = preview_img.getexif()  # Get all exif data from original image
                sg.user_settings_filename(path=Path.home())
                longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
                preview_img.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
                # Get necessary tags and write them to resized images
                # for k, v in preview_img.getexif().items():
                preview_img.save(previewfile, "JPEG", exif=exifd)  # Save all exif data from original to resized image
            except Exception as e:
                failed += PyImageFuser.logger(e) + '\n'  # get the error from the logger
                preview_img.save(previewfile, "JPEG")
                # pass
            images.append(previewfile)
        else:  # They do exist but we still need to populate or images list
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
            org_img = Image.open(orgfile)
            exifd = org_img.getexif()  # Get all exif data from original image
            sg.user_settings_filename(path=Path.home())
            longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
            org_img.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
            # Get necessary tags and write them to resized images
            # for k, v in preview_img.getexif().items():
            org_img.save(previewfile, "JPEG", exif=exifd)  # Save all exif data from original to resized image
        except Exception as e:
            PyImageFuser.logger(e)
            # pass


def check_ais_params(all_values):
    '''
    This function parses all align_image_stack settings and returns them
    to the create_ais_command

    :param all_values:   This is the dictionary containing all UI key variables
    :type all_values:    (Dict[Any, Any]) - {Element_key : value}
    '''
    cmd_string = ""
    cmd_list = []
    # print('autoCrop ',all_values['_autoCrop_'] )
    if all_values['_autoCrop_']:
        cmd_string += '-C '
        cmd_list.append('-C')
    if all_values['_useGPU_']:
        cmd_string += '--gpu  '
        # cmd_list.append('--gpu')
    if all_values['_fffImages_']:
        cmd_string += '-e '
        cmd_list.append('-e')
    if all_values['_fovOptimize_']:
        cmd_string += '-m '
        cmd_list.append('-m')
    if all_values['_optimizeImgCenter_']:
        cmd_string += '-i '
        cmd_list.append('-i')
    if all_values['_optimizeRadialDistortion_']:
        cmd_string += '-d '
        cmd_list.append('-d')
    #if all_values['_linImages_']:
    #    cmd_string += '-l '
    #    cmd_list.append('-l')
    if not all_values['_autoHfov']:
        cmd_string += '-f ' + all_values['_inHFOV_'] + ' '
        cmd_list.append('-f')
        cmd_list.append(all_values['_inHFOV_'])
    if not all_values['_inNoCP_'] == '8':
        cmd_string += '-c ' + all_values['_inNoCP_'] + ' '
        cmd_list.append('-c')
        cmd_list.append(all_values['_inNoCP_'])
    if not all_values['_removeCPerror_'] == '3':
        cmd_string += '-t ' + all_values['_removeCPerror_'] + ' '
        cmd_list.append('-t')
        cmd_list.append(all_values['_removeCPerror_'])
    if not all_values['_inScaleDown_'] == '1':
        cmd_string += '-s ' + all_values['_inScaleDown_'] + ' '
        cmd_list.append('-s')
        cmd_list.append(all_values['_inScaleDown_'])
    if not all_values['_inGridsize_'] == '5':
        cmd_string += '-g ' + all_values['_inGridsize_'] + ' '
        cmd_list.append('-g')
        cmd_list.append(all_values['_inGridsize_'])

    return cmd_string, cmd_list


# This function creates the basic align_image)stack command for the several options
# It uses the string from check_ais_params to complete the command string
def create_ais_command(all_values, folder, tmpfolder, type):
    '''
    This function creates the basic align_image)stack command for the several options
    It uses the string/list from check_ais_params to complete the command string

    :param all_values:   This is the dictionary containing all UI key variables
    :type all_values:    (Dict[Any, Any]) - {Element_key : value}
    '''
    cmd_string = ""
    cmd_list = []

    file_functions.remove_files(os.path.join(tmpfolder, '*ais*'))
    if platform.system() == 'Windows':
        #cmd_string = file_functions.resource_path(os.path.join('enfuse_ais', 'align_image_stack.exe'))
        cmd_string = os.path.join(os.path.realpath('.'), 'enfuse_ais', 'align_image_stack.exe')
        ais_string = cmd_string
    else:
        #cmd_string = file_functions.resource_path(os.path.join('enfuse_ais', 'usr', 'bin', 'align_image_stack'))
        check_pyinstaller =getattr (sys, '_MEIPASS', 'NotRunningInPyInstaller')
        if check_pyinstaller == 'NotRunningInPyInstaller': # we run from the script and assume enfuse and align_image_stack are in the PATH
            cmd_string = 'align_image_stack'
        else:
            cmd_string = os.path.join(os.path.realpath('.'), 'enfuse_ais', 'usr', 'bin', 'align_image_stack')

        #ais_string = cmd_string
    if (type == 'preview'):
        # cmd_string = 'align_image_stack --gpu -a ' + os.path.join(tmpfolder,'preview_ais_001') + ' -v -t 2 -C -i '
        cmd_string += ' -a ' + os.path.join(tmpfolder, 'preview_ais_001') + ' '
        # cmd_list.append('--gpu')
        cmd_list.append('-a')
        cmd_list.append(os.path.join(tmpfolder, 'preview_ais_001'))
    else:
        cmd_string += ' -a ' + os.path.join(tmpfolder, 'ais_001') + ' '
        cmd_list.append('-a')
        cmd_list.append(os.path.join(tmpfolder, 'ais_001'))
    tmp_string, tmp_list = check_ais_params(all_values)
    cmd_string += tmp_string
    cmd_list.extend(tmp_list)

    files = all_values['-FILE LIST-']
    for file in files:
        if type == 'preview':
            nfile = os.path.join(tmpfolder, file)
        else:
            nfile = os.path.join(folder, file)
        if platform.system() == 'Windows':
            cmd_string += "\"" + nfile.replace("/", "\\") + "\" "
            # cmd_list.append("\"" + nfile.replace("/", "\\") + "\" ")
            cmd_list.append(nfile.replace("/", "\\"))
        else:
            cmd_string += "\"" + nfile + "\" "
            cmd_list.append(nfile)
    # print("\n\n", cmd_string, "\n\n")
    # return cmd_string, cmd_list
    if platform.system() == 'Windows':
        return ais_string, cmd_list
    else:
        return cmd_string, cmd_list


# This function parses all enfuse settings and returns them
# to the create_enfuse_command
def check_enfuse_params(all_values):
    cmd_string = ""
    cmd_list = []
    if not all_values['_levels_'] == '29':
        cmd_string += '--levels=' + str(int(all_values['_levels_'])) + ' '
        cmd_list.append('--levels=' + str(int(all_values['_levels_'])))
    if not all_values['_exposure_weight_'] == '1.0':
        cmd_string += '--exposure-weight=' + str(all_values['_exposure_weight_']) + ' '
        cmd_list.append('--exposure-weight=' + str(all_values['_exposure_weight_']))
    if not all_values['_saturation_weight_'] == '0.2':
        cmd_string += '--saturation-weight=' + str(all_values['_saturation_weight_']) + ' '
        cmd_list.append('--saturation-weight=' + str(all_values['_saturation_weight_']))
    if not all_values['_contrast_weight_'] == '0':
        cmd_string += '--contrast-weight=' + str(all_values['_contrast_weight_']) + ' '
        cmd_list.append('--contrast-weight=' + str(all_values['_contrast_weight_']))
    if not all_values['_entropy_weight_'] == '0':
        cmd_string += '--entropy-weight=' + str(all_values['_entropy_weight_']) + ' '
        cmd_list.append('--entropy-weight=' + str(all_values['_entropy_weight_']))
    if not all_values['_exposure_optimum_'] == '0.5':
        cmd_string += '--exposure-optimum=' + str(all_values['_exposure_optimum_']) + ' '
        cmd_list.append('--exposure-optimum=' + str(all_values['_exposure_optimum_']))
    if not all_values['_exposure_width_'] == '0.2':
        cmd_string += '--exposure-width=' + str(all_values['_exposure_width_']) + ' '
        cmd_list.append('--exposure-width=' + str(all_values['_exposure_width_']))
    return cmd_string, cmd_list


def check_enfuse_output_format(all_values):
    cmd_string = ""
    cmd_list = []
    if all_values['_jpg_']:
        if all_values['_jpgCompression_'] == 90:
            cmd_string += '--compression=90 '
            cmd_list.append('--compression=90')
        else:
            cmd_string += '--compression=' + str(int(all_values['_jpgCompression_'])) + ' '
            cmd_list.append('--compression=' + str(int(all_values['_jpgCompression_'])))
    else:  # User selected tiff output
        cmd_string += '--compression=' + all_values['_tiffCompression'] + ' --depth='
        if all_values['_tiff8_']:
            cmd_string += '8 '
        elif all_values['_tif16_']:
            cmd_string += '16 '
        else:
            cmd_string += '32 '
    return cmd_string, cmd_list


def create_enfuse_command(all_values, folder, tmpfolder, type, newImageFileName):
    cmd_string = ""
    cmd_list = []
    enf_string = ""
    if platform.system() == 'Windows':
        #cmd_string = file_functions.resource_path(os.path.join('enfuse_ais', 'enfuse.exe'))
        cmd_string = os.path.join(os.path.realpath('.'), 'enfuse_ais', 'enfuse.exe')
        enf_string = cmd_string
    else:
        #cmd_string = file_functions.resource_path(os.path.join('enfuse_ais', 'usr', 'bin', 'enfuse'))
        check_pyinstaller =getattr (sys, '_MEIPASS', 'NotRunningInPyInstaller')
        if check_pyinstaller == 'NotRunningInPyInstaller': # we run from the script and assume enfuse is in the PATH
            cmd_string = 'enfuse'
        else:
            cmd_string = os.path.join(os.path.realpath('.'), 'enfuse_ais', 'usr', 'bin', 'enfuse')
    if type == 'preview_ais':
        cmd_string += ' -v --compression=90 ' + os.path.join(tmpfolder, 'preview_ais_001*') + ' -o ' + os.path.join(tmpfolder, 'preview.jpg ')
        cmd_list.append('-v')
        cmd_list.append('--compression=90')
        cmd_list.append('-o')
        cmd_list.append(os.path.join(tmpfolder, 'preview.jpg'))
        cmd_list.append(os.path.join(tmpfolder, 'preview_ais_001*'))
    elif type == 'preview':
        cmd_string += ' -v --compression=90 ' + ' -o ' + os.path.join(tmpfolder, 'preview.jpg ')
        cmd_list.append('-v')
        cmd_list.append('--compression=90')
        cmd_list.append(os.path.join(tmpfolder, 'preview.jpg'))
        files = all_values['-FILE LIST-']
        for file in files:
            nfile = os.path.join(tmpfolder, file)
            if platform.system() == 'Windows':
                cmd_string += "\"" + nfile.replace("/", "\\") + "\" "
                cmd_list.append(nfile.replace("/", "\\"))
            else:
                cmd_string += "\"" + nfile + "\" "
        # print("\n\n", cmd_string, "\n\n")
    elif type == 'full_ais':
        cmd_string += ' -v ' + os.path.join(tmpfolder, 'ais_001*') + ' -o "' + newImageFileName + '" '
        cmd_list.append('-v')
        cmd_list.append('-o')
        cmd_list.append(newImageFileName)
        cmd_list.append(os.path.join(tmpfolder, 'ais_001*'))
        # Check enfuse file output format
        # cmd_string += check_enfuse_output_format(all_values)
        tmp_string, tmp_list = check_enfuse_output_format(all_values)
        cmd_string += tmp_string
        cmd_list.extend(tmp_list)
    else:  # full enfuse without ais
        # cmd_string = 'enfuse -v --level=29 --compression=90 ' + ' -o ' + newImageFileName
        cmd_string += ' -v ' + ' -o "' + newImageFileName + '" '
        cmd_list.append('-v')
        cmd_list.append('-o')
        cmd_list.append(newImageFileName)
        # Check enfuse file output format
        # cmd_string += check_enfuse_output_format(all_values)
        tmp_string, tmp_list = check_enfuse_output_format(all_values)
        cmd_string += tmp_string
        cmd_list.extend(tmp_list)
        files = all_values['-FILE LIST-']
        for file in files:
            nfile = os.path.join(folder, file)
            if platform.system() == 'Windows':
                cmd_string += "\"" + nfile.replace("/", "\\") + "\" "
                cmd_list.append(nfile.replace("/", "\\"))
            else:
                cmd_string += "\"" + nfile + "\" "
        # print("\n\n", cmd_string, "\n\n")
    # Finally add our enfuse params
    tmp_string, tmp_list = check_enfuse_params(all_values)
    if platform.system() == 'Windows':
        cmd_string = tmp_string
    else:
        cmd_string += tmp_string
    cmd_list.extend(tmp_list)
    print('finale end create_enfuse_command')
    print('cmd_string ', cmd_string)
    print('cmd_list ', cmd_list)

    # return cmd_string
    if platform.system() == 'Windows':
        return enf_string, cmd_list
    else:
        return cmd_string, cmd_list


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
    root.destroy()  # do not forget to delete the tk window
    return int(width), int(height)


def display_preview(mainwindow, imgfile):
    try:
        # imgfile = os.path.join(folder, values['-FILE LIST-'][0])
        # image_functions.get_basic_exif_info(imgfile, 'print')
        # print("\n\nimgfile ", imgfile)
        image = Image.open(imgfile)
        image = reorient_img(image)
        sg.user_settings_filename(path=Path.home())
        longestSide = int(sg.user_settings_get_entry('last_size_chosen', '480'))
        image.thumbnail((longestSide, longestSide), Image.ANTIALIAS)
        bio = io.BytesIO()
        image.save(bio, format='PNG')
        mainwindow['-IMAGE-'].update(data=bio.getvalue())
    except:
        # print("Something went wrong converting ", imgfile)
        pass
    # exif_table = image_functions.get_basic_exif_info(imgfile, 'print')


# This displays the final image in the default viewer
def displayImage(imgpath):
    rawimgpath = str(imgpath)
    newImg = Image.open(rawimgpath)
    newImg.show()

def reorient_img(pil_img):
    img_exif = pil_img.getexif()

    if len(img_exif):
        if img_exif[274] == 3:
            pil_img = pil_img.transpose(Image.ROTATE_180)
        elif img_exif[274] == 6:
            pil_img = pil_img.transpose(Image.ROTATE_270)
        elif img_exif[274] == 8:
            pil_img = pil_img.transpose(Image.ROTATE_90)

    return pil_img

def displayImageWindow(imgpath):
    # If the user did not specify a file name extension, the program added ".jpg"
    '''
    basename, extension = os.path.splitext(imgpath)
    ext = extension.lower()
    if ext == '' or len(ext) == 0:
        rawimgpath = str(imgpath + '.jpg')
    else:
        rawimgpath = str(imgpath)
    print('displaying your image: ', rawimgpath, '\n')
    '''
    tmpImg = Image.open(str(imgpath))
    newImg = reorient_img(tmpImg)
    # imgsize = newImg.size
    scrwidth, scrheight = get_curr_screen_geometry()
    # print('scrwidth x scrheight: ' + str(scrwidth) + 'x' + str(scrheight))
    # 4k is 3840 x 2160, HD is 1920 x 18080
    if scrwidth >= 1920 and scrwidth < 3840:
        scrwidth = 1860
        scrheight = 1026
    newImg.thumbnail((scrwidth, scrheight), Image.ANTIALIAS)
    bio = io.BytesIO()
    newImg.save(bio, format='PNG')
    layout = [
        [sg.Image(bio.getvalue(), key='-IMAGE-')],
        [sg.Button('Exit', visible=False, key='-exit-')]  # invisible button necessary to allow windows read
    ]
    window = sg.Window('Your image: ' + imgpath, layout, no_titlebar=False, location=(0, 0), size=(scrwidth, scrheight),
                       keep_on_top=True, icon=get_icon())

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, '-exit-'):
            break
    window.close


def get_icon():
    '''
    This function adds the program icon to the top-left of the displayed windows and popups
    '''
    if platform.system() == 'Windows':
        wicon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'logo.ico')
    else:
        wicon = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'logo.png')

    return wicon


def get_filename_images(values, folder):
    '''
    This functions requests the filename and possible folder where to save
    the to be created image file.
    Next to that the path will be derived from the folder where the images reside

    :param values:          This is the dictionary containing all UI key variables
    :type values:           (Dict[Any, Any]) - {Element_key : value}
    :param folder:          The folder that contains the full size original images
    :type folder:           (list)
    '''
    full_images = []

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
        files = values['-FILE LIST-']
        for file in files:
            full_images.append(os.path.join(folder, file))

    return folderFileName[1], full_images

def copy_exif_info(reference_image, imagepath):

    print('reference_image ', reference_image)
    print('imagepath ', imagepath)
    ref_img = Image.open(reference_image)
    ref_exifd = ref_img.getexif()
    ref_img.close()
    pil_img = Image.open(imagepath)
    pil_img.save(imagepath, "JPEG", exif=ref_exifd)
    pil_img.close()
    '''
    rot_img = Image.open(imagepath)
    img_exif = rot_img.getexif()

    if len(img_exif):
        print('img_exif[274] ', img_exif[274])
        if img_exif[274] == 3:
            pil_img = pil_img.transpose(Image.ROTATE_180)
        elif img_exif[274] == 6:
            pil_img = pil_img.transpose(Image.ROTATE_270)
        elif img_exif[274] == 8:
            pil_img = pil_img.transpose(Image.ROTATE_90)

        pil_img.save(imagepath)
        pil_img.close()
    #return pil_img

    try:
        image = Image.open(imagepath)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break
        exif = dict(image._getexif().items())

        if exif[orientation] == 3:
            image = image.transpose(Image.ROTATE_180)
        elif exif[orientation] == 6:
            image = image.transpose(Image.ROTATE_270)
        elif exif[orientation] == 8:
            image = image.transpose(Image.ROTATE_90)
        image.save(imagepath)
        image.close()

    except (AttributeError, KeyError, IndexError):
        # cases: image don't have getexif
        print('No exif data?')
        pass
    '''