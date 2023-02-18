# Building distributable binaries

In here you will find the the scripts and config file I use to build distributable binaries.
They all work with relative paths the way I have set them up in my 3 systems.
These scripts and source code tree do not contain the pre-compiled enfuse and align_image_stack packaged in the AppImage, the Windows build and the MacOS bundel (and contain neither the scripts I use to make enfuse and align_image_stack distributable).  
PyInstaller is use to make the python binaries for the several platforms.


PyInstaller and OpenCV
Error:
    raise ImportError('ERROR: recursion is detected during loading of "cv2" binary extensions. Check OpenCV installation.')
ImportError: ERROR: recursion is detected during loading of "cv2" binary extensions. Check OpenCV installation.
[6534] Failed to execute script 'PyImageFuser' due to unhandled exception!

Solution: Install older version of opencv
python3 -m pip install pencv-python==4.5.3.56

Then run pyinstaller again.

HvdW, 2023-02-16.
HvdW, 2022-05-29.
