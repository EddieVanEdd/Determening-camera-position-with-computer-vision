import ansats1Functions
import os
import cv2
from scipy import ndimage
from collections import defaultdict

#   Path to the folder with subfolders with pictures to be analyzed
tiltLookUpTableFolder = "/home/dennipl/Documents/project/tagna_bilder/Bildinsamling4/Bildinsamling4Kameramodul1"
imagesFolder = "/home/dennipl/Downloads/bildinsamlingOrigianlKamera15april"
tiltOuterFile = os.path.join(tiltLookUpTableFolder, "outerTiltAndtiltPercentage.txt")
tiltInnerFile = os.path.join(tiltLookUpTableFolder, "innerTiltAndtiltPercentage.txt")

resultFile = os.path.join(tiltLookUpTableFolder, "tiltAndRollMeasurementsKamermodulOriginalKamera15April.txt" ) #"tiltAndRollMeasurementsKamermodul2AllaKameror.txt"

#   Get the values for the tiltLookUpTables and store them in 2 dictionaries
tiltOuterValues = defaultdict(list)
tiltInnerValues = defaultdict(list)

with open (tiltOuterFile, "r") as file:
    #Exempelline Tilt: -141, CalculatedTilt%: 97.488
    
    for line in file:
        
        stringAfterTilt = line.split("Tilt: ")[1]
        tilt = round(float(stringAfterTilt.split(", CalculatedTilt%")[0]))
        calculatedMeanTilt = float(line.split(", CalculatedTilt%: ")[1])

        tiltOuterValues[tilt] = calculatedMeanTilt

with open (tiltInnerFile, "r") as file:
    #Exempelline 
    
    for line in file:
        
        stringAfterTilt = line.split("Tilt: ")[1]
        tilt = round(float(stringAfterTilt.split(", CalculatedTilt%")[0]))
        calculatedMeanTilt = float(line.split(", CalculatedTilt%: ")[1])

        tiltInnerValues[tilt] = calculatedMeanTilt

#   Analyzes the pictures in the imagesFoldes and stores the result i a textfile
rollDifferenceValues = []
tiltDifferenceValues = []

for root, subfolder, files in os.walk(imagesFolder):
    if root == imagesFolder:
        continue

    for filename in files:

        #   Check if it's an image file
        if not filename.endswith(('.jpg', '.jpeg', '.png')):
            continue  #    Skip non-image files
        
        print(filename)

        #   Path to picture
        imagepath = os.path.join(root, filename)

        #   Get the image roll and tilt from it's filename
        roll = round(float(ansats1Functions.rollFromImageName(filename)), 3)
        tilt = round(float(ansats1Functions.tiltFromImageName(filename)))
       
        #   Calculates the rollangle of the picture
        calculatedRoll, totalAngle, filledImage, orientation = ansats1Functions.measureRollangle(imagepath)
        
        if orientation == "undefined" or calculatedRoll == "undefined":
            ansats1Functions.writeToFileResultStep2(resultFile, filename, orientation, roll, tilt, calculatedRoll, "undefined", "undefined", "undefined")
            continue
        
        #   Rotates picture with totalAngle. Is used to calculate tilt
        checkTiltImage = ndimage.rotate(filledImage, totalAngle, cval=255, reshape = False)
        checkTiltImageSmall = image = cv2.resize(checkTiltImage,(720,480)) 
 
        #   Calculates how many percent the fixture edge covers the picture
        calculatedTiltPercent = ansats1Functions.checkTilt(checkTiltImage)
        
        #   Handles pictures where values are undefined
        calculatedTilt = None
        if calculatedTiltPercent == "undefined":
            calculatedTilt = "undefined"
            calculatedRoll = "undefined"
        elif orientation == "outerPicture":
            calculatedTilt = ansats1Functions.closestTilt(tiltOuterValues, calculatedTiltPercent)
        elif orientation == "innerPicture":
            calculatedTilt = ansats1Functions.closestTilt(tiltInnerValues, calculatedTiltPercent)

        if calculatedTilt == "undefined":
            ansats1Functions.writeToFileResultStep2(resultFile, filename, orientation, roll, tilt, "undefined", calculatedTilt, "undefined", "undefined")
            continue
        
        #   Calculates the roll and tiltdifferences and writes the results to a textfile
        rollDifference = round(abs(calculatedRoll - roll), 3)

        rollDifferenceValues.append(rollDifference)

        tiltDifference = abs(calculatedTilt - tilt)
        
        tiltDifferenceValues.append(tiltDifference)

        print("roll: ", roll, "calculatedRoll: ", calculatedRoll, "difference: ", rollDifference)
        print("tilt: ", tilt, "calculatedTilt: ", calculatedTilt, "difference: ", tiltDifference)
        ansats1Functions.writeToFileResultStep2(resultFile, filename, orientation, roll, tilt, calculatedRoll, calculatedTilt, rollDifference, tiltDifference)
