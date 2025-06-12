import time

#####################################################################################
### Hårdvaruspecifika funktioner är inte publika och har klippts ut ur dokumentet ###
#####################################################################################

# En bildinsamling för kamera med nr kameraId som sparar 
# bilderna i mappen dirPath och gör insamlingen vid tilt vinkel
# Absolut minVinkel: -150 Absolut maxVinkel: -14
def enKameraSamlarInBilder5(kameraId, dirPath, vinkel):
    print("Steg Bildinsamling Kamera: " + str(kameraId))
    pan = getStatusCameraPanOrTiltOrRoll(kameraId, "pan")
    updateSetPosition(kameraId, pan, vinkel, 0)
    time.sleep(1)
    filename = "Id_" + str(kameraId) + "Nr_"
    updatedFilename = updateFilename(kameraId, filename, 0)
    takePicture(kameraId, dirPath, updatedFilename)
    time.sleep(0.5)
    updateSetPosition(kameraId, pan, vinkel, -90)
    time.sleep(2)
    filename = "Id_" + str(kameraId) + "Nr_"
    updatedFilename = updateFilename(kameraId, filename, 0)
    takePicture(kameraId, dirPath, updatedFilename)
    time.sleep(0.5)
    updateSetPosition(kameraId, pan, vinkel, 0)
    time.sleep(2)


# Hjälpfunktion till enKameraSamlarInBilder
# Sätter namnet på bilden med löpnummer och uppdaterad ptr.
def updateFilename(kameraId, filename, n):
    n += 1
    updatedFilename = filename + str(n) + "P_" + str(getStatusCameraPanOrTiltOrRoll(kameraId, "pan")) + "T_" + str(getStatusCameraPanOrTiltOrRoll(kameraId, "tilt")) + "R_" + str(getStatusCameraPanOrTiltOrRoll(kameraId, "roll"))
    return updatedFilename
