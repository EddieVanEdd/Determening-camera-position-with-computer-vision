import ansats4Functions
import cameraControl
import os
import time

####################################################################################
### Hårdvaruspecifika funktioner är inte publika därför delas inte cameraControl ###
####################################################################################

# cameradId 0-3 är i webbläsaren 1-4
cameraId = 0
parentFolder = "/home/dennipl/Desktop/yttreFixturTest"
resultFile = os.path.join(parentFolder, "outerTargetMeasurements.txt")
variable = "pan"
stepsize = -45
sleeptime = 5

# Kamera går tillbaks till utgångsläget kamera 0:0 grader, 1:90 grader, 2:180 grader, 3:270 grader

cameraControl.updateSetPosition(0,0,-16,0)
cameraControl.updateSetPosition(3,270,-16,0)
cameraControl.updateSetPosition(2,180,-16,0)
cameraControl.updateSetPosition(1,90,-16,0)

#bildtagning kamera 0
print("Bildtagning kamera ", cameraId)
actualPan, actualTilt, actualRoll, rollAngleFromFirstImage = ansats4Functions.centering(cameraId, parentFolder)
ansats4Functions.writeToFileResult(resultFile, cameraId,actualPan, actualTilt, actualRoll, rollAngleFromFirstImage)
print("actualPan: ", actualPan, ", actualTilt: ", actualTilt, ", actualRoll: ", actualRoll, ", rollAngleFromFirstImage: ", rollAngleFromFirstImage)

#bildtagning kamera 1

cameraControl.turnAllCameras(variable, stepsize, sleeptime)
cameraControl.turnAllCameras(variable, stepsize, sleeptime)

cameraId = 1
print("Bildtagning kamera ", cameraId)
actualPan, actualTilt, actualRoll, rollAngleFromFirstImage = ansats4Functions.centering(cameraId, parentFolder)
ansats4Functions.writeToFileResult(resultFile, cameraId,actualPan, actualTilt, actualRoll, rollAngleFromFirstImage)
print("actualPan: ", actualPan, ", actualTilt: ", actualTilt, ", actualRoll: ", actualRoll, ", rollAngleFromFirstImage: ", rollAngleFromFirstImage)

#bildtagning kamera 2
cameraControl.turnAllCameras(variable, stepsize, sleeptime)
cameraControl.turnAllCameras(variable, stepsize, sleeptime)

cameraId = 2
print("Bildtagning kamera ", cameraId)
actualPan, actualTilt, actualRoll, rollAngleFromFirstImage = ansats4Functions.centering(cameraId, parentFolder)
ansats4Functions.writeToFileResult(resultFile, cameraId,actualPan, actualTilt, actualRoll, rollAngleFromFirstImage)
print("actualPan: ", actualPan, ", actualTilt: ", actualTilt, ", actualRoll: ", actualRoll, ", rollAngleFromFirstImage: ", rollAngleFromFirstImage)

#bildtagning kamera 3
stepsize = 45
cameraControl.turnAllCameras(variable, stepsize, sleeptime)
cameraControl.turnAllCameras(variable, stepsize, sleeptime)
cameraControl.turnAllCameras(variable, stepsize, sleeptime)
cameraControl.turnAllCameras(variable, stepsize, sleeptime)
cameraControl.turnAllCameras(variable, stepsize, sleeptime)

cameraControl.updateSetPosition(0,90,-16,0)
cameraControl.updateSetPosition(3,360,-16,0)
cameraControl.updateSetPosition(2,270,-16,0)
cameraControl.updateSetPosition(1,180,-16,0)
time.sleep(5)

cameraId = 3
print("Bildtagning kamera ", cameraId)
actualPan, actualTilt, actualRoll, rollAngleFromFirstImage = ansats4Functions.centering(cameraId, parentFolder)
ansats4Functions.writeToFileResult(resultFile, cameraId,actualPan, actualTilt, actualRoll, rollAngleFromFirstImage)
print("actualPan: ", actualPan, ", actualTilt: ", actualTilt, ", actualRoll: ", actualRoll, ", rollAngleFromFirstImage: ", rollAngleFromFirstImage)

# Kamera går tillbaks till utgångsläget kamera 0:0 grader, 1:90 grader, 2:180 grader, 3:270 grader 
stepsize = -45  
sleeptime = 5
cameraControl.turnAllCameras(variable, stepsize, sleeptime)
cameraControl.turnAllCameras(variable, stepsize, sleeptime)
cameraControl.updateSetPosition(0,0,-16,0)
cameraControl.updateSetPosition(3,270,-16,0)
cameraControl.updateSetPosition(2,180,-16,0)
cameraControl.updateSetPosition(1,90,-16,0)
print("Gått tillbaks till utgångsläge")