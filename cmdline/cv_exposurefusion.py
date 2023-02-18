#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import the necessary packages
import numpy as np
import argparse
import imutils
import cv2
import os
import glob
from time import time
from PIL import Image
from PIL.ExifTags import TAGS

#########
# For focusstacking see/use https://github.com/momonala/focus-stack
#########

DEBUG = False

def get_exif_field (exif,field) :
  for (k,v) in exif.items():
     if TAGS.get(k) == field:
        return v

def get_xmp_field(img_file, field):
    with open( img_file, "rb") as fin:
        img = fin.read()
        imgAsString=str(img)
        xmp_start = imgAsString.find('<x:xmpmeta')
        xmp_end = imgAsString.find('</x:xmpmeta')
        if xmp_start != xmp_end:
            xmpString = imgAsString[xmp_start:xmp_end+12]
        tags = xmpString.split("\\n  ")
        for tag in tags:
            if "ExposureBiasValue" in tag:
                substr = tag.replace("<exif:ExposureBiasValue>", "").replace("</exif:ExposureBiasValue>", "")
                subtag = substr.split("/")
                #print(subtag[0])
                return(subtag[0])


def ORB_align_images(image, template, maxFeatures=5000, keepPercent=0.02, debug=False):
	# convert both the input image and template to grayscale
	imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
	# use ORB to detect keypoints and extract (binary) local
	# invariant features
	orb = cv2.ORB_create(maxFeatures)
	(kpsA, descsA) = orb.detectAndCompute(imageGray, None)
	(kpsB, descsB) = orb.detectAndCompute(templateGray, None)
	# match the features
	method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
	matcher = cv2.DescriptorMatcher_create(method)
	matches = matcher.match(descsA, descsB, None)
	# sort the matches by their distance (the smaller the distance,
	# the "more similar" the features are)
	matches = sorted(matches, key=lambda x:x.distance)
	# keep only the top matches
	keep = int(len(matches) * keepPercent)
	matches = matches[:keep]
	# check to see if we should visualize the matched keypoints
	if debug:
		matchedVis = cv2.drawMatches(image, kpsA, template, kpsB,
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
	(H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)
	# use the homography matrix to align the images
	(h, w) = template.shape[:2]
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
def ECC_align_images(image, ref_image, number_of_iterations=500, termination_eps = 1e-10, debug=False):
    # Convert images to grayscale
    ref_image = cv2.cvtColor(ref_image,cv2.COLOR_BGR2GRAY)
    image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
 
    # Find size of image1
    sz = ref_image.shape
 
    # Define the motion model
    #warp_mode = cv2.MOTION_TRANSLATION # shifted compared to other image
    warp_mode = cv2.MOTION_EUCLIDEAN   # rotation and shift (translation)
    #warp_mode = cv2.MOTION_AFFINE       # rotation, shift (translation), scale and shear
    #warp_mode = cv2.MOTION_HOMOGRAPHY    # All above are 2D; This one also accounts for some 3D effects.
 
    # Define 2x3 or 3x3 matrices and initialize the matrix to identity
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        warp_matrix = np.eye(3, 3, dtype=np.float32)
    else :
        warp_matrix = np.eye(2, 3, dtype=np.float32)

 
    # termination_eps is the threshold of the increment
    # in the correlation coefficient between two iterations 
    # Define termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)
 
    # Run the ECC algorithm with the defined warp_mode. The results are stored in warp_matrix.
    (cc, warp_matrix) = cv2.findTransformECC (image,ref_image,warp_matrix, warp_mode, criteria)
 
    if warp_mode == cv2.MOTION_HOMOGRAPHY :
        # Use warpPerspective for Homography
        image_aligned = cv2.warpPerspective (image, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
    else :
        # No longer: Use warpAffine for Translation, Euclidean and Affine
        image_aligned = cv2.warpAffine(image, warp_matrix, (sz[1],sz[0]), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP);
 
    # Show final results
    if debug:
        cv2.imshow("Image 1", ref_image)
        cv2.imshow("Image 2", image)
        cv2.imshow("Aligned Image 2", image_aligned)
        cv2.waitKey(0)

    return image_aligned


def remove_temp_files():
    fileList = glob.glob('/tmp/align*')
    for filePath in fileList:
        try:
            os.remove(filePath)
        except:
            print("Error while deleting file : ", filePath)



# ===== MAIN =====

if __name__ == '__main__':

    # First remove the optional tmp files
    remove_temp_files()
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", required=True,
    	help="name of the fused output file")
    ap.add_argument(
        'img_names', nargs='+',
        help="Files to stitch", type=str)
    ap.add_argument("-m", "--method",
    	help="name of the method to use for keypoint matching: ORB or ECC. ORB is default. ORB is much faster, only use ECC in case of large exposure differences",
        type=str, dest="method")
    ap.add_argument("-mf", "--maxfeatures", default=1500,
        help="Set the maxFeatures parameter for ORB and max_iterations for ECC. The default for ORB is 5000, for ECC 500",
        type=int, dest="maxfeatures")
    ap.add_argument("-cw", "--contrastweight", default=1.0,
        help="Set the contrast weight. The default for opencv is 1.0, for enfuse 0.2",
        type=float, dest="contrastweight")
    ap.add_argument("-ew", "--exposureweight", default=0.0,
        help="Set the exposure weight. The default for opencv is 0.0, for enfuse 1.0",
        type=float, dest="exposureweight")
    ap.add_argument("-sw", "--saturationweight", default=1.0,
        help="Set the saturation weight. The default for opencv is 1.0, for enfuse 0.2",
        type=float, dest="saturationweight")
    args = ap.parse_args()

    # Get the method, if given
    method = args.method
    if args.method is None:
        method = "ORB"
    else:
        method = (args.method).upper()
    maxfeatures = args.maxfeatures

    # Check optional weight parameters
    contrast_weight = args.contrastweight
    saturation_weight = args.saturationweight
    exposure_weight = args.exposureweight
    # load the input image and template from disk
    output = args.output
    print("\n[INFO] output " + output)
    #image = cv2.imread(args["image"])
    img_names = args.img_names
    print("[INFO] input images " + str(img_names))
    teller = 0
    ordered_filenames = []
    tmp_filenames = []
    other_filenames = []
    images = []
    tic = time()
    print("[INFO] loading images...")
    # First find the image with the exposurecompensation (PIL: ExposureBiasValue) == 0 
    for img_file in img_names:
        im = Image.open(img_file)
        exif = im.getexif().get_ifd(0x8769)
        EBV = get_exif_field(exif, 'ExposureBiasValue')
        if EBV is None:
            if DEBUG:
                print("[DEBUG] no exIFD ExposureBiasValue. Switching to xmp")
            EBV = get_xmp_field(img_file, 'ExposureBiasValue')
            if DEBUG:
                print("[DEBUG] xmp exif:ExposureBiasValue image: " + img_file + ": " + EBV)
            #print("xmp EBV " + EBV)
        else:
            if DEBUG:
                print("[DEBUG] exIFD ExposureBiasValue image: " + img_file + ": " + str(EBV))


        if EBV == '0.0' or EBV == '0' or EBV == 0.0 or EBV == 0:
            if DEBUG:
                print("\n")
            ordered_filenames.append(img_file)
        else:
            # Add all other exposure compensations to the other_images
            # In case we do not have an exposure == 0, all will be added to this one. So be it.
            other_filenames.append(img_file)
    ordered_filenames.extend(other_filenames)

    # Now do the loop with the aligning
    for img_file in ordered_filenames:
        if teller == 0:
            global ref_image
            global org_image_name
            org_image_name = img_file
            ref_image_name = "/tmp/aligned_" + img_file
            ref_image = cv2.imread(img_file)
            cv2.imwrite(("/tmp/aligned_" + img_file), ref_image)
            tmp_filenames.append(ref_image_name)
            teller += 1
        else:
            to_be_aligned = cv2.imread(img_file)
            # align the images
            if method == "ORB":
                print("[INFO] align image " + img_file + " against reference image " + ref_image_name + " using ORB.")
                aligned = ORB_align_images(to_be_aligned, ref_image, debug=DEBUG)
            else:
                print("[INFO] align image " + img_file + " against reference image " + ref_image_name + " using ECC")
                aligned = ECC_align_images(to_be_aligned, ref_image, debug=DEBUG)
            myaligned = aligned.astype(np.float32) * 255
            cv2.imwrite(("/tmp/aligned_" + img_file), aligned)
            tmp_filenames.append("/tmp/aligned_" + img_file)
    print(images)

    print("[INFO] Reading aligned images from /tmp for exposure fusion.")
    for filename in tmp_filenames:
        #print("[INFO] Reading aligned image for exposure fusion " + filename)
        im = cv2.imread(filename)
        images.append(im)

    # Merge using Exposure Fusion
    print("\nMerging using Exposure Fusion ... ");
    mergeMertens = cv2.createMergeMertens()
    # get our (optional) parameters
    mergeMertens.setContrastWeight(contrast_weight)
    mergeMertens.setExposureWeight(exposure_weight)
    mergeMertens.setSaturationWeight(saturation_weight)
    exposureFusion = mergeMertens.process(images)

    print("aligned and exposure fused {0} in {1} seconds".format(len(img_names), (time()-tic) ))

    print("Saving {}".format(output))
    # multiply by 255 to create an 8bit image
    cv2.imwrite(output, exposureFusion * 255, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    # Do the necessary exiftool stuff
    os.system("exiftool -overwrite_original -TagsFromFile " + org_image_name + " -all " + output)
    os.system("exiftool -v \"-CreateDate>FileModifyDate\" -overwrite_original " + output)

    if DEBUG:
        cv2.imshow("Fused and aligned image", exposureFusion)
        cv2.waitKey(0)

    # No matter we have chosen debug or not
    cv2.destroyAllWindows()
