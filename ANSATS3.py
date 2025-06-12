import os
import cv2
from angleCalculations import * 
import Functions as FUNC


#ang_Cal = angleCalculations()
cal_diff = []
big_diff = []
tilt_list_title = []
count_calculated_angles = 0
count_unreadable_angles = 0
count_total = 0
count_big_diff = 0
prev_tilt = 9999
PRESENTATION = 0        # 0 - show images for presentation, 1 - don't show images 


average_angles = []
out_of_range = []

class my_angleCal:
    Folder = "Directory of´folder with images that are to be imported" 
    file_path = "Directory to where you want your file to be" 
    data_directory = "Directory to where you want your data file to be"              # Directory + title of data file
    stapeldiagram_directory = "Directory to where you want your diagram file to be"    # Directory + title of diagram file

    with open(data_directory, "w") as fil:  # "w" creates file if it doesn't already excist
            fil.write("INSAMLAD DATA Ansats 3: \n")

    for foldername, subfolders, filenames in os.walk(Folder):
        print(f"📁 Mapp: {foldername}, subfolder: {subfolders}")
        
        # Loops through all the files in the current mapp
        for filename in filenames:

            count_total += 1

            path = foldername +"/"+ filename 
            curr_tilt = float(FUNC.tiltFromImageName(path)) 

            if filename.lower().endswith((".jpg")):  # We're only interested in jpg-files
                file_path = os.path.join(foldername, filename)
                roll = FUNC.rollFromImageName(filename)
                curr_tilt = FUNC.tiltFromImageName(filename)
                curr_cam = FUNC.camFromImageName(filename)
                exact_angle = roll
                image = cv2.imread(path) 
                image_copy = image.copy()
                
                # SHOW ORIGINAL
                if PRESENTATION == 0:
                    FUNC.show_image(image, 0, "original")
                
                # Returns a filtered image
                morpho = FUNC.handleImage(image, PRESENTATION)

                if PRESENTATION == 0:
                    FUNC.show_image(morpho, 0, "morph")
   
                funk = FUNC.fillWhiteSpots(morpho)
                funky = funk.copy()

                if PRESENTATION == 0:
                    FUNC.show_image(funky, 0, "filled whites")
                
                funk2, tilt_percent = FUNC.mask(funk, curr_tilt, file_path, PRESENTATION)
                
                FUNC.add_list(curr_tilt, tilt_percent)      # Puts tilt_percent into list of tilt values 

                if PRESENTATION == 0:
                    FUNC.show_image(funk2, 0, "mask")
                    cv2.destroyAllWindows()
                
                if isinstance(funk2, str):
                    count_unreadable_angles += 1
                    with open(data_directory, "a") as fil:
                        fil.write(funk2 + "\n")

                else:
                    # SHOW MASKED AND ORIGINAL IMAGE
                    if PRESENTATION == 0:
                        FUNC.show_image(image_copy, 30, "original")
                        cv2.waitKey(0)

                    # Check angle between image center and component mass center
                    vinkel = FUNC.angleToCentroid(funk2, PRESENTATION, curr_tilt) 
                    
                    if not isinstance(vinkel, (int, float)): 

                        count_unreadable_angles += 1 

                        with open(data_directory, "a") as fil:
                            fil.write(f"{vinkel} blää \n")

                    else:
                        
                        if (curr_tilt != prev_tilt):
                            list_title = f"tilt_{curr_tilt}_cam: {curr_cam}"
                            list = []
                            list.append(list_title)
                            list.append(curr_tilt)
                            tilt_list_title.append(list)
                            prev_tilt = curr_tilt
                        
                        list.append(tilt_percent)

                        difference = float(exact_angle) - vinkel
                        cal_diff.append("difference \n")

                        FUNC.add_list(curr_tilt, tilt_percent)
                        FUNC.categorize(difference)

                        if(abs(difference) > 160):
                            big_diff.append(f"Diff: {difference}, file: {path}")
                            count_big_diff += 1

                        string = f"Calculated angle: {vinkel} Roll from camera: {exact_angle} Difference: {difference} From file: {file_path} \n"
                        with open(data_directory, "a") as fil:
                            fil.write(string)
                        
                        count_calculated_angles += 1   
                PRESENTATION = 1

    # FUNCent some stats:
    percentage_unreadable_angles = count_unreadable_angles/count_total 
    percentage_calculated_angles = count_calculated_angles/count_total
    percentage_big_diff = count_big_diff/count_calculated_angles

    with open(data_directory, "a") as fil:
        fil.write(f"Calculated angles: {count_calculated_angles}, {percentage_calculated_angles*100}% of total {count_total} images.\n")
        fil.write(f"Unreadable angles: {count_unreadable_angles}, {percentage_unreadable_angles*100}% of total {count_total} images.\n")  
        fil.write(f"Big differential (>160 deg.) angles: {count_big_diff}, {percentage_big_diff*100}% of total {count_calculated_angles} calculated angles.\n")     

    for a in range(len(big_diff)):
        
        with open(data_directory, "a") as fil:
            fil.write(f"{big_diff[a]} \n")
    
    FUNC.string_list_container(data_directory, 2, "Ansats 3") # parameter == 2 in "string_list_container()" makes diagram aswell
    FUNC.showValues("Ansats 3", stapeldiagram_directory)