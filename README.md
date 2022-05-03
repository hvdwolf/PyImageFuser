# PyImageFuser
PyImageFuser is a Python3 PySimpleGui program to exposure fuse bracketed images, reduce noise in stacks and do focus stacking. It uses align_image_stack and enfuse to accomplish this.

<!--- ![splash](https://github.com/hvdwolf/PyImageFuser/raw/main/artwork/splash.png) --->
![main screen linux](https://github.com/hvdwolf/PyImageFuser/raw/main/screenshots/PIF-main-xfce4.jpg)

[More screenshots also for Windows and MacOS](screenshots/README.md)

## In development, no releases yet.

## Why doing Exposure Fusion?

Currently, the best cameras on the market have a dynamic range of around 15 stops on average, and 12-13 for the average models.
Compact cameras and phones even less.  

The human eye has a dynamic range of 20-21 stops.  
Our eyes are able to pick up details in deep shadow, but simultaneously also from significantly brighter areas from any given scene.  
Actually our eyes are not that much better but our brains "image algorithms" are much better and also adapt automatically to our focus points of attention and correct these.  

We can try to achieve the same using a set of photos with different exposure. This is called exposure bracketing.  
Most modern camera's support "auto bracketing". You make a photo in "auto bracketing" mode and your camera will take (in general) three photos: a 0EV standard exposure image, a -1EV underexposed image and a +1EV overexposed image.
Almost all camera's have a manual setting to compensate from -2EV (or -3EV) to +2EV (or +3EV) and sometimes more.
These manual settings are preferred over the standard "auto" mode which is mostly limited to -1/+1 EV.  
More about this, what the parameters mean and tips & tricks to improve your results in the Help menu.

## Choise of "tools"
Why use the external enfuse and align_image_stack and not the internal OpenCV/numpy modules to align (alignMTB/ECC/ORB) and exposure fuse (mergeMertens)?  
I started with [OpenCV](https://github.com/hvdwolf/PyImageFuser/tree/opencv), but in all my tests especially align_image_stack outperforms the OpenCV alignmnent methods. The OpenCV methods are equal at best, but in 50% of the cases they perform worse. Sometimes clearly visible, sometimes visible when zooming in.  
OpenCV mergeMertens is comparable with enfuse (which also uses Mertens), but enfuse is a little more tweakable although you will not use that in 95% of the cases. For "focus stacks" you really need enfuse.



## Installing
**No releases yet**
<!--- Either download one of the pyinstaller packages from the [Releases](https://github.com/hvdwolf/PyImageFuser/releases) page.
Unzip it so some place of your liking and start the binary with:

* "PyImageFuser &" (Linux)
* "PyImageFuser.exe" (Windows)
* "PyImageFuser &" (MacOS). *(There is no bundle yet. Maybe later.)*
--->
Download this python code and run the following command to install the dependencies:

    python3 -m pip install -r requirements.txt

Then start PyImageFuser with:

    python3 PyImageFuser.py

