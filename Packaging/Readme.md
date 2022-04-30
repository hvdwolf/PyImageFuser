# Building distributable binaries

In here you will find the the scripts and config file I use to build distributable binaries.
They all work with relative paths the way I have set them up in my 3 systems.
They do not contain the pre-compiled enfuse and align_image_stack (and neither the scripts I use
to make them distributable).  
I decided not to pack "everything" in one big Python executable, but to leave the data files
and enfuse and align_image_stack outside the Python executable, also to make the application start faster.

HvdW, 2022-04-30