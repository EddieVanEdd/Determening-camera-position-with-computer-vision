import bildinsamlingFunctions
import os
import time

dirPath = "/home/dennipl/Documents/project/tagna_bilder/Bildinsamling4"

# Kamera går tillbaks till utgångsläget kamera 0:0 grader, 1:90 grader, 2:180 grader, 3:270 grader 
bildinsamlingFunctions.updateSetPosition(0,0,-45,0)
print("Steg 1")
bildinsamlingFunctions.updateSetPosition(3,270,-45,0)
print("Steg 2")
bildinsamlingFunctions.updateSetPosition(2,180,-45,0)
print("Steg 3")
bildinsamlingFunctions.updateSetPosition(1,90,-45,0)
print("Steg 4")

# Kamera 0 och 1 tar ska ta bilder. Radar upp sig med uppställning från vänster: 3, 0, 1, 2 
bildinsamlingFunctions.updateSetPosition(0,0,-45,0)
print("Steg 5")
bildinsamlingFunctions.updateSetPosition(1,50,-45,0)
print("Steg 6")
bildinsamlingFunctions.updateSetPosition(2,100,-45,0)
print("Steg 7")
bildinsamlingFunctions.updateSetPosition(3,310,-45,0)
print("Steg 8")

#   Range -14 till -150
#   min maxVinkel innan ytterkanten försvinner -18
#   max minVinkel innan innerkanten försvinner -141

for kameraNr in range(0, 2):
    dirPathUpdatedKamera = os.path.join(dirPath, f"Kamera{kameraNr}")
    os.makedirs(dirPathUpdatedKamera, exist_ok=True)
    bildinsamlingFunctions.updateSetPosition(kameraNr, 50, -14, 0)
    for tilt in range(14, 20):
        dirPathUpdatedTilt = os.path.join(dirPathUpdatedKamera, f"Tilt-{tilt}")
        os.makedirs(dirPathUpdatedTilt, exist_ok=True)
        bildinsamlingFunctions.enKameraSamlarInBilder5(kameraNr, dirPathUpdatedTilt, -tilt)
        print(f"Klar kamera:{kameraNr} tilt:{tilt}")
    bildinsamlingFunctions.updateSetPosition(kameraNr,50,-140,0)
    time.sleep(8)
    for tilt in range(140, 151):
        dirPathUpdatedTilt = os.path.join(dirPathUpdatedKamera, f"Tilt-{tilt}")
        os.makedirs(dirPathUpdatedTilt, exist_ok=True)
        bildinsamlingFunctions.enKameraSamlarInBilder5(kameraNr, dirPathUpdatedTilt, -tilt)
        print(f"Klar kamera:{kameraNr} tilt:{tilt}")

# Kamera 3 tar ska ta bilder. Radar upp sig med uppställning från vänster: 2, 3, 0, 1
bildinsamlingFunctions.updateSetPosition(2,261,-45,0)

kameraNr = 3
dirPathUpdatedKamera = os.path.join(dirPath, f"Kamera{kameraNr}")
os.makedirs(dirPathUpdatedKamera, exist_ok=True)
for tilt in range(14, 20):
    dirPathUpdatedTilt = os.path.join(dirPathUpdatedKamera, f"Tilt-{tilt}")
    os.makedirs(dirPathUpdatedTilt, exist_ok=True)
    bildinsamlingFunctions.enKameraSamlarInBilder5(kameraNr, dirPathUpdatedTilt, -tilt)
    print(f"Klar kamera:{kameraNr} tilt:{tilt}")
time.sleep(10)
for tilt in range(140, 151):
    dirPathUpdatedTilt = os.path.join(dirPathUpdatedKamera, f"Tilt-{tilt}")
    os.makedirs(dirPathUpdatedTilt, exist_ok=True)
    bildinsamlingFunctions.enKameraSamlarInBilder5(kameraNr, dirPathUpdatedTilt, -tilt)
    print(f"Klar kamera:{kameraNr} tilt:{tilt}")

print("Steg 7")

# Kamera 2 tar ska ta bilder. Radar upp sig med uppställning från vänster: 1, 2, 3, 0
bildinsamlingFunctions.updateSetPosition(1,211,-45,0)

kameraNr = 2
dirPathUpdatedKamera = os.path.join(dirPath, f"Kamera{kameraNr}")
os.makedirs(dirPathUpdatedKamera, exist_ok=True)
bildinsamlingFunctions.updateSetPosition(kameraNr,211,-14,0)
for tilt in range(14, 20):
    dirPathUpdatedTilt = os.path.join(dirPathUpdatedKamera, f"Tilt-{tilt}")
    os.makedirs(dirPathUpdatedTilt, exist_ok=True)
    bildinsamlingFunctions.enKameraSamlarInBilder5(kameraNr, dirPathUpdatedTilt, -tilt)
    print(f"Klar kamera:{kameraNr} tilt:{tilt}")
bildinsamlingFunctions.updateSetPosition(kameraNr,211,-140,0)
time.sleep(8)
for tilt in range(140, 151):
    dirPathUpdatedTilt = os.path.join(dirPathUpdatedKamera, f"Tilt-{tilt}")
    os.makedirs(dirPathUpdatedTilt, exist_ok=True)
    bildinsamlingFunctions.enKameraSamlarInBilder5(kameraNr, dirPathUpdatedTilt, -tilt)
    print(f"Klar kamera:{kameraNr} tilt:{tilt}")

# Kamera går tillbaks till utgångsläget 0:0 grader, 1:90 grader, 2:180 grader, 3:270 grader
bildinsamlingFunctions.updateSetPosition(1,90,-45,0)
bildinsamlingFunctions.updateSetPosition(2,180,-45,0)
bildinsamlingFunctions.updateSetPosition(3,270,-45,0)