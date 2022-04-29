# -*- coding: utf-8 -*-

# firmware_modder.py - This is the main script to modify the firmware
# for the AllappUpdate.bin

# Copyright (c) 2022, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.
import webbrowser

import PySimpleGUI as sg
import os, sys , tempfile, timeit
# Necessary for windows
import requests
from pathlib import Path

#------- Helper python scripts ----
import ui_layout
import ui_actions
import Settings
import image_functions
import program_texts
import run_commands
import file_functions


#------- Some constants & variables -----------
sg.theme('SystemDefault1') # I hate all these colourful, childish themes. Please play with it and then grow up.
sg.SetOptions(font = ('Helvetica', 12))
filenames = []
pathnames = []
images = [] # This one is used for our calculations
resized_images = [] # This one contains the complete path names of our resized images
full_images = [] # this one contains the complete path names of the original images
image_exif_dictionaries = {}
reference_image = ''
image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)
#thread_done = 1

#----------------------------------------------------------------------------------------------
#------------------------------- Helper functions ---------------------------------------------
# This functions
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
        window['_Close_'].update(disabled=True)
        ##window['_sgOutput_'].update(visible=True, disabled=False, echo_stdout_stderr=True) # When buttons are disabled, output window becomes visible
        #window['_sgOutput_'].update(visible=True)  # When buttons are disabled, output window becomes visible
    else:
        window['_btnLoadImages_'].update(disabled=False)
        window['_btnPreferences_'].update(disabled=False)
        window['_select_all_'].update(disabled=False)
        window['_create_preview_'].update(disabled=False)
        window['_CreateImage_'].update(disabled=False)
        window['_Close_'].update(disabled=False)
        ##window['_sgOutput_'].update(visible=False, disabled=True, echo_stdout_stderr=False) # When buttons are enabled, output window is hidden
        #window['_sgOutput_'].update(visible=False) # When buttons are enabled, output window is hidden

def display_processing_time(window, starttime, stoptime):
    proc_time = stoptime - starttime
    str_proc_time = 'Processing time: ' + format(proc_time, '.2f') + ' seconds'
    window['_proc_time_'].update(str_proc_time , visible=True, )
    print(str_proc_time)

def replace_strings(Lines, orgstring, newstring):
    newLines = []
    # Now do the replacing
    for line in Lines:
        if orgstring not in line:
            newLines.append(line)
        else:
            newLines.append(newstring + '\n')
    return newLines

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


