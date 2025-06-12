import os 
import cv2 
import numpy as np
from scipy import ndimage
from scipy import optimize

#   Extracts the roll value from the picture filename. Exemple name: Id_0Nr_1P_0.0T_-14.0R_5.03.jpg
#   Id is the camera Id which is 0-3. Nr is serial number. T is tilt angle and R is roll angle.
def rollFromImageName(filename):
    afterR_ = filename.split("R_")[1]
    roll = afterR_.split(".jpg")[0]
    return roll

#   As above but extracts the tilt value from the picture filename.
def tiltFromImageName(filename):
    afterT_ = filename.split("T_")[1]
    tilt = afterT_.split("R_")[0]
    return tilt

#   Takes an image and returns its calculatedRoll, totalAngle, filledImage and orientation
def measureRollangle(imagepath):
    #   OpenCV imread-function reads and image and returns a pixelmatrix. Hear as a grayscale with only one grayscalematrix
    image = cv2.imread(imagepath, cv2.IMREAD_GRAYSCALE) 

    #   Blur the picture with a 7x7 kernel with the OpenCV-function GaussianBlur
    blurredImage = cv2.GaussianBlur(image, (7,7), 0)

    #   Otsu threshold of image with OpenCV threshold-function.
    _, otsuImage = cv2.threshold(blurredImage, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    #   Fills the white spots in the image except the biggest one above the camera fixture edge
    filledImage = fillWhiteSpots(otsuImage)

    #   Shows the picture orientation. If it's a picture of the inside fixture edge or the outside fixture edge
    orientation = innerOrOuterPicture(filledImage)
    
    #   If it is a picture of the outside fixture edge it has to be rotated 180 degrees. Then the the fixture edge 
    #   is situated in the lower edge of the picture
    addAngle = 0
    if orientation == "innerPicture":
        rotated = filledImage
    elif orientation == "outerPicture":
        rotated = ndimage.rotate(filledImage, 180, cval=255, reshape = False)
        addAngle = 180
    elif orientation == "undefined":
        #   If the orientation is undefined it saves the results of calculated roll and tilt as undefined
        return "undefined", "undefined", "undefined", "undefined"

    maskedImage = maskCircle(rotated)

    #   Calculates the rollangle of the picture
    calculatedRoll = round(rotateToHorizontal(maskedImage),2)

    #   Calculates the angle of rotation of the picture. For pictures of the inner fixture edge it is the same as calculated
    #   but for pictures of the outer fixture edge it has to add additional 180 degress
    totalAngle = calculatedRoll + addAngle

    return calculatedRoll, totalAngle, filledImage, orientation

#   Fills all the whitespots in the image exepct the biggest one that is the area above the camera fixture edge
def fillWhiteSpots(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask =  np.zeros_like(image)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    cv2.drawContours(mask, [contours[0]], -1, 255, thickness=cv2.FILLED)
    #cv2.imwrite(os.path.join("/home/dennipl/Documents/project/tagna_bilder/Bildinsamling/rapport", f"drawContours_{variable}.jpg"), mask)
    #cv2.imwrite(os.path.join(parentFolder, f"drawContours_{filename}"), mask)
    result = cv2.bitwise_and(image, mask)
    return result

#   Determines if the picture is of the outer or inner camera fixture edge
def innerOrOuterPicture(image):
    height = image.shape[0]
    width = image.shape[1]
    _, Otsu = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    quadrant_percentages = [
        ("leftUpper", blackPixelPercentage(Otsu[:height//2, :width//2])),
        ("rightUpper", blackPixelPercentage(Otsu[:height//2, width//2:])),
        ("leftLower", blackPixelPercentage(Otsu[height//2:, :width//2])),
        ("rightLower", blackPixelPercentage(Otsu[height//2:, width//2:]))
    ]

    quadrant_percentages.sort(key = lambda item : item[1], reverse = True)
    topOneName, topOnePercentage  = quadrant_percentages[0]
    topTwoName, topTwoPercentage = quadrant_percentages[1]

    state = "undefined"
    if (topOneName == "leftUpper" or
        (topOneName == "leftUpper" and topTwoName == "rightUpper") or
        (topOneName == "rightUpper" and topTwoName == "leftUpper") or
        (topOneName == "leftUpper" and topTwoName == "leftLower") or
        (topOneName == "leftLower" and topTwoName == "leftUpper")):
        state = "outerPicture"
    elif(topOneName == "leftLower" or
        (topOneName == "leftLower" and topTwoName == "rightLower") or 
        (topOneName == "rightLower" and topTwoName == "leftLower") or
        (topOneName == "rightUpper" and topTwoName == "rightLower") or
        (topOneName == "rightLower" and topTwoName == "rightUpper")):
        state   = "innerPicture"

    return state

#   Helpfunction that determines the percentage black pixels in an image
def blackPixelPercentage(image):
    whitePixels = cv2.countNonZero(image)
    blackPixels = image.size - whitePixels
    percentage = 100*(blackPixels/image.size)
    return percentage

#   Maskes out a circlecut of the image around its center
def maskCircle(image):
    height = image.shape[0]
    width = image.shape[1]
    halfHeight = height//2
    halfWidth = width//2
    radius = min(halfHeight, halfWidth)
    mask = np.zeros_like(image)
    cv2.circle(mask, (halfWidth, halfHeight), radius, 255, -1)
    maskInverted = cv2.bitwise_not(mask)
    maskedImageWhiteEdge = cv2.bitwise_or(maskInverted, image)

    return maskedImageWhiteEdge

#   Rotates the image until the cameras fixture edge is horisontal. Returns the angle it has to rotate
def rotateToHorizontal(image):
    # 5 degree steps
    lowLimit = -100
    highLimit = 10
    stepSize = 5
    angle = rotateToHorizontalChosenInterval(image, lowLimit, highLimit, stepSize)
    # 1 degree steps
    lowLimit = angle - 5
    highLimit = angle + 5
    stepSize = 1
    angle = rotateToHorizontalChosenInterval(image, lowLimit, highLimit, stepSize)
    # .1 degree steps
    lowLimit = angle - 1
    highLimit = angle + 1
    stepSize = 0.1
    angle = rotateToHorizontalChosenInterval(image, lowLimit, highLimit, stepSize)

    return round(angle,2)

#   Takes an image as an input and rotates it from lowLimit degrees to higLimit degrees with
#   stepSize degrees between. Returns the angle when the picture has the most horizontal 
#   camera fixture edge

def rotateToHorizontalChosenInterval(image, lowLimit, highLimit, stepSize):
    differenceLeftRight = []
    i = lowLimit
    while i <= highLimit:
        rotated = ndimage.rotate(image, i, cval=255, reshape = False)
        differenceLeftRight.append((i, getDifferenceCircle(rotated)))
        i += stepSize
    differenceLeftRight.sort(key = lambda item : item[1])
    angle = differenceLeftRight[0][0]
    #print(angle)
    return angle

def getDifferenceCircle(image):
        left, right = blackPixelPercentInCircle(image)
        if left == 0 or right == 0:
            return 100
        return abs(left - right)

#   Returns the black percentage of the left and right half of the circle if 
#   it is divied in verticaly in the middle 

def blackPixelPercentInCircle(image):
    height = image.shape[0]
    width = image.shape[1]
    halfHeight = height//2
    halfWidth = width//2
    leftImage = image[halfHeight:, :halfWidth]
    rightImage = image[halfHeight:, halfWidth:]
    leftPercentage = blackPixelPercentage(leftImage)
    rightPercentage = blackPixelPercentage(rightImage)
  
    return leftPercentage, rightPercentage

#   This function returns the distance from the center to the first black pixel 
#   in a straight vertical line going down from the center, expressed as a percentage 
#   of the image height
def checkTilt(image):
    
    maxImageHeight = image.shape[0]-1
    halfImagewidth = (image.shape[1]-1)//2
    halfImageHeight = image.shape[0]//2
    height = halfImageHeight
    while height <= maxImageHeight:
        color = image[height, halfImagewidth]
        if color == 0:
            return round(100 * (height - halfImageHeight)/(halfImageHeight), 2)
        height += 1

    return "undefined"

#   Function to write results to a textfile
def writeToFileResultStep1(result_file, filename, orientation, roll, tilt, calculatedRoll, calculatedTilt):
    with open (result_file, "a") as file:
            file.write(f"Imagename: {filename}, ")
            file.write(f"Imageorientation: {orientation}, ")
            file.write(f"Roll: {roll}, ")
            file.write(f"Tilt: {tilt}, ")
            file.write(f"CalculatedRoll: {calculatedRoll}, ")
            file.write(f"CalculatedTilt%: {calculatedTilt}\n")

#   Function to write results to a textfile
def writeToFileResultStep2(result_file, filename, orientation, roll, tilt, calculatedRoll, calculatedTilt, rollDifference, tiltDifference):
    with open (result_file, "a") as file:
            file.write(f"Imagename: {filename}, ")
            file.write(f"Imageorientation: {orientation}, ")
            file.write(f"Roll: {roll}, ")
            file.write(f"CalculatedRoll: {calculatedRoll}, ")
            file.write(f"Tilt: {tilt}, ")
            file.write(f"CalculatedTilt: {calculatedTilt},")
            file.write(f"rollDifference: {rollDifference}, ")
            file.write(f"tiltDifference: {tiltDifference}\n")

#   Function to write results to a textfile
def writeToFileTilt(result_file, tilt, meanTilt):
    with open (result_file, "a") as file:
            file.write(f"Tilt: {tilt}, ")
            file.write(f"CalculatedTilt%: {meanTilt}\n")

#   Determines which tiltAveragePercentagevalue is the closest to the tiltPercentagevalue.
#   Returns the tiltValue of the closest tiltAveragePercentagevalue
def closestTilt(tiltValues, calculatedTiltPercent):
    minDif = 100
    minDifTilt = None
    for tilt in tiltValues:
        compareDif = abs(calculatedTiltPercent-tiltValues[tilt])
        if compareDif < minDif:
            minDif = compareDif
            minDifTilt = tilt
    return minDifTilt
            
#######################################################################
###   Improvement for rotateToHorizontal that didnt work completly  ###
#######################################################################
def rotateToHorizontalFast(image):
    def objective(angle):
        rotated = ndimage.rotate(image, angle, cval=255, reshape=False)
        return getDifferenceCircle(rotated)

    result = optimize.minimize_scalar(objective, bounds=(-360, 360), method='bounded',#test bounds=(-270, 0), #bounds=(-180, 180) Klarar ej -90 och -95 ibland original: bounds=(-110, 10)
        options={'xatol': 0.01})
    best_angle = result.x
    return best_angle
