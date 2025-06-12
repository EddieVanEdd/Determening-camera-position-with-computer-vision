import cv2
import numpy as np
import cameraControl
import time
import os

#   Returns the x, y coordinates of green target
def getCoordinatesForGreenTarget(image):
  
# Konvertera till HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Grön mask
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Morfologisk filtrering (för att ta bort småprickar)
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Fyll små hål

    # Analysera komponenter
    num_labels, labels, stats, centroid = cv2.connectedComponentsWithStats(mask, connectivity=8)

    # Hämta koordinater för största komponentens centroid
    centroidx = round(centroid[1][0])
    centroidy = round(centroid[1][1])
    return centroidx, centroidy

#   Returns the x, y coordinates of red target
def getCoordinatesForRedTarget(image):

    # Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Create mask
    lower_red1 = np.array([0, 120, 50])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 120, 50])
    upper_red2 = np.array([180, 255, 255])

    # Create two masks 
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # combine masks
    mask = cv2.bitwise_or(mask1, mask2)

    # Opening followed by closing to get rid of white and black noise
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Get centroid coordinates
    analysis = cv2.connectedComponentsWithStats(mask , 8, cv2.CV_32S)
    (_, _, _, centroid) = analysis
    centroidx = round(centroid[1][0])
    centroidy = round(centroid[1][1])
    
    # Get coordinates
    return centroidx, centroidy