#----------------------------------------------------------------------------------------------
#----------------------------- Main function --------------------------------------------------
def main():
    #global thread_done
    tmpfolder = os.path.join(os.path.realpath(tempfile.gettempdir()), 'pyimagefuser')
    settingsFile = os.path.join(os.path.realpath(Path.home()), '.pyimagefuser.json')
    file_functions.recreate_tmp_workfolder(tmpfolder)
    sg.user_settings_filename(path=os.path.realpath(Path.home()))
    start_folder = sg.user_settings_get_entry('imgfolder', os.path.realpath(Path.home()))
    print("\ntmpfolder: ", tmpfolder)
    print("settingsfile: ",settingsFile)
    print("tmpdir", os.path.realpath(tempfile.gettempdir()))
    print("current path ", os.path.realpath('.'))
    #print(getattr(sys, '_MEIPASS', 'NotRunningInPyInstaller'))

    # Display the GUI to the user
    window =  ui_layout.create_and_show_gui(tmpfolder,start_folder)

    while True:
        event, values = window.Read(timeout=100)
        #window['_proc_time_'].update('Processing time: --')
        if event == sg.WIN_CLOSED or event == '_Close_' or event == 'Exit':
            file_functions.remove_tmp_workfolder(tmpfolder)
            #print('pressed Close')
            return('Cancel', values)
            break
        elif event == '-FILES-':
            filenames = []
            window['-FILE LIST-'].update(filenames)
            if values["-FILES-"]: # or values["-FILES-"] == {}: #empty list returns False
                file_list = values["-FILES-"].split(";")
                null_image = file_list[0]
                reference_image = ''
                for file in file_list:
                    # print(f)
                    fname = os.path.basename(file)
                    folder = os.path.dirname(os.path.abspath(file))
                    # Now save this folder as "last opened folder" to our settings
                    sg.user_settings_filename(path=Path.home())
                    sg.user_settings_set_entry('last_opened_folder', folder)
                    filenames.append(fname)
                    pathnames.append(file)
                    # get all exif date if available
                    tmp_reference_image, image_exif_dictionaries[fname] = image_functions.get_all_exif_info(file)
                    if tmp_reference_image != '':
                        reference_image = tmp_reference_image
                        print('reference_image', reference_image)
                    #image_functions.get_basic_exif_info_from_file(file, '')
                window['-FILE LIST-'].update(filenames)
                window['-FOLDER-'].update(folder)
                # Check if we now have a reference image, in case the images do not contain (enough) exif info
                if reference_image == None or reference_image == "":
                    reference_image = null_image
        elif event == 'About...':
            window.disappear()
            sg.popup(program_texts.about_message, grab_anywhere=True, keep_on_top=True, icon=image_functions.get_icon())
            window.reappear()
        elif event == 'Credits':
            window.disappear()
            sg.popup(program_texts.Credits, grab_anywhere=True, keep_on_top=True, icon=image_functions.get_icon())
            window.reappear()
        elif event == 'Program buttons':
            #window.disappear()
            program_texts.explain_parameters_popup()
            #window.reappear()
        elif event == 'Align_Image_stack parameters':
            try:
                webbrowser.open('file://' + file_functions.resource_path(os.path.join('docs', 'align_image_stack.html')) )
                #webbrowser.open('https://manpages.debian.org/testing/hugin-tools/align_image_stack.1.en.html')
            except:
                sg.popup("Can't open the align_image_stack parameters html", icon=image_functions.get_icon())
        elif event == 'Enfuse parameters':
            try:
                webbrowser.open('file://' + file_functions.resource_path(os.path.join('docs', 'enfuse.html')))
                #webbrowser.open('https://manpages.debian.org/buster/enfuse/enfuse.1.en.html')
            except:
                sg.popup("Can't open the enfuse parameters html", icon=image_functions.get_icon())
        elif event == 'Preferences' or event =='_btnPreferences_':
            Settings.settings_window()
        elif event == '_select_all_':
            #print('_select_all_')
            list_index = []
            max = len(values["-FILES-"].split(";"))
            list_index.extend(range(0, max))
            window['-FILE LIST-'].update(set_to_index = list_index,)
            window.refresh()
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            #print('A file was chosen from the listbox')
            if values['_display_selected_'] and len(values['-FILE LIST-']) !=0:
                image_functions.resizesingletopreview(folder, tmpfolder, values['-FILE LIST-'][0])
                image_functions.display_preview(window, os.path.join(tmpfolder, values['-FILE LIST-'][0]))
        elif event == '_preset_opencv_' or event == '_preset_enfuse_':
            ui_actions.set_fuse_presets(window, values)
        elif event == '_create_preview_':
            # The exposure fusion and aligning has been copied from below page
            # https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
            print('User pressed Create Preview\n')
            window['_proc_time_'].update('Processing time: --')
            if len(values['-FILE LIST-']) >1: # We have at least 2 files
                failed, resized_images = image_functions.resizetopreview(values, folder, tmpfolder)
                print(failed)
                go_on = False
                if failed != '':
                    is_zero = file_functions.getFileSizes(values, tmpfolder)
                    if is_zero > 0:
                        #sg.popup_scrolled(program_texts.resize_error_message, failed, icon=image_functions.get_icon())
                        sg.popup(program_texts.resize_error_message, icon=image_functions.get_icon())
                        go_on = False # not necessary but do it anyway
                    else:
                        go_on = True
                        #sg.popup_scrolled(program_texts.resize_warning_message, failed, icon=image_functions.get_icon())
                        program_texts.popup_text_scroll('Something went wrong',program_texts.resize_warning_message, failed)
                else: # failed = ''
                    go_on = True
                if go_on:
                    disable_elements(window, True)
                    window.refresh()
                    starttime = timeit.default_timer()
                    if (values['_useAISPreview_']):
                        cmdstring, cmd_list = image_functions.create_ais_command(values, folder, tmpfolder, 'preview')
                        print("\n\ncmdstring: ", cmdstring, "; cmd_list: ", cmd_list, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, cmd_list, "running align_image_stack", False)
                        # print("\n\n" + result + "\n\n")
                        if result == 'OK':
                            cmdstring, cmd_list = image_functions.create_enfuse_command(values, folder, tmpfolder, 'preview_ais','')
                            print("\n\n", cmdstring, "\n\n")
                            result = run_commands.run_shell_command(cmdstring, cmd_list, 'running enfuse', False)
                            image_functions.display_preview(window, os.path.join(tmpfolder, 'preview.jpg'))
                    else:  # Create preview without using ais
                        cmdstring, cmd_list = image_functions.create_enfuse_command(values, folder, tmpfolder, 'preview', '')
                        print("\n\n", cmdstring, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, cmd_list, 'running enfuse', False)
                    stoptime = timeit.default_timer()
                    display_processing_time(window, starttime, stoptime)
                    disable_elements(window, False)
                    window.refresh()
                    #print('create preview reference_image: ', reference_image)
                    #print('null_image', null_image)
                    if reference_image == "":
                        reference_image = null_image
                    filepath = image_functions.copy_exif_info(reference_image, os.path.join(tmpfolder, 'preview.jpg'))
                    image_functions.display_preview(window, filepath)
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
        elif event == '_CreateImage_':
            # The exposure fusion and aligning has been copied from below page
            # https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
            print('User pressed "Create Exposure fused image\n')
            window['_proc_time_'].update('Processing time: --')
            if len(values['-FILE LIST-']) > 1:  # We have at least 2 files
                newFileName, full_images = image_functions.get_filename_images(values, folder)
                if newFileName == '':
                    sg.popup("You did not provide a filename!", icon=image_functions.get_icon())
                elif newFileName != 'Cancel':
                    disable_elements(window, True)
                    window.refresh()
                    starttime = timeit.default_timer()
                    newFileName = file_functions.check_filename(values, newFileName)
                    if values['_useAIS_']:
                        cmdstring, cmd_list = image_functions.create_ais_command(values, folder, tmpfolder, '')
                        print("\n\n", cmdstring, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, cmd_list, '  Now running align_image_stack  \n  Please be patient  ', False)
                        print("\n\n" + result + "\n\n")
                        if result == 'OK':
                            cmdstring, cmd_list = image_functions.create_enfuse_command(values, folder, tmpfolder, 'full_ais', os.path.join(folder, newFileName))
                            print("\n\n", cmdstring, "\n\n")
                            result = run_commands.run_shell_command(cmdstring, cmd_list, '  Now running enfuse  \n  Please be patient  ', False)
                    else:  # Create full image without using ais
                        cmdstring, cmd_list = image_functions.create_enfuse_command(values, folder, tmpfolder, '', os.path.join(folder, newFileName))
                        print("\n\n", cmdstring, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, cmd_list, '  Now running enfuse  \n  Please be patient  ', False)
                    stoptime = timeit.default_timer()
                    display_processing_time(window, starttime, stoptime)
                    disable_elements(window, False)
                    window.refresh()
                    print('create reference_image: ', reference_image)
                    print('null_image', null_image)
                    if reference_image == "":
                        reference_image = null_image
                    image_functions.copy_exif_info(reference_image, os.path.join(folder, newFileName))
                    if values['_dispFinalIMG_']:
                        image_functions.displayImageWindow(os.path.join(folder, newFileName))
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
        '''        
        elif event == '_noise_reduction_':
            # This code is copied from: https://github.com/maitek/image_stacking
            print('User pressed "Create noise reduced image"\n')
            window['_proc_time_'].update('Processing time: --')
            if len(values['-FILE LIST-']) > 1:  # We have at least 2 files
                newFileName, full_images = image_functions.get_filename_images(values, folder)
                if newFileName != '' and newFileName != 'Cancel':
                    disable_elements(window, True)
                    starttime = timeit.default_timer()
                    image_functions.do_align_and_noise_reduction(full_images, folder, newFileName, values, '')
                    stoptime = timeit.default_timer()
                    display_processing_time(window, starttime, stoptime)
                    disable_elements(window, False)
                    if values['_dispFinalIMG_']:
                        image_functions.displayImageWindow(os.path.join(folder, newFileName))
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
        '''
    window.Close()

 
#------------------- Main "boilerplate" function ----------------------------------------------
#----------------------------------------------------------------------------------------------


## Main program, main module
if __name__ == '__main__':
    main()
