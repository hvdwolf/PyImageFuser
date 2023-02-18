#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob, os, sys
import cv2
import numpy as np
from time import time


# From: https://github.com/maitek/image_stacking

# Align and stack images by matching ORB keypoints (KeyPointMarching)
def stackImagesORB(file_list):

    orb = cv2.ORB_create(nfeatures=5000) #instead of default nlevels = 8 and scaleFactor = 1.2f => scaleFactor=1.4, nlevels = 10

    # disable OpenCL to because of bug in ORB in OpenCV 3.1
    #cv2.ocl.setUseOpenCL(False)

    stacked_image = None
    first_image = None
    first_kp = None
    first_des = None
    for file in file_list:
        print(file)
        image = cv2.imread(file,1)
        imageF = image.astype(np.float32) / 255

        # compute the descriptors with ORB
        kp = orb.detect(image, None)
        kp, des = orb.compute(image, kp)

        # create BFMatcher object
        matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        if first_image is None:
            # Save keypoints for first image
            stacked_image = imageF
            first_image = image
            first_kp = kp
            first_des = des
        else:
             # Find matches and sort them in the order of their distance
            matches = matcher.match(first_des, des)
            matches = sorted(matches, key=lambda x: x.distance)

            src_pts = np.float32(
                [first_kp[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
            dst_pts = np.float32(
                [kp[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)

            # Estimate perspective transformation
            M, mask = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
            w, h, _ = imageF.shape
            imageF = cv2.warpPerspective(imageF, M, (h, w))
            stacked_image += imageF

    stacked_image /= len(file_list)
    stacked_image = (stacked_image*255).astype(np.uint8)
    return stacked_image





# Align and stack images with ECC method
# Much slower but better in case of huge exposure differences
def stackImagesECC(file_list):
    M = np.eye(3, 3, dtype=np.float32)

    first_image = None
    stacked_image = None

    for file in file_list:
        image = cv2.imread(file,1).astype(np.float32) / 255
        print(file)
        if first_image is None:
            # convert to gray scale floating point image
            first_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            stacked_image = image
        else:
            # Estimate perspective transform
            s, M = cv2.findTransformECC(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY), first_image, M, cv2.MOTION_HOMOGRAPHY)
            w, h, _ = image.shape
            # Align image to first image
            image = cv2.warpPerspective(image, M, (h, w))
            stacked_image += image

    stacked_image /= len(file_list)
    stacked_image = (stacked_image*255).astype(np.uint8)
    return stacked_image

def Info():
    print("\nUse opencv_stack.py with opencv_stack.py \"image name.jpg\" \"files to use\"  \"(Optional) method -> ECC or ORB\"")
    print("Note that you need to use double quotes around the wildcard like \"IMG*\"\n")
    sys.exit(1)


# ===== MAIN =====

if __name__ == '__main__':



    #for arg in sys.argv:
    #    print(arg)
    if len(sys.argv) < 3:
       Info()
    elif len(sys.argv) == 4:  # script (0) imagename (1) filestouse(2) method(3)
        #print("3 " + sys.argv[3])
        global method 
        method = sys.argv[3]
    else:
        method = "ORB"

    if ("--help" in sys.argv[1]) or ("-help" in sys.argv[1]):
        Info()
    else:
        print("\nDID YOU THINK TO EMBED THE IMAGES BETWEEN DOUBLE QUOTES? like \"img*\".\n\n")
        global myimage
        myimage = sys.argv[1]
    #print("myimage " + myimage)
    file_list = glob.glob(sys.argv[2])
    teller = 0
    for file in file_list:
        print("Reading image " + file)
        if teller == 0:
            global first_image
            first_image = file
            teller += 1
    print("\n\n")
    tic = time()

    print("Chosen method " + method)
    if method == "ORB":
        description = "Stacking images using ORB method"
        print(description)
        stacked_image = stackImagesORB(file_list)
    else:    
        # Stack images using ECC method
        description = "Stacking images using ECC method"
        print(description)
        stacked_image = stackImagesECC(file_list)


    print("Stacked {0} in {1} seconds".format(len(file_list), (time()-tic) ))

    print("Saved {}".format(myimage))
    cv2.imwrite(myimage,stacked_image)

    # Do the necessary exiftool stuff
    # os.system("ffmpeg -i " + filename + " -qscale:v 2 -vf fps=1 " + os.path.join(begin, begin+ "-%03d.jpg"));
    os.system("exiftool -overwrite_original -TagsFromFile " + first_image + " -all " + myimage)
    os.system("exiftool -v \"-CreateDate>FileModifyDate\" -overwrite_original " + myimage)
    # Show image
    #if args.show:
    #cv2.imshow(description, stacked_image)
    #cv2.waitKey(0)
