# -*- coding: utf-8 -*-

# opencv.py
# This helper file does the aligning and exposure fusion using OpenCV
# However, currently it is not being used as its functionality
# is below align_image_stack and enfuse.

# Copyright (c) 2022, Harry van der Wolf. all rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import os

import file_functions

# Do not forget to re-enable below 2 in case of using OpenCV
#import cv2
#import numpy as np

################################ Bring Back the opencv functionality ########################
# Do not forget to re-enambe the import of cv2 and numpy
# Mostly copied from https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
def opencv_align_fuse(all_values, images, tmpfolder, filename_type, align_YN):
    """
    This function uses the opencv options to align (optionally, but default)
    and then exposure fuse the images
    the images are either the resized images for the preview, or the full images for the final result

    :param all_values:      This is the dictionary containing all UI key variables
    :type all_values:       (Dict[Any, Any]) - {Element_key : value}
    :param images:          The images to (optionally) align and fuse
    :type images:           (list)
    :param tmpfolder:       The dynamically created work folder in the OS temp folder
    :type tmpfolder:        (str)
    :param filename_type:   Either the real final filename or a string 'preview'
    :type filename_type:    (str)
    :param align_YN:        Determines whether the user wants to align (default) or not
    :type align_YN:         (bool)
    """
    work_images = []
    processed_images = None
    # processed_work_images = []
    for image in images:
        im = cv2.imread(image)
        work_images.append(im)

    if align_YN:  # True
        if filename_type == 'preview':
            print("Aligning preview images using alignMTB ...\n")
        else:
            print("Aligning full size images using alignMTB ...\n")
        # alignMTB = cv2.createAlignMTB()
        alignMTB = cv2.createAlignMTB(int(all_values['_bitshiftCombo_']))
        alignMTB.process(work_images, work_images)

    print("\nMerging using Exposure Fusion ...\n")
    mergeMertens = cv2.createMergeMertens()
    mergeMertens.setContrastWeight(all_values['_contrast_weight_'])
    mergeMertens.setExposureWeight(all_values['_exposure_weight_'])
    mergeMertens.setSaturationWeight(all_values['_saturation_weight_'])
    exposureFusion = mergeMertens.process(work_images)
    if filename_type == 'preview':
        print("\nSaving preview image ...\n")
        cv2.imwrite(os.path.join(tmpfolder, 'preview.jpg'), exposureFusion * 255, [int(cv2.IMWRITE_JPEG_QUALITY),
                                                                                   int(sg.user_settings_get_entry(
                                                                                       '_jpgCompression_',
                                                                                       '90'))])  # * 255 to get an 8-bit image
    else:
        print("\nSaving finale fused image ...\n", str(filename_type), "\n")
        cv2_image = exposureFusion * 255
        file_functions.save_file(str(filename_type), cv2_image)
        # cv2.imwrite(str(filename_type), exposureFusion * 255, [int(cv2.IMWRITE_JPEG_QUALITY), int(sg.user_settings_get_entry('_jpgCompression_', '90'))]) # * 255 to get an 8-bit image; jpg_quality=(int)quality?


# Mostly copied from https://learnopencv.com/exposure-fusion-using-opencv-cpp-python/
def opencv_exposure_fuse(all_values, images, tmpfolder, filename_type):
    """
    This function uses the opencv options to exposure fuse the images
    the images are either the resized images for the preview, or the full images for the final result

    :param all_values:      This is the dictionary containing all UI key variables
    :type all_values:       (Dict[Any, Any]) - {Element_key : value}
    :param images:          The images to (optionally) align and fuse
    :type images:           (list)
    :param tmpfolder:       The dynamically create work folder in the OS temp folder
    :type tmpfolder:        (str)
    :param filename_type:   Either the real final filename or a string 'preview'
    :type filename_type:    (str)
    """
    work_images = []
    processed_images = None
    # processed_work_images = []
    for image in images:
        im = cv2.imread(image)
        work_images.append(im)

    print("\nMerging using Exposure Fusion ...\n")
    mergeMertens = cv2.createMergeMertens()
    mergeMertens.setContrastWeight(all_values['_contrast_weight_'])
    mergeMertens.setExposureWeight(all_values['_exposure_weight_'])
    mergeMertens.setSaturationWeight(all_values['_saturation_weight_'])
    exposureFusion = mergeMertens.process(work_images)
    if filename_type == 'preview':
        print("\nSaving preview image ...\n")
        cv2.imwrite(os.path.join(tmpfolder, 'preview.jpg'), exposureFusion * 255, [int(cv2.IMWRITE_JPEG_QUALITY),
                                                                                   int(sg.user_settings_get_entry(
                                                                                       '_jpgCompression_',
                                                                                       '90'))])  # * 255 to get an 8-bit image
    else:
        print("\nSaving finale fused image ...\n")
        cv2_image = exposureFusion * 255
        file_functions.save_file(str(filename_type), cv2_image)


