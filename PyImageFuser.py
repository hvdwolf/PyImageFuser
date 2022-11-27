# -*- coding: utf-8 -*-

# PyImageFuser.py - This is the main script from which everything is called
# and which contains the user interaction events.

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
import histogram
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
read_errors = ""
images = [] # This one is used for our calculations
resized_images = [] # This one contains the complete path names of our resized images
full_images = [] # this one contains the complete path names of the original images
image_exif_dictionaries = {}
reference_image = ''
image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)
null_image = ''
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
    print('pyinstaller _MEIPASS ', getattr(sys, '_MEIPASS', 'NotRunningInPyInstaller'))
    if os.getenv('HERE') != None:
        print('HERE ', os.getenv('HERE'))

    # Display the GUI to the user
    window =  ui_layout.create_and_show_gui(tmpfolder,start_folder)

    # Now do the version check
    file_functions.version_check()


    while True:
        event, values = window.Read(timeout=100)
        if event == sg.WIN_CLOSED or event == '_Close_' or event == 'Exit':
            file_functions.remove_tmp_workfolder(tmpfolder)
            return('Cancel', values)
            break
        elif event == 'Load images':
            sg.popup_get_file('Load images', no_window=True, initial_folder=ui_actions.which_folder(), file_types = program_texts.image_formats)
        elif event == '-FILES-': # user just loaded a bunch of images
            reference_image, folder, image_exif_dictionaries, read_errors = ui_actions.fill_images_listbox(window, values)
            #print(image_exif_dictionaries.keys())
            print("reference_image " + reference_image)
            if (len(read_errors)>0):
                sg.Popup("Errors reading file(s):\n\n" + read_errors, icon=image_functions.get_icon(), auto_close=False)
            ui_actions.clean_screen_after_file_loading(window)
            window['-FILE LIST-'].update()
        # Check on presets
        elif event == '_alltodefault_':
            ui_actions.set_presets(window, 'defaults')
        elif event == '_noisereduction_':
            ui_actions.set_presets(window, 'noisereduction')
        elif event == '_focusstacking_':
            ui_actions.set_presets(window, 'focusstacking')
        # Now check the numerical "text" fields if only numerical
        elif event == '_inHFOV_' and values['_inHFOV_'] and values['_inHFOV_'][-1] not in ('0123456789.'):
            window['_inHFOV_'].update(values['_inHFOV_'][:-1])
        elif event == '_correlation_' and values['_correlation_'] and values['_correlation_'][-1] not in ('0123456789.'):
            window['_correlation_'].update(value='0.9')
        elif event == '_inNoCP_' and values['_inNoCP_'] and values['_inNoCP_'][-1] not in ('0123456789'):
            window['_inNoCP_'].update(value='8')
        elif event == '_removeCPerror_' and values['_removeCPerror_'] and values['_removeCPerror_'][-1] not in ('0123456789'):
            window['_removeCPerror_'].update(value='3')
        elif event == '_inScaleDown_' and values['_inScaleDown_'] and values['_inScaleDown_'][-1] not in ('0123456789'):
            window['_inScaleDown_'].update(value='1')
        elif event == '_inGridsize_' and values['_inGridsize_'] and values['_inGridsize_'][-1] not in ('0123456789'):
            window['_inGridsize_'].update(value='5')
        # end of numerical checks
        elif event == '_autoHfov':
            if values['_autoHfov']:
                window['_inHFOV_'].update(disabled=True)
            else:
                window['_inHFOV_'].update(disabled=False)
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
        elif event.startswith('Align_Image_stack parameters') \
                or event.startswith('Align_Image_stack tips') \
                or event.startswith('Enfuse parameters') \
                or event.startswith('Why exposure')\
                or event.startswith('Examples'):
            file_functions.show_html_in_browser(event)
        elif event == 'System Info':
            sg.popup(sg.get_versions())
        elif event == 'Preferences' or event =='_btnPreferences_':
            Settings.settings_window()
        elif event == '_select_all_':
            #print('_select_all_')
            list_index = []
            max = len(values["-FILES-"].split(";"))
            list_index.extend(range(0, max))
            window['-FILE LIST-'].update(set_to_index = list_index,)
            window.refresh()
        elif event == '_histogram_':
            if len(values['-FILE LIST-']) != 0:
                histogram.show_histogram(os.path.join(folder, values['-FILE LIST-'][0]))
        elif event == '_display_selected_':
            if values['_display_selected_']:
                list_index = []
                window['-FILE LIST-'].update(set_to_index=list_index, )
                window.refresh()
        elif event == "-FILE LIST-":  # A file was chosen from the listbox
            if values['_display_selected_'] and len(values['-FILE LIST-']) !=0:
                imgtodisplay = image_functions.resizesingletopreview(folder, tmpfolder, values['-FILE LIST-'][0])
                #image_functions.display_preview(window, os.path.join(tmpfolder, values['-FILE LIST-'][0]))
                image_functions.display_preview(window, imgtodisplay)
            if len(values['-FILE LIST-']) !=0:
                imgtodisplay = image_functions.resizesingletothumb(folder, tmpfolder, values['-FILE LIST-'][0])
                #image_functions.display_thumb(window, os.path.join(tmpfolder, 'thumb-' + values['-FILE LIST-'][0]))
                image_functions.display_thumb(window, imgtodisplay)
                #print(image_exif_dictionaries.get(values['-FILE LIST-'][0]))
                ui_actions.exif_table(window, image_exif_dictionaries.get(values['-FILE LIST-'][0]))
                histogram.show_histogram(window, os.path.join(folder, values['-FILE LIST-'][0]))
        elif event == '_preset_opencv_' or event == '_preset_enfuse_':
            ui_actions.set_fuse_presets(window, values)
        elif event == '_useOpenCV_':
            ui_actions.set_levels_status(window,values)
        elif event == '_create_preview_':
            print('User pressed Create Preview\n')
            window['_proc_time_'].update('Processing time: --')
            if len(values['-FILE LIST-']) >1: # We have at least 2 files
                failed, resized_images = image_functions.resizetopreview(values, folder, tmpfolder)
                print(failed)
                go_on = False
                if failed != '':
                    is_zero = file_functions.getFileSizes(values, tmpfolder)
                    if is_zero > 0:
                        sg.popup(program_texts.resize_error_message, icon=image_functions.get_icon())
                        go_on = False # not necessary but do it anyway
                    else:
                        go_on = True
                        program_texts.popup_text_scroll('Something went wrong',program_texts.resize_warning_message, failed)
                else: # failed = ''
                    go_on = True
                if go_on:
                    disable_elements(window, True)
                    window.refresh()
                    starttime = timeit.default_timer()
                    if (values['_useAISPreview_']):
                        cmdstring, cmd_list = image_functions.create_ais_command(values, folder, tmpfolder, 'preview')
                        print("\n\ncmdstring: ", cmdstring, "\ncmd_list: ", cmd_list, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, cmd_list, " running align_image_stack ", False)
                        if result == 'OK':
                            cmdstring, cmd_list = image_functions.create_enfuse_command(values, folder, tmpfolder, 'preview_ais','')
                            #print("\n\ncmdstring: ", cmdstring, "\ncmd_list: ", cmd_list, "\n\n")
                            result = run_commands.run_shell_command(cmdstring, cmd_list, 'running enfuse', False)
                        else:
                            print("return string from ais ", result)
                    else:  # Create preview without using ais
                        cmdstring, cmd_list = image_functions.create_enfuse_command(values, folder, tmpfolder, 'preview', '')
                        print("\n\n", cmdstring, "\n\n")
                        result = run_commands.run_shell_command(cmdstring, cmd_list, ' running enfuse ', False)
                    stoptime = timeit.default_timer()
                    display_processing_time(window, starttime, stoptime)
                    disable_elements(window, False)
                    window.refresh()
                    if reference_image == "":
                        reference_image = null_image
                    image_functions.copy_exif_info(reference_image, os.path.join(tmpfolder, 'preview.jpg'))
                    print('preview filepath', os.path.join(tmpfolder, 'preview.jpg'))
                    image_functions.display_preview(window, os.path.join(tmpfolder, 'preview.jpg'))
                window['_CreateImage_'].set_focus(force=True)
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
        elif event == '_CreateImage_':
            print('User pressed "Create Exposure fused image\n')
            window['_proc_time_'].update('Processing time: --')
            if len(read_errors) == 0:
                if len(values['-FILE LIST-']) > 1:  # We have at least 2 files
                    newFileName, full_images = image_functions.get_filename_images(values, folder)
                    if newFileName != '' and newFileName != 'Cancel':
                        disable_elements(window, True)
                        window.refresh()
                        starttime = timeit.default_timer()
                        newFileName = file_functions.check_filename(values, newFileName)
                        if values['_useAIS_']:
                            cmdstring, cmd_list = image_functions.create_ais_command(values, folder, tmpfolder, '')
                            print("\n\n", cmdstring, "\n\n")
                            result = run_commands.run_shell_command(cmdstring, cmd_list,'  Now running align_image_stack  \n  Please be patient  ',False)
                            print("\n\n" + result + "\n\n")
                            if result == 'OK':
                                cmdstring, cmd_list = image_functions.create_enfuse_command(values, folder, tmpfolder,'full_ais',os.path.join(folder,newFileName))
                                print("\n\n", cmdstring, "\n\n")
                                result = run_commands.run_shell_command(cmdstring, cmd_list,'  Now running enfuse  \n  Please be patient  ',False)
                        else:  # Create full image without using ais
                            cmdstring, cmd_list = image_functions.create_enfuse_command(values, folder, tmpfolder, '',os.path.join(folder,newFileName))
                            print("\n\n", cmdstring, "\n\n")
                            result = run_commands.run_shell_command(cmdstring, cmd_list,'  Now running enfuse  \n  Please be patient  ',False)
                        stoptime = timeit.default_timer()
                        display_processing_time(window, starttime, stoptime)
                        disable_elements(window, False)
                        window.refresh()
                        # print('create reference_image: ', reference_image)
                        # print('null_image', null_image)
                        if reference_image == "":
                            reference_image = null_image
                        image_functions.copy_exif_info(reference_image, os.path.join(folder, newFileName))
                        if values['_dispFinalIMG_']:
                            image_functions.displayImageWindow(os.path.join(folder, newFileName))
                    window['_CreateImage_'].set_focus(force=True)
                else:  # 1 or 0 images selected
                    sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
            else:
                sg.popup("At least one of the files could not be read. This means that no enfused image can be created.", icon=image_functions.get_icon(), auto_close=False)
    window.Close()

 
#------------------- Main "boilerplate" function ----------------------------------------------
#----------------------------------------------------------------------------------------------

## Main program, main module
if __name__ == '__main__':
    main()
