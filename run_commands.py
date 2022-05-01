# -*- coding: utf-8 -*-

# run_commands.py - This python helper scripts holds the several to be executed commands

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
import platform, subprocess


def run_command(cmdstring):
    retstring = ""
    result = subprocess.run(cmdstring, shell=True)
    if result.returncode != 0:
        retstring =  "Something went wrong"
    else:
        retstring = "OK"
    return retstring

def run_shell_command(cmdstring, arguments, waitmessage, output):
    retstring = ""
    if platform.system() == 'Windows':
        result = sg.shell_with_animation(cmdstring, arguments, message=waitmessage, font='Helvetica 15', no_titlebar=True, alpha_channel=0.90)
    else:
        tlist = []
        result = sg.shell_with_animation(cmdstring, tlist, message=waitmessage, font='Helvetica 15', no_titlebar=True, alpha_channel=0.90)

    if output:
        sg.popup_scrolled(result, font='Courier 10')

    if 'error' in result or 'Error' in result:
        retstring = "Something went wrong"
    else:
        retstring = "OK"
    return retstring