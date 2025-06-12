import ansats1Functions
import os
import cv2
from scipy import ndimage
from collections import defaultdict

#   Path to the folder with subfolders with pictures to be analyzed
parentFolder = "/home/dennipl/Documents/project/tagna_bilder/Bildinsamling4/Bildinsamling4Kameramodul1"

#   Path to the textfile which will be created to store results
resultFile = os.path.join(parentFolder, "tiltPercentageMeasurements.txt")

#   Path to the textfile which will be created to store tiltAngle and tiltPercentage
tiltOuterFile = os.path.join(parentFolder, "outerTiltAndtiltPercentage.txt")
tiltInnerFile = os.path.join(parentFolder, "innerTiltAndtiltPercentage.txt")

#   2 dictionaries for storing the outer and inner pictures tiltAngle 
#   paired with the calculated tiltPercentage
tiltOuterValues = defaultdict(list)
tiltInnerValues = defaultdict(list)

#   2 for-loops to walk through all the subfolders and access each picture from camera 1
for root, subfolder, files in os.walk(parentFolder):
    if root == parentFolder:
        continue

    for filename in files:

        #   Check if it's an image file
        if not filename.endswith(('.jpg', '.jpeg', '.png')):
            continue  #    Skip non-image files

        #   Path to picture
        imagepath = os.path.join(root, filename)
        
        #   Get the image roll and tilt from it's filename
        print(filename)
        roll = ansats1Functions.rollFromImageName(filename)
        tilt = round(float(ansats1Functions.tiltFromImageName(filename)))


        #   Calculates the rollangle of the picture
        calculatedRoll, totalAngle, filledImage, orientation = ansats1Functions.measureRollangle(imagepath)

        #   Rotates picture with totalAngle. Is used to calculate tiltPercentage
        checkTiltImage = ndimage.rotate(filledImage, totalAngle, cval=255, reshape = False)

        #   Calculates how many percent the fixture edge covers the picture
        calculatedTiltPercent = ansats1Functions.checkTilt(checkTiltImage)
        
        if calculatedTiltPercent != "undefined":
            if orientation == "outerPicture":
                tiltOuterValues[tilt].append(round(calculatedTiltPercent, 2))
            elif orientation == "innerPicture":
                tiltInnerValues[tilt].append(round(calculatedTiltPercent, 2))
            
            #   Writes the calculated roll and tilt to a textfile togehter with filname, orientation, and roll and tilt derived from filenamne
        ansats1Functions.writeToFileResultStep1(resultFile, filename, orientation, roll, tilt, calculatedRoll, calculatedTiltPercent)

#   For all colected tiltValues the mean value of its tiltPercentages is calculated and stored in a textfile
#   One textfile for outerpictures
tiltOuterMeanValues = {}
for tilt in tiltOuterValues:
    values = tiltOuterValues[tilt]
    meanValue = sum(float(v) for v in values) / len(values)
    tiltOuterMeanValues[tilt] = meanValue

for tilt in sorted(tiltOuterMeanValues):
    ansats1Functions.writeToFileTilt(tiltOuterFile, tilt, tiltOuterMeanValues[tilt])

#   And another textfile for innerpictures
tiltInnerMeanValues = {}
for tilt in tiltInnerValues:
    values = tiltInnerValues[tilt]
    meanValue = sum(float(v) for v in values) / len(values)
    tiltInnerMeanValues[tilt] = meanValue

for tilt in sorted(tiltInnerMeanValues):
    ansats1Functions.writeToFileTilt(tiltInnerFile, tilt, tiltInnerMeanValues[tilt])




