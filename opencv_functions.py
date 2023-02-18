# -*- coding: utf-8 -*-

# opencv_functions.py
# This helper file does the aligning and exposure fusion using OpenCV
# However, currently it is not being used as its functionality
# is below align_image_stack and enfuse.

# Copyright (c) 2022-2023, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import os
import numpy as np
import imutils
import cv2
from time import time

def myprint(window, theString, status=False):
    print(theString)
    if status:
        window['_STATUS_'].update(theString)
    window.refresh()


import file_functions
################################# First the high level functions ###########################
def align_fuse(window, all_values, ordered_filenames, outputFileName, tmpfolder, filetype="Full"):
    """
    This function uses the opencv options to align (optionally, but default)
    and then exposure fuse the images
    the images are either the resized images for the preview, or the full images for the final result

    :param all_values:          This is the dictionary containing all UI key variables
    :type all_values:           (Dict[Any, Any]) - {Element_key : value}
    :param ordered_filenames:   The images to (optionally) align and fuse
    :type ordered_filenames:    (list)
    :param tmpfolder:           The dynamically created work folder in the OS temp folder
    :type tmpfolder:            (str)
    :param outputFileName:      The filename + path for the output file
    :type outputFileName:       (str)
    :param filetype:            (optional) Determines full size image (default) or preview
    :type filetype:             (str)
    """

    teller = 0
    ref_image_name = ""
    tmp_filenames = []
    other_filenames = []
    images = []
    basename_images = []
    amtb_images = []

    DEBUG = False

    #print("to start with " + outputFileName)
    tic = time()
    if all_values['_alignmtb_']:
        myprint(window, "[INFO] aligning images using alignMTB")
        for img_file in ordered_filenames:
            # alignMTB = cv2.createAlignMTB(int(all_values['_bitshiftCombo_']))
            im = cv2.imread(img_file, 1)
            images.append(im)
        alignMTB = cv2.createAlignMTB()
        alignMTB.process(images, images)
    else:
        #print("Now do the loop with the aligning with ORB or ECC")
        for img_file in ordered_filenames:
            if teller == 0:
                global ref_image
                global org_image_name
                org_image_name = img_file
                ref_image_name = os.path.join(tmpfolder,"aligned_" + os.path.basename(img_file))
                ref_image = cv2.imread(img_file)
                cv2.imwrite(os.path.join(tmpfolder,"aligned_" + os.path.basename(img_file)), ref_image)
                tmp_filenames.append(ref_image_name)
                basename_images.append(os.path.basename(img_file))
                teller += 1
            else:
                to_be_aligned = cv2.imread(img_file)
                # align the images
                if all_values['_orb_']:
                    myprint(window, "[INFO] align " + img_file + " against reference " + ref_image_name + " using ORB.")
                    window.refresh()
                    aligned = ORB_align_images(window, all_values, to_be_aligned, ref_image, maxFeatures=int(all_values['_maxfeatures_']), keepPercent=float(all_values['_keeppercent_']), debug=DEBUG)
                elif all_values['_ecc_']:
                    myprint(window, "[INFO] align " + img_file + " against reference " + ref_image_name + " using ECC")
                    aligned = ECC_align_images(window, all_values, to_be_aligned, ref_image, debug=DEBUG)
                    #aligned = aligned.astype(np.uint8) * 255
                elif all_values['_sift_']:
                    myprint(window, "[INFO] align " + img_file + " against reference " + ref_image_name + " using SIFT")
                    aligned = SIFT_align_images(to_be_aligned, ref_image, keepPercent=float(all_values['_keeppercent_']), debug=DEBUG)
                #myaligned = aligned.astype(np.float32) * 255
                #aligned = (aligned * 255).astype(np.uint8)
                cv2.imwrite(os.path.join(tmpfolder,"aligned_" + os.path.basename(img_file)), aligned)
                tmp_filenames.append(os.path.join(tmpfolder,"aligned_" + os.path.basename(img_file)))
                basename_images.append(os.path.basename(img_file))
                """
                else:
                    print("[INFO] align image " + img_file + " against reference image " + ref_image_name + " using ECC")
                    aligned = ECC_align_images(to_be_aligned, ref_image, debug=DEBUG)
                myaligned = aligned.astype(np.float32) * 255
                cv2.imwrite(("/tmp/aligned_" + img_file), aligned)
                tmp_filenames.append("/tmp/aligned_" + img_file)
                """

        myprint(window, images)
        myprint(window, "[INFO] Reading aligned images from " + tmpfolder + " for exposure fusion.")
        for filename in tmp_filenames:
            myprint(window, "[INFO] Reading aligned image for exposure fusion " + filename)
            im = cv2.imread(filename)
            images.append(im)


    # Merge using Exposure Fusion
    myprint(window, "\nMerging using Exposure Fusion ... ");
    mergeMertens = cv2.createMergeMertens()
    # get our (optional) parameters
    mergeMertens.setContrastWeight(all_values['_cv_contrast_weight_'])
    mergeMertens.setExposureWeight(all_values['_cv_exposure_weight_'])
    mergeMertens.setSaturationWeight(all_values['_cv_saturation_weight_'])
    exposureFusion = mergeMertens.process(images)


    myprint(window, "aligned and exposure fused {0} in {1} seconds".format(len(images), (time()-tic) ))

    myprint(window, "Saving {}".format(outputFileName))
    # multiply by 255 to create an 8bit image
    cv2.imwrite(outputFileName, exposureFusion * 255, [int(cv2.IMWRITE_JPEG_QUALITY), 95])