def opencv_align_and_noise_reduction(images, folder, fileName, values, tmpfolder):
    """
    This code is copied from: https://github.com/maitek/image_stacking
    Only some merging of code and minor changes were applied

    :param images:      The images to align and reduce noise off
    :type images:       (list)
    :param folder:      folder that contains original images
    :type folder:       (str)
    :param fileName:    filename that user gives to final image when stacking
    :type fileName:     (str)
    :param values:      This is the dictionary containing all UI key variables
    :type values:       (Dict[Any, Any]) - {Element_key : value}
    :param tmpfolder:   The dynamically created work folder in the OS temp folder
    :type tmpfolder:    (str)
    """
    strBefore = '\nimage before aligning: '
    strAfter = '\nimage after aligning: '
    aligned_images = []

    if values['_radio_ecc_']:  # ECC => Enhanced Correlation Coefficient
        warp_mode = ''
        print('\n\nAligning images using ECC via\n\n')

        first_image = None
        stacked_image = None

        for image in images:
            tmpfilename = os.path.basename(image)
            basename, ext = os.path.splitext(tmpfilename)
            print(strBefore, image)
            image = cv2.imread(image, 1).astype(np.float32) / 255
            print(image)

            if first_image is None:
                # convert to gray scale floating point image
                first_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                stacked_image = image
                if tmpfolder != '':
                    # newFile = os.path.join(tmpfolder, basename + '.png')
                    newFile = os.path.join(tmpfolder, basename + '.ppm')  # Should be 3x faster than png
                    aligned_images.append(newFile)
                    print(strAfter, newFile)
                    newImage = (image * 255).astype(np.uint8)
                    cv2.imwrite(str(newFile), newImage)
            else:
                # Estimate perspective transform
                if values['_homography_']:
                    warp_matrix = np.eye(3, 3, dtype=np.float32)  # cv2.MOTION_HOMOGRAPHY
                    s, warp_matrix = cv2.findTransformECC(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), first_image,
                                                          warp_matrix, cv2.MOTION_HOMOGRAPHY)
                else:
                    warp_matrix = np.eye(2, 3, dtype=np.float32)  # all other warp modes
                    if values['_affine_']:
                        warp_mode = cv2.MOTION_AFFINE
                    elif values['_euclidean_']:
                        warp_mode = cv2.MOTION_EUCLIDEAN
                    elif values['_translation_']:
                        warp_mode = cv2.MOTION_TRANSLATION
                    # Start using Criteria parameter, specifying the termination criteria of the ECC algorithm;
                    # Criteria.epsilon defines the threshold of the increment in the correlation coefficient between two iterations
                    # (a negative Criteria.epsilon makes Criteria.maxcount the only termination criterion).
                    # Default values are: struct('type','Count+EPS', 'maxCount',50, 'epsilon',0.001)
                    number_of_iterations = 5000
                    termination_eps = 1e-10;
                    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations, termination_eps)
                    # specify criteria as last parameter in the cv2.findTransformECC
                    # like cv2.findTransformECC(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), first_image, warp_matrix, warp_mode, criteria )
                    s, warp_matrix = cv2.findTransformECC(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), first_image,
                                                          warp_matrix, warp_mode, criteria)
                    # s, warp_matrix = cv2.findTransformECC(cv2.cvtColor(image, cv2.COLOR_BGR2GRAY), first_image, warp_matrix, warp_mode,)
                w, h, _ = image.shape

                # Align image to first image
                if values['_homography_']:
                    image = cv2.warpPerspective(image, warp_matrix, (h, w))  # HOMOGRAPHY
                else:
                    image = cv2.warpAffine(image, warp_matrix,
                                           (h, w))  # Use warpAffine for Translation, Euclidean and Affine
                stacked_image += image
                if tmpfolder != '':
                    # newFile = os.path.join(tmpfolder, basename + '.png')
                    newFile = os.path.join(tmpfolder, basename + '.ppm')  # Should be 3x faster than png
                    aligned_images.append(newFile)
                    print(strAfter, newFile)
                    newImage = (image * 255).astype(np.uint8)
                    cv2.imwrite(str(newFile), newImage)
        if folder != '' and fileName != '':
            stacked_image /= len(images)
            stacked_image = (stacked_image * 255).astype(np.uint8)
            file_functions.save_file(str(os.path.join(folder, fileName)), stacked_image)

        return aligned_images

    else:  # We use the ORB method => Images KeyPoint matching
        print('\n\nDoing keypoint detection using ORB\n\n')
        orb = cv2.ORB_create()

        # disable OpenCL to because of bug in ORB in OpenCV 3.1
        cv2.ocl.setUseOpenCL(False)

        stacked_image = None
        first_image = None
        first_kp = None
        first_des = None
        for image in images:
            tmpfilename = os.path.basename(image)
            basename, ext = os.path.splitext(tmpfilename)
            print(strBefore, image)
            image = cv2.imread(image, 1)
            imageF = image.astype(np.float32) / 255
            print(imageF)

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
                if tmpfolder != '':
                    # newFile = os.path.join(tmpfolder, basename + '.png')
                    newFile = os.path.join(tmpfolder, basename + '.ppm')  # Should be 3x faster than png
                    aligned_images.append(newFile)
                    print(strAfter, newFile)
                    newImage = (imageF * 255).astype(np.uint8)
                    cv2.imwrite(str(newFile), newImage)
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
                if tmpfolder != '':
                    # newFile = os.path.join(tmpfolder, basename + '.png')
                    newFile = os.path.join(tmpfolder, basename + '.ppm')  # Should be 3x faster than png
                    aligned_images.append(newFile)
                    print(strAfter, newFile)
                    newImage = (imageF * 255).astype(np.uint8)
                    cv2.imwrite(str(newFile), newImage)

        if folder != '' and fileName != '':
            stacked_image /= len(images)
            stacked_image = (stacked_image * 255).astype(np.uint8)
            file_functions.save_file(str(os.path.join(folder, fileName)), stacked_image)

        return aligned_images


'''
    elif values['_radio_alignmtb_']:
        work_images = []
        new_image = None
        alignMTB = cv2.createAlignMTB()
        for image in images:
            if new_image is None:
                new_image = image
            im = cv2.imread(image)
            work_images.append(im)
        alignMTB.process(work_images, work_images)
        mergeExposures = cv2.MergeExposures()
        mergeExposures.process(work_images)
        new_image /= len(work_images)
        new_image = (new_image * 255).astype(np.uint8)
        file_functions.save_file(str(os.path.join(folder, fileName)), new_image)
'''