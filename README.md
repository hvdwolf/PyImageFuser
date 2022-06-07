# PyImageFuser
PyImageFuser is a Python3 PySimpleGUI program to exposure fuse bracketed images, reduce noise in stacks and do focus stacking. It uses align_image_stack and enfuse to accomplish this.

<!--- ![splash](https://github.com/hvdwolf/PyImageFuser/raw/main/artwork/splash.png) --->
![main screen linux](https://github.com/hvdwolf/PyImageFuser/raw/main/screenshots/PIF-main-xfce4.jpg)

[More screenshots also for Windows and MacOS](screenshots/README.md)  

Downloadable packages on the [Releases](https://github.com/hvdwolf/PyImageFuser/releases) page.  


## Why doing Exposure Fusion?

Currently, the best cameras on the market have a dynamic range of around 15 stops on average, and 12-13 for the average models.
Compact cameras and phones even less.  

The human eye has a dynamic range of 20-21 stops.  
Our eyes are able to pick up details in deep shadow, but simultaneously also from significantly brighter areas from any given scene.  
Actually our eyes are not that much better but the "image algorithms" of our brains are much better and also adapt automatically to our focus points of attention and correct for these focus points.  

We can try to achieve the same using a set of photos with different exposure. This is called exposure bracketing.  
Most modern camera's support "auto bracketing". You make a photo in "auto bracketing" mode and your camera will take (in general) three photos: a 0EV standard exposure image, a -1EV underexposed image and a +1EV overexposed image.
Almost all camera's have a manual setting to compensate from -2EV (or -3EV) to +2EV (or +3EV) and sometimes more.
These manual settings are preferred over the standard "auto" mode which is mostly limited to -1/+1 EV.  
More about this, what the parameters mean and tips & tricks to improve your results in the Help menu.

Nowadays a lot of cameras can also do "in camera" HDR and some can do "in camera" bracketing to a final exposure bracketed image. Due to limited CPU capacity this is often not as good as what can be achieved on a PC/laptop. Next to that: None of the current cameras has the ability to align the images before exposure processing as the CPU performance seriously falls short for this alignment.

## Choise of "tools"
Why use the external enfuse and align_image_stack and not the internal OpenCV/numpy modules to align (alignMTB/ECC/ORB) and exposure fuse (mergeMertens)?  
I started with [OpenCV](https://github.com/hvdwolf/PyImageFuser/tree/opencv), but in all my tests especially align_image_stack outperforms the OpenCV alignmnent methods. The OpenCV methods are equal at best, but in 50% (my rough judgement) of the cases they really perform worse. Sometimes clearly visible, sometimes visible when zooming in.  
OpenCV mergeMertens is comparable with enfuse (which also uses Mertens), but enfuse is a little more tweakable although you will not use that in 95% of the cases. For "focus stacks" you really need enfuse.



## Installing
Either download one of the binary packages from the [Releases](https://github.com/hvdwolf/PyImageFuser/releases) page.
Unzip it so some place of your liking and start the binary with:

* "pyimagefuser &" (Linux deb package)
* From the folder where downloaded/copied: "PyImageFuser-<version>-x86_64.AppImage &" (Linux x64 AppImage)
* From the folder where unzipped: "PyImageFuser.exe" (Windows)
* Open the dmg and drag the PyImageFuser.app to the Applications folder (or another folder of your liking).

**Or:**
Download this python code and run the following command to install the dependencies:

    python3 -m pip install -r requirements.txt
    Install enfuse and align_image_stack for your system.

Then start PyImageFuser with:

    python3 PyImageFuser.py

