# -*- coding: utf-8 -*-

# PyImageFuser.py - This is the main script from which everything is called
# and which contains the user interaction events.

# Copyright (c) 2022-2023, Harry van der Wolf. all rights reserved.
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
import cv2
import threading

#------- Helper python scripts ----
import histogram
import ui_layout
import ui_actions
import Settings
import image_functions
import program_texts
import file_functions
import opencv_functions



#------- Some constants & variables -----------
sg.theme('SystemDefault1') # I hate all these colourful, childish themes. Please play with it and then grow up.
sg.SetOptions(font = ('Helvetica', 12))
filenames = [] # All the file names
other_filenames = [] # The file names not having exposurecompensation (exposureBiasValue) 0
ordered_filenames = [] # This is the list where the ref_image is the first one
pathnames = []
read_errors = ""
images = [] # This one is used for our calculations
resized_images = [] # This one contains the complete path names of our resized images
full_images = [] # this one contains the complete path names of the original images
image_exif_dictionaries = {}
reference_image = ''
image_formats = (('image formats', '*.jpg *.JPG *.jpeg *.JPEG *.png *.PNG *.tif *.TIF *.tiff *.TIFF'),)
null_image = ''
files_chosen = None
#thread_done = 1



#----------------------------------------------------------------------------------------------
#------------------------------- Helper functions ---------------------------------------------
# This functions

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

    MLINE = '-ML-' + sg.WRITE_ONLY_KEY

    # Display the GUI to the user
    window =  ui_layout.create_and_show_gui(tmpfolder,start_folder)

    sg.cprint_set_output_destination(window, MLINE)
    # Show some variabels to the user
    print("\ntmpfolder: ", tmpfolder)
    print("settingsfile: ", settingsFile)
    print("tmpdir", os.path.realpath(tempfile.gettempdir()))
    print("current path ", os.path.realpath('.'))
    print('pyinstaller _MEIPASS ', getattr(sys, '_MEIPASS', 'NotRunningInPyInstaller'))
    if os.getenv('HERE') != None:
        print('HERE ', os.getenv('HERE'))

    # Now do the version check
    file_functions.version_check()

    while True:
        event, values = window.Read(timeout=100)
        if event == sg.WIN_CLOSED or event == '_Close_' or event == 'Exit':
            file_functions.remove_tmp_workfolder(tmpfolder)
            return('Cancel', values)
            break
        elif event == 'Load images':
        #elif event == 'Load images' or event == '_btnLoadImages_':
            file_functions.remove_temp_files()
            values['-FILE LIST-'] = None
            reference_image = None
            image_exif_dictionaries = []
            other_filenames = []
            read_errors = []
            files_chosen = sg.popup_get_file('Load images', multiple_files=True, no_window=True, initial_folder=ui_actions.which_folder(), file_types = program_texts.image_formats)
            #values['-FILE LIST-'] = list(files_chosen)
            values["-FILES-"] = "; ".join(files_chosen)
            opencv_functions.myprint(window, "files chosen " + files_chosen)
        elif event == '-FILES-': # user just loaded a bunch of images
            ordered_filenames = []
            reference_image, folder, image_exif_dictionaries, other_filenames, all_filenames, read_errors = ui_actions.fill_images_listbox(window, values)
            #print(image_exif_dictionaries.keys())
            opencv_functions.myprint(window, "reference_image " + reference_image)
            ordered_filenames.append(reference_image)
            ordered_filenames.extend(other_filenames)
            if (len(read_errors)>0):
                sg.Popup("Errors reading file(s):\n\n" + read_errors, icon=image_functions.get_icon(), auto_close=False)
            ui_actions.clean_screen_after_file_loading(window)
            window['-FILE LIST-'].update()
        # Visibility of "create image" buttons based on desired output
        elif event == '_exposurefusion_' or event == '_noisereduction_' or event == '_focusstacking_':
            ui_actions.hide_show_buttons_options(window, values)
        # Available options for alignment
        elif event =='_orb_' or event == '_ecc_' or event == '_sift_' or event == '_alignmtb_':
            ui_actions.set_align_options(window, values)
        elif event == '_showOutput_':
            if values['_showOutput_']:
                window["-MLINE-"].update(visible=True)
            else:
                window["-MLINE-"].update(visible=False)
        # Now check the numerical "text" fields if only numerical
        elif event == '_maxfeatures_' and values['_maxfeatures_'] and values['_maxfeatures_'][-1] not in ('0123456789.'):
            window['_maxfeatures_'].update(value='5000')
        elif event == '_keeppercent_' and values['_keeppercent_'] and values['_keeppercent_'][-1] not in ('0123456789.'):
            window['_keeppercent_'].update(value='0.1')
        elif event == '_max_iterations_' and values['_max_iterations_'] and values['_max_iterations_'][-1] not in ('0123456789'):
            window['_max_iterations_'].update(value='500')
        elif event == '_termination_eps_' and values['_termination_eps_'] and values['_termination_eps_'][-1] not in ('0123456789'):
            window['_termination_eps_'].update(value='1e-10')
        # end of numerical checks
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
            #sg.popup(program_texts.Explain_buttons, grab_anywhere=True, keep_on_top=True, icon=image_functions.get_icon())
            #window.reappear()
            program_texts.explain_buttons_popup()
        elif event.startswith('Alignment') \
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
            #print("select all files" + values["-FILES-"])
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
            opencv_functions.myprint(window, 'User pressed Create Preview\n')
            window['_proc_time_'].update('Processing time: --')
            if len(values['-FILE LIST-']) >1: # We have at least 2 files
                opencv_functions.myprint(window,'resizing the images to preview size')
                failed, resized_images = image_functions.resizetopreview(values, folder, tmpfolder)
                opencv_functions.myprint(window, "failed resizes: " + failed + "\nresized images: " + str(resized_images))
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
                    ui_actions.disable_elements(window, True)
                    window.refresh()
                    starttime = timeit.default_timer()

                    thumb_reference, other_thumbs, read_errors = image_functions.get_thumbs_exposure_compensation(resized_images)
                    if (values['_exposurefusion_']):
                        if (values['_always_align_']):
                            # Do the orb/mergemertens thing
                            opencv_functions.myprint(window, "Align the preview images and then exposure fuse them")
                            if thumb_reference == "":
                                opencv_functions.align_fuse(window, values, resized_images, os.path.join(tmpfolder,'preview.jpg'), tmpfolder)
                            else:
                                opencv_functions.align_fuse(window, values, resized_images, os.path.join(tmpfolder,'preview.jpg'), tmpfolder)
                        else:
                            # Only do the mergemertens thing
                            opencv_functions.myprint(window, "Only do the mergemertens exposure fusion on the preview")
                    else:  # Only stack the preview
                        # Only align
                        opencv_functions.myprint(window, "Only align the images for stacking")
                        stacked_image = opencv_functions.which_stacking_metnod(window, values, all_filenames)
                        cv2.imwrite(os.path.join(tmpfolder, 'preview.jpg'), stacked_image)
                    stoptime = timeit.default_timer()
                    display_processing_time(window, starttime, stoptime)
                    ui_actions.disable_elements(window, False)
                    window.refresh()
                    if reference_image == "":
                        reference_image = resized_images[0]
                    image_functions.copy_exif_info(reference_image, os.path.join(tmpfolder, 'preview.jpg'))
                    print('preview filepath', os.path.join(tmpfolder, 'preview.jpg'))
                    image_functions.display_preview(window, os.path.join(tmpfolder, 'preview.jpg'))
                window['_CreateImage_'].set_focus(force=True)
            else: # 1 or 0 images selected
                sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
        elif event == '_CreateImage_':
            opencv_functions.myprint(window, '\nUser pressed "Create Exposure fused image\n')
            window['_proc_time_'].update('Processing time: --')
            file_functions.remove_temp_files()
            if len(read_errors) == 0:
                if len(values['-FILE LIST-']) > 1:  # We have at least 2 files
                    newFileName, full_images = image_functions.get_filename_images(values, folder)
                    if newFileName != '' and newFileName != 'Cancel':
                        #sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
                        ui_actions.disable_elements(window, True)
                        window.refresh()
                        starttime = timeit.default_timer()
                        newFileName = file_functions.check_filename(values, newFileName)
                        if values['_always_align_']:
                            #window.perform_long_operation(lambda : opencv_functions.align_fuse(values,ordered_filenames,os.path.join(folder,newFileName), tmpfolder), '-END KEY-')
                            #thread = threading.Thread(target=opencv_functions.align_fuse(values, ordered_filenames, os.path.join(folder, newFileName), tmpfolder), daemon=True)
                            #thread.start()
                            #window.start_thread(opencv_functions.align_fuse(window, values, ordered_filenames, os.path.join(folder, newFileName), tmpfolder), '-THREAD FINISHED-')
                            if reference_image == "":
                                opencv_functions.align_fuse(window, values, all_filenames, os.path.join(folder, newFileName), tmpfolder)
                            else:
                                opencv_functions.align_fuse(window, values, ordered_filenames, os.path.join(folder, newFileName), tmpfolder)
                        else:  # Create full image without using alignment
                            if reference_image == "":
                                opencv_functions.exposure_fuse(window, values, all_filenames, os.path.join(folder, newFileName), tmpfolder, "Full")
                            else:
                                opencv_functions.exposure_fuse(window, values, ordered_filenames, os.path.join(folder, newFileName), tmpfolder, "Full")
                        stoptime = timeit.default_timer()
                        display_processing_time(window, starttime, stoptime)
                        ui_actions.disable_elements(window, False)
                        #sg.popup_animated(None)
                        window.refresh()
                        # print('create reference_image: ', reference_image)
                        # print('null_image', null_image)
                        if reference_image == "":
                            reference_image = all_filenames[0]
                        image_functions.copy_exif_info(reference_image, os.path.join(folder, newFileName))
                        if values['_dispFinalIMG_']:
                            image_functions.displayImageWindow(os.path.join(folder, newFileName))
                    window['_CreateImage_'].set_focus(force=True)
                else:  # 1 or 0 images selected
                    sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
            else:
                sg.popup("At least one of the files could not be read. This means that no enfused image can be created.", icon=image_functions.get_icon(), auto_close=False)
        elif event == '_create_noise_reduced_':
            stacked_image = ""
            opencv_functions.myprint(window, '\nUser pressed "Create noise reduced image from stack"\n')
            window['_proc_time_'].update('Processing time: --')
            file_functions.remove_temp_files()
            if len(read_errors) == 0:
                if len(values['-FILE LIST-']) > 1:  # We have at least 2 files
                    newFileName, full_images = image_functions.get_filename_images(values, folder)
                    if newFileName != '' and newFileName != 'Cancel':
                        ui_actions.disable_elements(window, True)
                        window.refresh()
                        starttime = timeit.default_timer()
                        stacked_image = opencv_functions.which_stacking_metnod(window, values, all_filenames)
                        """
                        if values['_orb_']:
                            opencv_functions.myprint(window,"Stacking images using ORB method")
                            stacked_image = opencv_functions.stackImages_ORB_SIFT(window, values, all_filenames)
                        elif values['_ecc_']:
                            # Stack images using ECC method
                            opencv_functions.myprint(window,"Stacking images using ECC method")
                            stacked_image = opencv_functions.stackImagesECC(window, values, all_filenames)
                        else:
                            # Stack images using SIFT method
                            opencv_functions.myprint(window,"Stacking images using SIFT method")
                            stacked_image = opencv_functions.stackImages_ORB_SIFT(window, values, all_filenames)
                        """
                        cv2.imwrite(os.path.join(folder, newFileName), stacked_image)
                        stoptime = timeit.default_timer()
                        display_processing_time(window, starttime, stoptime)
                        ui_actions.disable_elements(window, False)
                        window.refresh()
                        # opencv_functions.myprint(window,'create reference_image: ', reference_image)
                        # opencv_functions.myprint(window,'null_image', null_image)
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
        elif event == '_create_focus_stacked_':
            opencv_functions.myprint(window,'\nUser pressed "Create focus stacked image"\n')
            #window['-STATUS-'].update('User pressed "Create focus stacked image"')
            window['_proc_time_'].update('Processing time: --')
            file_functions.remove_temp_files()
            if len(read_errors) == 0:
                if len(values['-FILE LIST-']) > 1:  # We have at least 2 files
                    newFileName, full_images = image_functions.get_filename_images(values, folder)
                    if newFileName != '' and newFileName != 'Cancel':
                        ui_actions.disable_elements(window, True)
                        window.refresh()
                        starttime = timeit.default_timer()
                        focus_stacked_image = opencv_functions.focus_stack(window, values, all_filenames)
                        cv2.imwrite(os.path.join(folder, newFileName), focus_stacked_image)
                        stoptime = timeit.default_timer()
                        display_processing_time(window, starttime, stoptime)
                        ui_actions.disable_elements(window, False)
                        window.refresh()
                        # opencv_functions.myprint(window,'create reference_image: ', reference_image)
                        # opencv_functions.myprint(window,'null_image', null_image)
                        if reference_image == "":
                            reference_image = null_image
                        image_functions.copy_exif_info(reference_image, os.path.join(folder, newFileName))
                        if values['_dispFinalIMG_']:
                            image_functions.displayImageWindow(os.path.join(folder, newFileName))
                    window['_CreateImage_'].set_focus(force=True)
                    #window['-STATUS-'].update('')
                else:  # 1 or 0 images selected
                    sg.popup("You need to select at least 2 images", icon=image_functions.get_icon())
            else:
                sg.popup("At least one of the files could not be read. This means that no enfused image can be created.", icon=image_functions.get_icon(), auto_close=False)
        elif event == '-END KEY-':
            return_value = values[event]
            window['-STATUS-'].update(f'Completed. Returned: {return_value}')


        # Do the thread actions and checks
        #if thread:
        #    sg.popup_animated(sg.DEFAULT_BASE64_LOADING_GIF, background_color='white', transparent_color='white', time_between_frames=100)
        #    thread.join(timeout=0)
        #    if not thread.is_alive():
        #        sg.popup_animated(None)
        #        thread = None
    window.Close()

 
#------------------- Main "boilerplate" function ----------------------------------------------
#----------------------------------------------------------------------------------------------

## Main program, main module
if __name__ == '__main__':
    main()
