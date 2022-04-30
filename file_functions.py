# -*- coding: utf-8 -*-

# file_functions.py - This python helper scripts holds the user interface functions

# Copyright (c) 2022, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import glob, os, shutil, sys

import PySimpleGUI as sg

import image_functions


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        print('pyinstaller temp path: ', base_path)
    except Exception:
        base_path = os.path.realpath(".")

    return os.path.join(os.path.realpath(base_path), relative_path)


# This functions (re)creates our work folder which is a subfolder
# of the platform define tmp folder
def recreate_tmp_workfolder(tmp_folder):
    #tmp_folder = os.path.join(tempfile.gettempdir(), 'jimgfuse')
    if os.path.exists(tmp_folder):
        try:
            shutil.rmtree(tmp_folder) # emove all contents of the folder
            os.mkdir(tmp_folder) # recreate folder
        except:
            print('Error deleting directory')
        # Now leave it be as it is now empty
    else: # It does not exist so we need to recreate it
        os.mkdir(tmp_folder)

def remove_tmp_workfolder(tmp_folder):

    if os.path.exists(tmp_folder):
        try:
            shutil.rmtree(tmp_folder) # emove folder with all contents
        except:
            print('Error deleting directory')

def remove_files(filepattern):
    fileList = glob.glob(filepattern)
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)
            

def readFile(filename):
    # read the file using readlines
    orgFile = open(filename, 'r', encoding='utf-8')
    Lines = orgFile.readlines()
    orgFile.close()
    return Lines

def writeFile(filename, Lines):
    newFile = open(filename, 'w', encoding='utf-8')
    newFile.writelines(Lines)
    newFile.close()

def getFileName(folder):
    folderInputTxt = ""
    if folder == '':
        foldertxt = 'Select a folder for your output image'
    else:
        foldertxt = 'You selected the images source folder as destination.\nClick "Browse" to select another folder'
        folderInputTxt = folder

    layout = [[sg.Text('Enter the image filename:', font = ('Calibri', 10, 'bold'))],
              #[sg.Text('The fileformat to save to is determined by the extension, which is either .jp(e)g, .tif(f) or .png')],
              #[sg.Text('Without extension it will be saved as jpg in the quality as specified in the "Preferences"')],
              [sg.Input(key='-FILENAME-')],
              [sg.Text(foldertxt)],
              [sg.Input(folderInputTxt, key='-FOLDER-'), sg.FolderBrowse()],
              [sg.B('OK',  bind_return_key=True), sg.B('Cancel'), ]]

    window = sg.Window('Provide a filename', layout, icon=image_functions.get_icon())
    while True:
        event, values = window.read()
        if event in(sg.WINDOW_CLOSED, 'Cancel'):
            folder = ''
            fileName = 'Cancel'
            break
        elif event == 'OK':
            fileName= values['-FILENAME-']
            folder = values['-FOLDER-']
            break

    window.close()
    return folder, fileName

def check_filename(values, fileName):

    basename, extension = os.path.splitext(fileName)
    ext = extension.lower()
    if ext == '' or len(ext) == 0: # which means the user did not give an extension
        if values['_jpg_']:
            fileName = fileName + '.jpg'
        else:
            fileName = fileName + '.tif'

    return fileName


# This functions gets the file sizes of the preview images
def getFileSizes(all_values, tmpfolder):
    is_zero = 0

    files = all_values['-FILE LIST-']
    for file in files:
        previewfile = os.path.join(tmpfolder, file)
        if os.path.getsize(previewfile) == 0:
            is_zero += 1
    return is_zero