# Mostly copied from https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
def exposure_fuse(window, all_values, ordered_filenames, outputFileName, tmpfolder, filetype="Full"):
    """
    This function uses the opencv options to align (optionally, but default)
    and then exposure fuse the images
    the images are either the resized images for the preview, or the full images for the final result

    :param all_values:          This is the dictionary containing all UI key variables
    :type all_values:           (Dict[Any, Any]) - {Element_key : value}
    :param ordered_filenames:   The images to (optionally) align and fuse
    :type ordered_filenames:    (list)
    :param tmpfolder:           The dynamically created work folder in the OS temp folder
    :type tmpfolder:            (str)
    :param outputFileName:      The filename + path for the output file
    :type outputFileName:       (str)
    :param filetype:            (optional) Determines full size image (default) or preview
    :type filetype:             (str)
    """
    work_images = []
    processed_images = None
    # processed_work_images = []
    for image in ordered_filenames:
        im = cv2.imread(image)
        work_images.append(im)

    myprint(window, "\nMerging using Exposure Fusion ...\n")
    mergeMertens = cv2.createMergeMertens()
    mergeMertens.setContrastWeight(all_values['_cv_contrast_weight_'])
    mergeMertens.setExposureWeight(all_values['_cv_exposure_weight_'])
    mergeMertens.setSaturationWeight(all_values['_cv_saturation_weight_'])
    exposureFusion = mergeMertens.process(work_images)
    if filetype.lower() == 'preview':
        myprint(window, "\nSaving preview image ...\n")
        # Use tmpfolder for cross-platform. Now a quick hack
        cv2.imwrite(os.path.join(tmpfolder, 'preview.jpg'), exposureFusion * 255)  # * 255 to get an 8-bit image
    else:
        myprint(window, "\nSaving finale fused image ...\n")
        cv2_image = exposureFusion * 255
        #file_functions.save_file(str(filetype), cv2_image)
        cv2.imwrite(outputFileName, cv2_image)




def ORB_align_images(window, all_values, image, ref_image, maxFeatures=500, keepPercent=0.3, debug=False):
    # convert both the input image and ref_image to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ref_imageGray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)

    """
    # use ORB to detect keypoints and extract (binary) local
    # invariant features
    orb = cv2.ORB_create(maxFeatures)
    (kpsA, descsA) = orb.detectAndCompute(imageGray, None)
    (kpsB, descsB) = orb.detectAndCompute(ref_imageGray, None)
    """

    if all_values['_orb_orb_desc_']:
        myprint(window, 'Running ORB with ORB detector and descriptor')
        orb = cv2.ORB_create(maxFeatures)
        (kpsA, descsA) = orb.detectAndCompute(imageGray, None)
        (kpsB, descsB) = orb.detectAndCompute(ref_imageGray, None)
    else: # use the BEBLID descriptor
        myprint(window, 'Running ORB with ORB detector and BEBLID descriptor')
        detector = cv2.ORB_create(maxFeatures)
        kpsA = detector.detect(imageGray, None)
        kpsB = detector.detect(ref_imageGray, None)
        descriptor = cv2.BEBLID_create(0.75)
        kpsA, descsA = descriptor.compute(imageGray, kpsA)
        kpsB, descsB = descriptor.compute(ref_imageGray, kpsB)

    # match the features
    method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
    matcher = cv2.DescriptorMatcher_create(method)

    matches = matcher.match(descsA, descsB, None)

    # sort the matches by their distance (the smaller the distance,
    # the "more similar" the features are)
    matches = sorted(matches, key=lambda x: x.distance)
    # keep only the top matches
    keep = int(len(matches) * keepPercent)
    matches = matches[:keep]

    # check to see if we should visualize the matched keypoints
    if debug:
        matchedVis = cv2.drawMatches(image, kpsA, ref_image, kpsB,
                                     matches, None)
        matchedVis = imutils.resize(matchedVis, width=1600)
        cv2.imshow("Matched Keypoints", matchedVis)
        cv2.waitKey(0)
    # allocate memory for the keypoints (x, y)-coordinates from the
    # top matches -- we'll use these coordinates to compute our
    # homography matrix
    ptsA = np.zeros((len(matches), 2), dtype="float")
    ptsB = np.zeros((len(matches), 2), dtype="float")
    # loop over the top matches
    for (i, m) in enumerate(matches):
        # indicate that the two keypoints in the respective images
        # map to each other
        ptsA[i] = kpsA[m.queryIdx].pt
        ptsB[i] = kpsB[m.trainIdx].pt
    # compute the homography matrix between the two sets of matched
    # points
    (H, mask) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, 5.0)
    # use the homography matrix to align the images
    (h, w) = ref_image.shape[:2]
    aligned = cv2.warpPerspective(image, H, (w, h))
    # return the aligned image
    return aligned
    """
        # crop the black borders of the image
    _,thresh = cv2.threshold(aligned,1,255,cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    x,y,w,h = cv2.boundingRect(cnt)
    aligned_cropped = img[y:y+h,x:x+w]
    return aligned_cropped
    """



