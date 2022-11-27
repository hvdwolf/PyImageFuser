# -*- coding: utf-8 -*-

# ais_enfuse.py
# This helper file does the align_image_stack and enfuse functionality

# Copyright (c) 2022, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import os, platform, sys

import file_functions


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
        cmd_list.append('--gpu')
    if all_values['_fffImages_']:
        cmd_string += '-e '
        cmd_list.append('-e')
    if all_values['_usegivenorder_']:
        cmd_string += '--use-given-order '
        cmd_list.append('--use-given-order')
    if all_values['_OptimizeFOV_']:
        cmd_string += '-m '
        cmd_list.append('-m')
    if all_values['_optimizeImgCenter_']:
        cmd_string += '-i '
        cmd_list.append('-i')
    if all_values['_optimizeRadialDistortion_']:
        cmd_string += '-d '
        cmd_list.append('-d')
    if all_values['_optimixeXposition_']:
        cmd_string += '-x '
        cmd_list.append('-x')
    if all_values['_optimixeYposition_']:
        cmd_string += '-y '
        cmd_list.append('-y')
    if all_values['_optimixeZposition_']:
        cmd_string += '-z '
        cmd_list.append('-z')
    #if all_values['_linImages_']:
    #    cmd_string += '-l '
    #    cmd_list.append('-l')
    if not all_values['_autoHfov']:
        cmd_string += '-f ' + all_values['_inHFOV_'] + ' '
        cmd_list.append('-f')
        cmd_list.append(all_values['_inHFOV_'])
    if not all_values['_correlation_'] == '0.9':
        cmd_string += '--corr=' + all_values['_correlation_'] + ' '
        cmd_list.append('--corr=' + all_values['_correlation_'])
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
        cmd_string = os.path.join(os.path.realpath('.'), 'enfuse_ais', 'align_image_stack.exe')
        ais_string = cmd_string
    elif platform.system() == 'Darwin':
        #cmd_string = os.path.join(os.path.realpath('.'), 'enfuse_ais', 'MacOS', 'align_image_stack')
        check_pyinstaller =getattr (sys, '_MEIPASS', 'NotRunningInPyInstaller')
        if check_pyinstaller == 'NotRunningInPyInstaller': # we run from the script and assume enfuse is in the PATH
        #    cmd_string = 'enfuse'
             cmd_string = os.path.join(os.path.realpath('.'), 'enfuse_ais', 'MacOS', 'align_image_stack')
        else:
             cmd_string = os.path.join(check_pyinstaller, 'enfuse_ais', 'MacOS', 'align_image_stack')

    else: # 'Linux'
        # If it is an appimage we use our builtin align_image_stack via internal usr/bin
        # If it is a deb, we will install it in the path
        # If the user runs it from python, (s)he needs to install align_image_stack him-/herself
        cmd_string = 'align_image_stack'
    if (type == 'preview'):
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
    if not all_values['_levels_'] == 29:
        cmd_string += '--levels=' + str(int(all_values['_levels_'])) + ' '
        cmd_list.append('--levels=' + str(int(all_values['_levels_'])))
    if not all_values['_exposure_weight_'] == 1.0:
        cmd_string += '--exposure-weight=' + str(all_values['_exposure_weight_']) + ' '
        cmd_list.append('--exposure-weight=' + str(all_values['_exposure_weight_']))
    if not all_values['_saturation_weight_'] == 0.2:
        cmd_string += '--saturation-weight=' + str(all_values['_saturation_weight_']) + ' '
        cmd_list.append('--saturation-weight=' + str(all_values['_saturation_weight_']))
    if not all_values['_contrast_weight_'] == 0:
        cmd_string += '--contrast-weight=' + str(all_values['_contrast_weight_']) + ' '
        cmd_list.append('--contrast-weight=' + str(all_values['_contrast_weight_']))
    if not all_values['_entropy_weight_'] == 0:
        cmd_string += '--entropy-weight=' + str(all_values['_entropy_weight_']) + ' '
        cmd_list.append('--entropy-weight=' + str(all_values['_entropy_weight_']))
    if not all_values['_exposure_optimum_'] == 0.5:
        cmd_string += '--exposure-optimum=' + str(all_values['_exposure_optimum_']) + ' '
        cmd_list.append('--exposure-optimum=' + str(all_values['_exposure_optimum_']))
    if not all_values['_exposure_width_'] == 0.2:
        cmd_string += '--exposure-width=' + str(all_values['_exposure_width_']) + ' '
        cmd_list.append('--exposure-width=' + str(all_values['_exposure_width_']))
    if all_values['_hardmask_']:
        cmd_string += '--hard-mask '
        cmd_list.append('--hard-mask')
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
    elif platform.system() == 'Darwin':
        check_pyinstaller =getattr (sys, '_MEIPASS', 'NotRunningInPyInstaller')
        if check_pyinstaller == 'NotRunningInPyInstaller': # we run from the script and assume enfuse is in the PATH
        #    cmd_string = 'enfuse'
            cmd_string = os.path.join(os.path.realpath('.'), 'enfuse_ais', 'MacOS', 'enfuse')
        else:
            cmd_string = os.path.join(check_pyinstaller, 'enfuse_ais', 'MacOS', 'enfuse')
    else: # 'Linux'
        # If it is an appimage we use our builtin enfuse via internal usr/bin
        # If it is a deb, we will install it in the path
        # If the user runs it from python, (s)he needs to install enfuse him-/herself
        cmd_string = 'enfuse'
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
    #print('finaly end of create_enfuse_command')
    #print('cmd_string ', cmd_string)
    #print('cmd_list ', cmd_list)

    # return cmd_string
    if platform.system() == 'Windows':
        return enf_string, cmd_list
    else:
        return cmd_string, cmd_list