#   Centers the camera on the green target in pan
def panCenter(image, cameraId, dirPath, filename):
    centerX = (image.shape[1]//2)
    x, _ = getCoordinatesForGreenTarget(image)
    variable = "pan"
    sleeptime = 0.5
    smallStepLimit = round(0.04*centerX)
    accumulatedPan = 0
    if cameraId == 3:
        accumulatedPan = 360

    # Right is positive steps
    if centerX < x:
        print("Moving right")
        stepsize = 1
        while centerX < x:
            xDifference = abs(x-centerX)
            if xDifference < smallStepLimit:
                stepsize = 0.1  
            cameraControl.rollOrTiltOrPanOneDirection(cameraId, variable, stepsize, sleeptime)
            image = cameraControl.takePicture(cameraId, dirPath, filename)
            time.sleep(0.5)
            x, _ = getCoordinatesForGreenTarget(image)
            xDifference = abs(x-centerX)
            accumulatedPan += stepsize
            print("xDifference: ",xDifference)
        image = cameraControl.takePicture(cameraId, dirPath, filename)
        time.sleep(0.5)
        x, _ = getCoordinatesForGreenTarget(image)
        xDifference = abs(x-centerX)
        return accumulatedPan, xDifference

    # Left is negative steps
    elif centerX > x:
        print("Moving left")
        stepsize = -1
        while centerX > x:
            xDifference = abs(x-centerX)
            if xDifference < smallStepLimit:
                stepsize = -0.1
            cameraControl.rollOrTiltOrPanOneDirection(cameraId, variable, stepsize, sleeptime)
            image = cameraControl.takePicture(cameraId, dirPath, filename)
            time.sleep(0.5)
            x, _ = getCoordinatesForGreenTarget(image)
            xDifference = abs(x-centerX)
            accumulatedPan += stepsize
            print("xDifference: ",xDifference)
        image = cameraControl.takePicture(cameraId, dirPath, filename)
        time.sleep(0.5)
        x, _ = getCoordinatesForGreenTarget(image)
        xDifference = abs(x-centerX)
        return accumulatedPan, xDifference
    
    elif centerX == x:
        return 0, 0

#   Centers the camera on the green target in tilt
def tiltCenter(image, cameraId, dirPath, filename):
    centerY = (image.shape[0]//2)
    _, y = getCoordinatesForGreenTarget(image)
    variable = "tilt"
    sleeptime = 0.5
    smallStepLimit = round(0.05*centerY)
    accumulatedTilt = 0

    #Moving down is negative steps
    if centerY < y:
        print("Moving down")
        stepsize = -1
        while centerY < y :
            yDifference = abs(y-centerY)
            if yDifference < smallStepLimit:
                stepsize = -0.1  
            cameraControl.rollOrTiltOrPanOneDirection(cameraId, variable, stepsize, sleeptime)
            image = cameraControl.takePicture(cameraId, dirPath, filename)
            time.sleep(0.5)
            _, y = getCoordinatesForGreenTarget(image)
            yDifference = abs(y-centerY)
            accumulatedTilt += stepsize
            print("yDifference: ",yDifference)
        image = cameraControl.takePicture(cameraId, dirPath, filename)
        time.sleep(0.5)
        _, y = getCoordinatesForGreenTarget(image)
        yDifference = abs(y-centerY)
        return accumulatedTilt, yDifference

    
    #Moving up is positive steps
    elif centerY > y:
        print("Moving up")
        stepsize = 1
        while centerY > y:
            yDifference = abs(y-centerY)
            if yDifference < smallStepLimit:
                stepsize = 0.1
            cameraControl.rollOrTiltOrPanOneDirection(cameraId, variable, stepsize, sleeptime)
            image = cameraControl.takePicture(cameraId, dirPath, filename)
            time.sleep(0.5)
            _, y = getCoordinatesForGreenTarget(image)
            yDifference = abs(y-centerY)
            accumulatedTilt += stepsize
            print("yDifference: ",yDifference)
        image = cameraControl.takePicture(cameraId, dirPath, filename)
        time.sleep(0.5)
        _, y = getCoordinatesForGreenTarget(image)
        yDifference = abs(y-centerY)
        tilt = cameraControl.getStatusCameraPanOrTiltOrRoll(cameraId, "tilt")
        return accumulatedTilt, yDifference
    
    elif centerY == y:
        return 0, 0
    


#   Rolls the camera untill the red and green target are horizontal
def tiltRoll(image, cameraId, dirPath, filename):
    centerY = (image.shape[0]//2)
    _, yRed = getCoordinatesForRedTarget(image)
    variable = "roll"
    sleeptime = 0.5
    smallStepLimit = round(0.01*centerY)
    accumulatedRoll = 0
   
    # Clockwise is positive rotation
    if yRed < centerY:  
        print("Rotating clockwise")
        stepsize = 1
        while yRed < centerY:
            yDifference = abs(yRed-centerY)
            if yDifference < smallStepLimit:
                stepsize = 0.1
            cameraControl.rollOrTiltOrPanOneDirection(cameraId, variable, stepsize, sleeptime)
            image = cameraControl.takePicture(cameraId, dirPath, filename)
            time.sleep(0.5)
            _, yRed = getCoordinatesForRedTarget(image)
            yDifference = abs(yRed-centerY)
            accumulatedRoll += stepsize
            print("yDifference: ",yDifference)
        image = cameraControl.takePicture(cameraId, dirPath, filename)
        time.sleep(0.5)
        _, yRed = getCoordinatesForRedTarget(image)
        yDifference = abs(yRed-centerY)
        return accumulatedRoll, yDifference

    # Anticlockwise is negative rotation
    elif yRed > centerY:
        print("Rotating anticlockwise")
        stepsize = -1
        while yRed > centerY:
            yDifference = abs(yRed-centerY)
            if yDifference < smallStepLimit:
                stepsize = -0.1
            cameraControl.rollOrTiltOrPanOneDirection(cameraId, variable, stepsize, sleeptime)
            image = cameraControl.takePicture(cameraId, dirPath, filename)
            time.sleep(0.5)
            _, yRed = getCoordinatesForRedTarget(image)
            yDifference = abs(yRed-centerY)
            accumulatedRoll += stepsize
            print("yDifference: ",yDifference)
        image = cameraControl.takePicture(cameraId, dirPath, filename)
        time.sleep(0.5)
        _, yRed = getCoordinatesForRedTarget(image)
        yDifference = abs(yRed-centerY)
        return accumulatedRoll, yDifference
    
    elif yRed == centerY:
        return 0, 0

#   Moves the camera to ptr: 0, -16, 0 then it takes pictures of the target, 
#   tries to center it in the picture and make horizontal 
def centering(cameraId, dirPath):
    pan = 0
    tilt = -16
    roll = 0
    if cameraId == 3:
        pan = 360
    cameraControl.updateSetPosition(cameraId, pan, tilt, roll)
    time.sleep(1)
    acculumatedPan = 0
    accumulatedTilt = 0
    accumulatedRoll = 0

    filename = f"startbildCamera{cameraId}"
    image = cameraControl.takePicture(cameraId, dirPath, filename)
    centerX = (image.shape[1]//2)
    centerY = (image.shape[0]//2)
    image = cv2.circle(image, (centerX, centerY), radius=10, color=(0, 0, 255), thickness=-1)
    cv2.imwrite(os.path.join(dirPath, filename + "MarkeratCentrum.jpg"), image)
    
    filename = f"startbildPanCamera{cameraId}"
    image = cameraControl.takePicture(cameraId, dirPath, filename)
    addPan, _ = panCenter(image, cameraId, dirPath, filename)
    acculumatedPan += addPan 

    filename = f"startbildTiltCamera{cameraId}"
    image = cameraControl.takePicture(cameraId, dirPath, filename)
    addTilt, _ = tiltCenter(image, cameraId, dirPath, filename)
    accumulatedTilt += addTilt

    rollAngleFromFirstImage = rollAngleFromStillImage(cameraId, dirPath)

    filename = f"startbildRollCamera{cameraId}"
    image = cameraControl.takePicture(cameraId, dirPath, filename)
    addRoll,_ = tiltRoll(image, cameraId, dirPath, filename)
    accumulatedRoll += addRoll

    #If the changes are large the loop bellow might be needed
    
    xDifference = 10
    yDifference = 10
    tries = 0
    while xDifference > 1 and tries <= 5:
        filename = f"slutbildPanCamera{cameraId}"
        image = cameraControl.takePicture(cameraId, dirPath, filename)
        addPan, xDifference = panCenter(image, cameraId, dirPath, filename)
        acculumatedPan += addPan
        tries += 1
        print("xDifference: ", xDifference)

    tries = 0
    while yDifference > 1 and tries <= 5:
        filename = f"slutbildTiltCamera{cameraId}"
        image = cameraControl.takePicture(cameraId, dirPath, filename)
        addTilt, yDifference = tiltCenter(image, cameraId, dirPath, filename)
        accumulatedTilt += addTilt
        tries += 1
        print("yDifference: ", yDifference)
    
    filename = f"slutbildCamera{cameraId}"
    image = cameraControl.takePicture(cameraId, dirPath, filename)
    image = cv2.circle(image, (centerX, centerY), radius=10, color=(0, 0, 255), thickness=-1)
    cv2.imwrite(os.path.join(dirPath, filename + "MarkeratCentrum.jpg"), image)

    acculumatedPan = round(acculumatedPan,1)
    accumulatedTilt = round(accumulatedTilt,1)
    accumulatedRoll = round(accumulatedRoll,1)

    actualPan = round(pan - acculumatedPan,1)
    actualTilt = round(tilt - accumulatedTilt,1)
    actualRoll = round(roll - accumulatedRoll,1)

    return actualPan, actualTilt, actualRoll, rollAngleFromFirstImage

#   Turns all cameras at once
def turnAllCameras(variable, stepsize, sleeptime):
    cameraControl.rollOrTiltOrPanOneDirection(0, variable, stepsize, sleeptime)
    cameraControl.rollOrTiltOrPanOneDirection(1, variable, stepsize, sleeptime)
    cameraControl.rollOrTiltOrPanOneDirection(2, variable, stepsize, sleeptime)
    cameraControl.rollOrTiltOrPanOneDirection(3, variable, stepsize, sleeptime)

#   Analyzes the rollangle from a image   
def rollAngleFromStillImage(cameraId, dirPath):
    filename = f"angleFromPictureDirectlyCamera{cameraId}"
    xDist = 0

    image = cameraControl.takePicture(cameraId, dirPath, filename)
    x, y = getCoordinatesForGreenTarget(image)
    x2, y2 = getCoordinatesForRedTarget(image)
    xDist = x2 - x
    yDist = y2 - y
    print(xDist)
    print(yDist)

    angle_radians = np.arctan(yDist/xDist)  # Calculate arctan of Ydist and Xdist, in radians
    angle_degrees = np.degrees(angle_radians)

    return round(angle_degrees,2)

#   Writes results to a textfile
def writeToFileResult(result_file, cameraId, actualPan, actualTilt, actualRoll, rollAngleFromFirstImage):
    with open (result_file, "a") as file:
            file.write(f"Camera: {cameraId}, ")
            file.write(f"actualPan: {actualPan}, ")
            file.write(f"actualTilt: {actualTilt}, ")
            file.write(f"actualRoll: {actualRoll}, ")
            file.write(f"rollAngleFromFirstImage: {rollAngleFromFirstImage}\n")

            