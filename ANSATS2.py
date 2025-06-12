import cv2
import os
import math
import imutils
import Functions as FUNC

count_calculated_angles = 0
count_unreadable_angles = 0

class my_angleCal:

    Folder = "Directory of´folder with images that are to be imported" 
    file_path = "Directory to where you want your file to be" 
    data_directory = "Directory to where you want your data file to be"

    count_total = 0
    big_tilt_list = []
    tilt_list = []
    angles = []

    average_angles = []
    out_of_range = []

    with open(data_directory, "w") as fil:  # "w" creates file if it doesn't already excist
            fil.write("INSAMLAD DATA Ansats 2: \n")

    for foldername, subfolders, filenames in os.walk(Folder):
        print(f"📁 Mapp: {foldername}, subfolder: {subfolders}")
        
        min_tilt_percent = 9999
        max_tilt_percent = -1 
        
        # Loops through all the files in the current mapp
        for filename in filenames:

            count_total += 1
            tilt_measure = True
            file_path = os.path.join(foldername, filename)
            curr_tilt = float(FUNC.tiltFromImageName(file_path))
            out_of_range_bool = False

            if filename.lower().endswith((".jpg")):  # We're only interested in jpg-files
                
                # count_total += 1
                roll = int(round(float(FUNC.rollFromImageName(filename))))              # Set point roll value from image title
                curr_tilt = int(round(float(FUNC.tiltFromImageName(filename))))         # Set point tilt value from image title
                curr_cam = FUNC.camFromImageName(filename)                              # Number of the camera that collected the image
                image = cv2.imread(file_path)

                if image is None:       # If image not readable continue to next itteration in for loop
                    count_unreadable_angles += 1
                    with open(data_directory, "a") as fil:
                        fil.write(f"Fel: Kunde inte läsa in bilden från {file_path}")
                    continue

                if curr_tilt > -40:
                    rotation = 180 + roll
                else:
                    rotation = roll

                orig_rot  = imutils.rotate(image, rotation)
                image_rotated = FUNC.handleImage(orig_rot, 1)
    
                shape = orig_rot.shape
                height = shape[0]
                width = shape[1]
                midX = int(width/2)
                midY = int(height/2) 
                count = 0
                sum_angle = 0
                
                # Search for the edge of the fixture
                for i in range(2,19):
                    count = count + 1

                    point_b = midX-(15*i)
                    point_c = midX+(15*i)
                    
                    # Search for the edge of the fixture, left hand side of image center
                    for b in range(midY, height-1):

                        pixelBW = image_rotated[b, point_b]                         

                        if pixelBW == 0:                                            # When black pixel found, break loop
                            break

                    cv2.circle(image_rotated,(point_b, b), 5, (129,129,129), 3)     # Draw a circle around point b 

                    # Search for the edge of the fixture,right hand side of image center
                    for c in range(midY, height-1):
                        
                        pixelBW = image_rotated[c, point_c]     

                        if pixelBW == 0:                                            # When black pixel found, break loop
                            break
                    cv2.circle(image_rotated,(point_c, c), 5, (129,129,129), 3)     # Draw a circle around point c 

                    if (b>c):                                                       # Compare found coordinates of the edge to make the right angle calculation
                        heightDiffBC = b-c
                    else: 
                        heightDiffBC = ( c-b)

                    Xdist_BC = point_c-point_b

                    angle = (math.atan(heightDiffBC/Xdist_BC))*180/math.pi  # Calculate angle between point b and c

                    if tilt_measure == True:                                # Include only the first b and c value in the calculation of tilt value
                        tilt_distance = (b + c - 2*midY)/2
                        tilt_percent = round((tilt_distance/midY)*100, 2)
                        tilt_measure = False

                    if tilt_distance < midY - 2:                            # Only let through images with visable fixture
                        
                        FUNC.add_list(curr_tilt, tilt_percent)
                        angles.append(angle)                                # Put calculated angle in list "angles" 
                        sum_angle = sum_angle + angle
                        count_calculated_angles += 1

                    else:
                        count_unreadable_angles += 1
                        out_of_range.append(f"\nOut of range - Camera setpoint: {roll}\tFrom file: {file_path}")
                        i = 24
                        out_of_range_bool = True
                        break
                        # tilt_measure = False
                
                if out_of_range_bool == True:   # If out_of_range_bool == True - proceed to next image  
                    continue

                FUNC.show_image(image_rotated,15,"orig_rot")  

                cal_av_angle = round(sum_angle/count, 2) # average measured angle value
                resized_image_rotated = cv2.resize(image_rotated, (1280, 720))

                angles.sort()
                
                median_val_at = int(len(angles)/2)
                print(f"median_val_at: {median_val_at}, angle length: {len(angles)}")
                median_val = angles[median_val_at]
                average_value = round((sum(angles)/len(angles)), 2)
                print(f"angles length: {len(angles)}")
                print(f"\nAngles: {angles}, Median: {median_val} (median val at: {median_val_at}), Average: {average_value} file: {file_path}")
                
                FUNC.categorize(average_value)

                string = (f"Camera setpoint: {roll}\tAverage diff. = {average_value}\tMedian diff. = {round(angles[median_val_at],2)}\tFrom File: {file_path} \n")
                average_angles.append(string)
                angles.clear()
                
    # Sort based on "average_value"
    sorted_list = sorted(average_angles, key=lambda x: float(x.split("\t")[1].split("=")[1]))

    for i in range (len(average_angles)):
        with open(data_directory, "a") as fil:
            fil.write(average_angles[i])

    for j in range (len(out_of_range)):
        with open(data_directory, "a") as fil:
            fil.write(out_of_range[j])

    percentage_unreadable_angles = count_unreadable_angles/count_total 
    percentage_calculated_angles = count_calculated_angles/count_total
    
    with open(data_directory, "a") as fil:
        fil.write(f"\nCalculated angles: {count_calculated_angles}, {percentage_calculated_angles*100}% of total {count_total} images.\n")
        fil.write(f"Unreadable angles: {count_unreadable_angles}, {percentage_unreadable_angles*100}% of total {count_total} images.\n")  
    
    count_unreadable_angles = 0
    count_calculated_angles = 0
    percentage_unreadable_angles = 0
    percentage_calculated_angles = 0

    FUNC.string_list_container(data_directory, 2, "Ansats 2") # parameter == 2 in "string_list_container()" makes diagram aswell
    FUNC.showValues("Ansats 2", 'Directory of diagram of rollangle diff')            
    
    average_angles.clear()
    out_of_range.clear()
    angles.clear()

cv2.destroyAllWindows()       