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

import PySimpleGUI as sg
import os, sys , tempfile, threading
# Necessary for windows
import requests
from pathlib import Path
import cv2

#------- Helper python scripts ----
import run_long_functions
import ui_layout
import Settings
import image_functions
import program_texts
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
image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)
#thread_done = 1

#----------------------------------------------------------------------------------------------
#------------------------------- Helper functions ---------------------------------------------
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
    print("\nsettingsfile: ",settingsFile)
    print("tmpdir", os.path.realpath(tempfile.gettempdir()))
    print("current path ", os.path.realpath('.'))

    # Display the GUI to the user
    window =  ui_layout.create_and_show_gui(tmpfolder,start_folder)
    while True:
        event, values = window.Read(timeout=100)
        window.Element('-WAITGIF-').UpdateAnimation(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','animated_dotsx32.gif'), time_between_frames=100)
        #print('You entered ', values)
        window['bar'].Widget['value'] += window['bar'].metadata
        if event == sg.WIN_CLOSED or event == '_Close_' or event == 'Exit':
            file_functions.remove_tmp_workfolder(tmpfolder)
            #print('pressed Close')
            return('Cancel', values)
            break
        elif event == '_dispOutput_':
            #print(values['_dispOutput_'])
            window['_sgOutput_'].update(visible=values['_dispOutput_'])
        elif event == '-FILES-':
            #print('values["-FILES-"]   ',values["-FILES-"])
            filenames = []
            window['-FILE LIST-'].update(filenames)
            if values["-FILES-"]: # or values["-FILES-"] == {}: #empty list returns False
                file_list = values["-FILES-"].split(";")
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
                    image_exif_dictionaries[fname] = image_functions.get_all_exif_info(file)
                window['-FILE LIST-'].update(filenames)
                window['-FOLDER-'].update(folder)
        elif event == 'About...':
            window.disappear()
            sg.popup(program_texts.about_message, grab_anywhere=True, keep_on_top=True, icon=image_functions.get_icon())
            window.reappear()
        elif event == 'Credits':
            window.disappear()
            sg.popup(program_texts.Credits, grab_anywhere=True, keep_on_top=True, icon=image_functions.get_icon())
            window.reappear()
        elif event == 'Preferences' or event =='_btnPreferences_':
            Settings.settings_window()
        elif event == '_select_all_':
            print('_select_all_')
            #print(str(values["-FILES-"].split(";")))
            #index = range(len(values["-FILES-"].split(";")))
            #window["-FILE LIST-"](set_to_index=[index], scroll_to_index=index)
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            #print('A file was chosen from the listbox')
            if values['_display_selected_'] and len(values['-FILE LIST-']) !=0:
                image_functions.resizesingletopreview(folder, tmpfolder, values['-FILE LIST-'][0])
                image_functions.display_preview(window, os.path.join(tmpfolder, values['-FILE LIST-'][0]))
        elif event == '_create_preview_':
            # The exposure fusion and aligning has been copied from below page
            # https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
            print('User pressed Create Preview\n')
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
                    if (values['_align_images_']):
                        image_functions.align_fuse(values, resized_images, tmpfolder, 'preview', True) #True for  "do align"
                        image_functions.display_preview(window, os.path.join(tmpfolder, 'preview.jpg'))
                    else:  # Create preview without aligning
                        image_functions.align_fuse(values, resized_images, tmpfolder, 'preview', False) # False for "don't align"
                        image_functions.display_preview(window, os.path.join(tmpfolder, 'preview.jpg'))
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
        elif event == '_CreateImage_':
            # The exposure fusion and aligning has been copied from below page
            # https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
            print('User pressed "Create Exposure fused image"\n')
            if len(values['-FILE LIST-']) > 1:  # We have at least 2 files
                newFileName, full_images = image_functions.get_filename_images(values, folder)
                if newFileName != '' and newFileName != 'Cancel':
                    #window.write_event_value('_updater_', '')
                    #window['-WAITGIF-'].Update(visible=True)
                    #window['_progress_message_'].update('aligning and fusing')
                    #window['bar'].Update(visible=True)
                    window['_sgOutput_'].update(visible=True)
                    window.refresh()
                    if values['_align_images_']:
                        #image_functions.align_fuse(values, full_images, tmpfolder, os.path.join(folder, newFileName), True)  # True for  "do align"
                        #ui_layout.progress_window("enfusing")
                        #threading.Thread(target=image_functions.align_fuse, args=(values, full_images, tmpfolder, os.path.join(folder, newFileName), True, ), daemon=True).start()
                        try:
                            print('start run_long_functions.long_function_with_animation')
                            ftarget = 'image_functions.align_fuse'
                            fargs = (values, full_images, tmpfolder,os.path.join(folder, newFileName))
                            fmessage = 'Aligning and fusing images'
                            run_long_functions.long_function_with_animation(target = ftarget, args = fargs,message= fmessage, font='Helvetica 15', no_titlebar=True, alpha_channel=0.85)
                        except Exception as e:
                            logger(e)
                    else:  # Create full image without aligning
                        image_functions.align_fuse(values, full_images, tmpfolder, os.path.join(folder, newFileName),True)  # True for  "do align"
                    window['_sgOutput_'].update(visible=False)
                    window.refresh()
                    if values['_dispFinalIMG_']:
                        image_functions.displayImageWindow(os.path.join(folder, newFileName))
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
        elif event == '_noise_reduction_':
            # This code is copied from: https://github.com/maitek/image_stacking
            print('User pressed "Create noise reduced image"\n')
            if len(values['-FILE LIST-']) > 1:  # We have at least 2 files
                newFileName, full_images = image_functions.get_filename_images(values, folder)
                if newFileName != '' and newFileName != 'Cancel':
                    #window.write_event_value('_updater_', '')
                    #window['-WAITGIF-'].Update(visible=True)
                    window['_sgOutput_'].update(visible=True)
                    window['_progress_message_'].update('starting noise reduction')
                    #window['bar'].Update(visible=True)
                    window.refresh()
                    image_functions.do_noise_reduction(full_images, os.path.join(folder, newFileName), window, values)
                    #ui_layout.progress_window("noise reduction")
                    threading.Thread(target=image_functions.do_noise_reduction,args=(full_images, os.path.join(folder, newFileName), values,),daemon=True).start()
                    window['_progress_message_'].update('noise reduction finished')
                    window['_sgOutput_'].update(visible=False)
                    window.refresh()
                    #thread_done = True
                    if values['_dispFinalIMG_']:
                        image_functions.displayImageWindow(os.path.join(folder, newFileName))
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())

        # --------------- Check for incoming messages from threads  ---------------
        '''
        if thread_done is True:
            print('The thread has finished!')
            thread_done = False
            window.write_event_value('_updater_', '')
            window['-WAITGIF-'].Update(visible=False)
            window['_progress_message_'].update('')
            window['bar'].Update(visible=False)
            window.refresh()
            '''

    window.Close()

 
#------------------- Main "boilerplate" function ----------------------------------------------
#----------------------------------------------------------------------------------------------


## Main program, main module
if __name__ == '__main__':
    main()