# Based on https://learnopencv.com/image-alignment-ecc-in-opencv-c-python/
def ECC_align_images(window, values, image, ref_image, number_of_iterations=500, termination_eps=1e-10, debug=False):
    # Convert images to grayscale
    ref_image = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Find size of image1
    sz = ref_image.shape

    if values['_homography_']:
        warp_matrix = np.eye(3, 3, dtype=np.float32)
        warp_mode = cv2.MOTION_HOMOGRAPHY
        myprint(window, "warpmode MOTION_HOMOGRAPHY")
    else:
        warp_matrix = np.eye(2, 3, dtype=np.float32)
        if values['_affine_']:
            warp_mode = cv2.MOTION_AFFINE
            myprint(window, "warpmode MOTION_AFFINE")
        elif values['_euclidean_']:
            warp_mode = cv2.MOTION_EUCLIDEAN
            myprint(window, "warpmode MOTION_EUCLIDEAN")
        elif values['_translation_']:
            warp_mode = cv2.MOTION_TRANSLATION
            myprint(window, "warpmode MOTION_TRANSLATION")

    # termination_eps is the threshold of the increment
    # in the correlation coefficient between two iterations
    # Define termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations, termination_eps)

    # Run the ECC algorithm with the defined warp_mode. The results are stored in warp_matrix.
    (cc, warp_matrix) = cv2.findTransformECC(image, ref_image, warp_matrix, warp_mode, criteria)

    if warp_mode == cv2.MOTION_HOMOGRAPHY:
        # Use warpPerspective for Homography
        image_aligned = cv2.warpPerspective(image, warp_matrix, (sz[1], sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else:
        #Use warpAffine for Translation, Euclidean and Affine
        image_aligned = cv2.warpAffine(image, warp_matrix, (sz[1], sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);

    # Show final results
    if debug:
        cv2.imshow("Image 1", ref_image)
        cv2.imshow("Image 2", image)
        cv2.imshow("Aligned Image 2", image_aligned)
        cv2.waitKey(0)

    #return cv2.cvtColor((image_aligned).astype(np.uint8),cv2.COLOR_GRAY2RGB)
    return image_aligned



def SIFT_align_images(image, ref_image, nFeatures=20, matchdistance=0.65, debug=False):
    # convert both the input image and ref_image to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ref_imageGray = cv2.cvtColor(ref_image, cv2.COLOR_BGR2GRAY)

    # "sift"the 2 images"
    #sift = cv2.SIFT_create(nFeatures)
    sift = cv2.SIFT_create()
    (keypointsA, descriptorsA) = sift.detectAndCompute(imageGray, None)
    (keypointsB, descriptorsB) = sift.detectAndCompute(ref_imageGray, None)

    bf = cv2.BFMatcher()
    matches = bf.match(descriptorsA, descriptorsB)
    matches = sorted(matches, key=lambda x: x.distance)
    # keep only the top matches
    keep = int(len(matches) * matchdistance)
    matches = matches[:keep]

    # allocate memory for the keypoints (x, y)-coordinates from the
    # top matches -- we'll use these coordinates to compute our
    # homography matrix
    ptsA = np.zeros((len(matches), 2), dtype="float")
    ptsB = np.zeros((len(matches), 2), dtype="float")
    # loop over the top matches
    for (i, m) in enumerate(matches):
        # indicate that the two keypoints in the respective images
        # map to each other
        ptsA[i] = keypointsA[m.queryIdx].pt
        ptsB[i] = keypointsB[m.trainIdx].pt

    # compute the homography matrix between the two sets of matched
    # points
    (warp_matrix, mask) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC)
    # use the homography matrix to align the images
    (height, width) = ref_image.shape[:2]
    # Check
    warp_matrix = np.eye(3, 3, dtype=np.float32) # according cv2.MOTION_HOMOGRAPHY

    aligned = cv2.warpPerspective(image, warp_matrix, (width, height))
    # return the aligned image
    return aligned


# Function to check which stacking is used, both for final image
# as well as preview image
def which_stacking_metnod(window, values, all_filenames):
    if values['_orb_']:
        myprint(window, "Stacking images using ORB method")
        stacked_image = stackImages_ORB_SIFT(window, values, all_filenames)
    elif values['_ecc_']:
        # Stack images using ECC method
        myprint(window, "Stacking images using ECC method")
        stacked_image = stackImagesECC(window, values, all_filenames)
    else:
        # Stack images using SIFT method
        myprint(window, "Stacking images using SIFT method")
        stacked_image = stackImages_ORB_SIFT(window, values, all_filenames)

    return stacked_image

# Align and stack images with ECC method
# Much slower but better in case of huge exposure differences
def stackImagesECC(window, values, file_list):

    M = None
    warpmode = None
    # warp_mode = cv2.MOTION_TRANSLATION # shifted compared to other image
    # warp_mode = cv2.MOTION_EUCLIDEAN  # rotation and shift (translation)
    # warp_mode = cv2.MOTION_AFFINE       # rotation, shift (translation), scale and shear
    # warp_mode = cv2.MOTION_HOMOGRAPHY    # All above are 2D; This one also accounts for some 3D effects.

    if values['_homography_']:
        M = np.eye(3, 3, dtype=np.float32)
        warpmode = cv2.MOTION_HOMOGRAPHY
        myprint(window, "warpmode MOTION_HOMOGRAPHY")
    else:
        M = np.eye(2, 3, dtype=np.float32)
        if values['_affine_']:
            warpmode = cv2.MOTION_AFFINE
            myprint(window, "warpmode MOTION_AFFINE")
        elif values['_euclidean_']:
            warpmode = cv2.MOTION_EUCLIDEAN
            myprint(window, "warpmode MOTION_EUCLIDEAN")
        else:
            warpmode = cv2.MOTION_TRANSLATION
            myprint(window, "warpmode MOTION_TRANSLATION")


    first_image = None
    stacked_image = None

    for file in file_list:
        image = cv2.imread(file,1).astype(np.float32) / 255
        #image = cv2.imread(file, 1)
        myprint(window, "opencv open image " + file)
        if first_image is None:
            # convert to gray scale floating point image
            first_image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
            stacked_image = image
        else:
            # Estimate perspective transform
            s, M = cv2.findTransformECC(cv2.cvtColor(image,cv2.COLOR_BGR2GRAY), first_image, M, warpmode)
            w, h, _ = image.shape
            # Align image to first image
            if (warpmode == cv2.MOTION_HOMOGRAPHY):
                image = cv2.warpPerspective(image, M, (h, w))
            else:
                image = cv2.warpAffine(image, M, (h, w))
            stacked_image += image

    stacked_image /= len(file_list)
    stacked_image = (stacked_image*255).astype(np.uint8)
    return stacked_image


def stackImages_ORB_SIFT(window, values, file_list):

    featuresmethod = None
    matcherType = None

    if values['_orb_']:
        featuresmethod = cv2.ORB_create(nfeatures=int(values['_maxfeatures_']))
        matcherType = cv2.NORM_HAMMING
    else:
        featuresmethod = cv2.SIFT_create()
        matcherType = cv2.NORM_L2

    stacked_image = None
    first_image = None
    first_kp = None
    first_des = None
    for file in file_list:
        myprint(window, "opencv open " + file)
        image = cv2.imread(file,1)
        imageF = image.astype(np.float32) / 255

        # compute the keypoints and then the descriptors
        kp = featuresmethod.detect(image, None)
        kp, des = featuresmethod.compute(image, kp)
        """
        if orb_orb => featuresmethod = cv2.ORB_create
        if orb_beblid => featuresmethod = cv2.ORB_create + cv2.BEBLID
        if sift => sift
        """


        # create BFMatcher object
        matcher = cv2.BFMatcher(matcherType, crossCheck=True)

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
            # keep only the top matches
            #keep = int(len(matches) * values['_keeppercent_'])
            #matches = matches[:keep]

            match_error = 0
            try:
                keep = int(len(matches) * values['_keeppercent_'])
                matches = matches[:keep]
            except Exception as e:
                #myprint(window, "\nCan't determine the top matches as we do not have enough matches after the keeppercent.\n")
                match_error += match_error
                pass
            if match_error > 0:
                myprint(window, "\nCan't determine the top matches as we do not have enough matches after the keeppercent.\n")

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




################## Focus stacking ###############################
# Started with: https://github.com/cmcguinness/focusstack
# Improved version?: https://github.com/momonala/focus-stack
# This will still require some optimization and use of my current alignment routines
def findHomography(image_1_kp, image_2_kp, matches):
    image_1_points = np.zeros((len(matches), 1, 2), dtype=np.float32)
    image_2_points = np.zeros((len(matches), 1, 2), dtype=np.float32)

    for i in range(0,len(matches)):
        image_1_points[i] = image_1_kp[matches[i].queryIdx].pt
        image_2_points[i] = image_2_kp[matches[i].trainIdx].pt

    homography, mask = cv2.findHomography(image_1_points, image_2_points, cv2.RANSAC, ransacReprojThreshold=2.0)

    return homography


def align_images(window, values, file_list):

    outimages = []

    if values['_sift_']:
        detector = cv2.SIFT_create()
    else:
        detector = cv2.ORB_create(5000)

    #   We assume that image 0 is the "base" image and align everything to it
    myprint(window, "Detecting features of base image")
    outimages.append(file_list[0])
    image1gray = cv2.cvtColor(file_list[0],cv2.COLOR_BGR2GRAY)
    image_1_kp, image_1_desc = detector.detectAndCompute(image1gray, None)

    for i in range(1,len(file_list)):
        myprint(window, "Aligning image {}".format(i))
        image_i_kp, image_i_desc = detector.detectAndCompute(file_list[i], None)

        if values['_sift_']:
            bf = cv2.BFMatcher()
            # This returns the top two matches for each feature point (list of list)
            pairMatches = bf.knnMatch(image_i_desc,image_1_desc, k=2)
            rawMatches = []
            for m,n in pairMatches:
                if m.distance < 0.7*n.distance:
                    rawMatches.append(m)
        else:
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            rawMatches = bf.match(image_i_desc, image_1_desc)

        sortMatches = sorted(rawMatches, key=lambda x: x.distance)
        matches = sortMatches[0:128]

        hom = findHomography(image_i_kp, image_1_kp, matches)
        newimage = cv2.warpPerspective(file_list[i], hom, (file_list[i].shape[1], file_list[i].shape[0]), flags=cv2.INTER_LINEAR)

        outimages.append(newimage)
        # If you find that there's a large amount of ghosting, it may be because one or more of the input
        # images gets misaligned.  Outputting the aligned images may help diagnose that.
        # cv2.imwrite("aligned{}.png".format(i), newimage)

    return outimages


#
#   This routine finds the points of best focus in all images and produces a merged result...
#
def focus_stack(window, values, file_list, kernel_size=5, blur_size=5):
    opencv_images = []
    for img in file_list:
        im = cv2.imread(img)
        opencv_images.append(im)
    images = align_images(window, values, opencv_images)

    myprint(window, "Computing the laplacian of the blurred images")
    laps = []
    for i in range(len(images)):
        myprint(window, "Lap {}".format(i))
        image = cv2.cvtColor(images[i], cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(image, (blur_size, blur_size), 0)
        lap_blurred = cv2.Laplacian(blurred, cv2.CV_64F, ksize=kernel_size)
        #laps.append(doLap(cv2.cvtColor(images[i], cv2.COLOR_BGR2GRAY)))
        laps.append(lap_blurred)

    laps = np.asarray(laps)
    myprint(window, "Shape of array of laplacians = {}".format(laps.shape))
    output = np.zeros(shape=images[0].shape, dtype=images[0].dtype)

    abs_laps = np.absolute(laps)
    maxima = abs_laps.max(axis=0)
    bool_mask = abs_laps == maxima
    mask = bool_mask.astype(np.uint8)
    for i in range(0, len(images)):
        output = cv2.bitwise_not(images[i], output, mask=mask[i])

    return 255 - output