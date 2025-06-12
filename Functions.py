import matplotlib.pyplot as plt
import numpy as np
import cv2
import os
import math


values = [0]*16
no_of_Pix = 0 
centroid = 0
mask_radius = 0
count_total = 0
tilt_list = []
color_count = 0
list_container = {}

def coordDist(image):

    height, width = image.shape[:2]
    centreY = height//2
    centreX = width//2

    analysis = cv2.connectedComponentsWithStats(image , 8, cv2.CV_32S)
    (_, _, _, centroid) = analysis
    x = round(centroid[0][0])
    y = round(centroid[0][1])

    y1 = min(y, centreY)
    y2 = max(y, centreY)
    x1 = min(x, centreX)
    x2 = max(x, centreX)
    
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def coordDistXY(image):

    xDist = 0
    yDist = 0
    height, width = image.shape[:2]
    centreY = height//2
    centreX = width//2

    analysis = cv2.connectedComponentsWithStats(image , 8, cv2.CV_32S)
    (_, _, _, centroid) = analysis
    x = round(centroid[0][0])
    y = round(centroid[0][1])

    print(f"Centroid: {centroid}")

    xDist = (x - centreX)
    yDist = (y - centreY)

    return xDist, yDist

def angle_between_coords(x,y,x2,y2):

    xDist = x2 - x
    yDist = y2 - y
    angle_radians = np.arctan(yDist/xDist)  # Calculate arctan of Ydist and Xdist, in radians
    angle_degrees = np.degrees(angle_radians)

    return angle_degrees

def draw_line_to_coord(x, y, image, circle_radius):

    height, width = image.shape[:2]
    centreY = height//2
    centreX = width//2
    x = centreX + x
    y = centreY + y

    cv2.circle(image, (centreX, centreY), circle_radius, 255, -1)
    cv2.circle(image, (x, y), circle_radius, 255, -1)
    cv2.line(image, (x, y), (centreX, centreY), (129,129,129), 3)

    resized_image= cv2.resize(image, (960, 720))
    cv2.imshow("Lined image", resized_image)


def tiltFromImageName(imagepath):
    filename = os.path.basename(imagepath)
    afterT_ = filename.split("T_")[1]
    tilt = afterT_.split("R_")[0]
    return tilt

def rollFromImageName(imagepath):
    filename = os.path.basename(imagepath)
    afterR_ = filename.split("R_")[1]
    roll = afterR_.split(".jpg")[0]
    return roll 

def camFromImageName(imagepath):
    filename = os.path.basename(imagepath)
    afterId_ = filename.split("Id_")[1]
    cam = afterId_.split("Nr")[0]
    return cam 

def fillWhiteSpots(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask =  np.zeros_like(image)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    cv2.drawContours(mask, [contours[0]], -1, 255, thickness=cv2.FILLED)
    result = cv2.bitwise_and(image, mask)
    return result

def handleImage (image, nbr):

    # SHOW BLURRED
    blurred = cv2.bilateralFilter(image, 15, 105, 15)

    if nbr == 0:
        show_image(blurred, 0, "blurred")
    
    # SHOW GRAY BLURRED
    blurred_gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    
    if nbr == 0:
        show_image(blurred_gray, 0, "blurred gray")

    (_, thresh_blurred_gray) = cv2.threshold(blurred_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = np.ones(34, np.uint8)
    morpho = cv2.morphologyEx(thresh_blurred_gray, cv2.MORPH_OPEN, kernel)

    return morpho

def mask(image, tilt, file_path, nbr):

    global totalLabels
    global label_ids
    global no_of_Pix
    global centroid
    global mask_radius

    height, width = image.shape[:2]
    halfHeight = height//2
    halfWidth = width//2
    x = False
    minRadius = min(halfHeight, halfWidth)
    maxRadius = max(halfHeight, halfWidth)

    if (mask_radius == 0):
        mask_radius = minRadius

    while(x == False): 

        mask = np.zeros_like(image) # Creates a black image
        if nbr == 0:
            show_image(mask, 0,"masking")

        cv2.circle(mask, (halfWidth, halfHeight), mask_radius, 255, -1) # draws a circle in the image and fills it (-1) with a value (255)
        maskInverted = cv2.bitwise_not(mask)
        
        maskedImageWhiteEdge = cv2.bitwise_or(maskInverted, image)
        if nbr == 0:
            show_image(mask, 1,"mask")
            show_image(maskInverted, 1 ,"mask inverted")
            show_image(maskedImageWhiteEdge, 0,"masked - component")
        
        if nbr == 3:
            show_image(mask, 1,"mask - target")
            show_image(maskInverted, 1 ,"mask inverted - target")
            show_image(maskedImageWhiteEdge, 0,"masked - component - target")

        (totalLabels, label_ids, values, centroid) = cv2.connectedComponentsWithStats(maskedImageWhiteEdge , 8, cv2.CV_32S)
        no_of_Pix = values[0,4]     # amount of pixels in component 0

        # Check how many pixels there are in the masked component
        if(no_of_Pix < 15000):

            if(mask_radius <= minRadius-50):
                mask_radius += 50
            else:
                maskedImageWhiteEdge = f"ERROR: Edge is out of range, in image: {file_path}"
                distance = 0
                return maskedImageWhiteEdge, distance

        elif(no_of_Pix > 200000):
            mask_radius -= 50
            
        # Check if centroid of label [0] is NaN, if so - show image
        elif np.isnan(centroid[0][0]) and (mask_radius > maxRadius):
            
            maskedImageWhiteEdge = f"ERROR: There's no component inside the radius in image '{file_path}'"
            distance = 0
            return maskedImageWhiteEdge, distance
        
        else:
            mask = 0
            print("mask_radius3", mask_radius)
            x = True

    
    startpoint = (halfWidth, halfHeight)
    endX = int(round((centroid[0][0])))
    endY = int(round((centroid[0][1])))
    endpoint = (endX, endY)
    print(f"startpoint ={startpoint}, endpoint = {endpoint}")
    # cv2.waitKey(0)

    distance = center_to_edge_dist(maskedImageWhiteEdge, startpoint, endpoint, nbr) # nbr only for presentation, so that image only show first time
    distance_percent =  (distance/minRadius)*100

    string = (f"Distance center to edge is: {distance_percent}%, in tilt{tilt} \n")
    
    with open("/home/edvinl/test/distances.txt", "a") as fil:
                    fil.write(string + "\n")  

    return maskedImageWhiteEdge, distance_percent


def angleToCentroid(image, nbr, tilt):

    height, width = image.shape[:2]
    centreY = height//2
    centreX = width//2
    tilt = int(round(float(tilt)))

    x = round(centroid[0][0])
    y = round(centroid[0][1])
    Xdist = x - centreX
    Ydist = centreY - y

    cv2.line(image, (x, y), (centreX, centreY), (129,129,129), 3)
    cv2.circle(image,(x, y), 29, (129,129,129), 6) 
    cv2.circle(image,(centreX, centreY), 29, (129,129,129), 6) 


    if(Xdist == 0):
        angle_degrees = 0
    elif(Ydist<0 and Xdist<0): #in case the angle is in the third quadrent
        angle_radians = np.arctan(Xdist/Ydist)  # Calculate arctan of Ydist and Xdist, in radians
        angle_degrees = np.degrees(angle_radians)
        angle_degrees = -angle_degrees-90
        save = angle_degrees
    else:
        angle_radians = np.arctan(Ydist/Xdist)  # Calculate arctan of Ydist and Xdist, in radians
        angle_degrees = np.degrees(angle_radians)
        save = angle_degrees
        print(f"Xdist: {Xdist}, Ydist: {Ydist}, before any changes.")

        if(angle_degrees > 180):
            angle_degrees = (angle_degrees - 360) # if angle_degrees is bigger then 180 change it to a negative degree value

    if(45 < angle_degrees <= 180): # translate camera angle to calculated angle. Intervals with a margin
        angle_degrees = (90 - angle_degrees) #
        
    elif(-135 < angle_degrees < 45):
            angle_degrees = -(90 + angle_degrees)
        
    elif(-180 < angle_degrees < -135):
        # sets limit to -20 even thou the edge's not visible under tiltvalues of -16
        angle_degrees = -(270 + angle_degrees)
        
    else:
        angle_degrees = "Angle is out of range"    
    if (angle_degrees < -100):
        show_image(f"Look at this angle, supposed to be {angle_degrees}???. Before: {save}, Ydist = {Ydist}, Xdist = {Xdist}", 0, image)
    if nbr == 0:
        show_image(image,1,"Angle calculation")
    return angle_degrees
    
def showValues(title, directory):

    global count_total 
    if count_total != 0:
        # Calculate percentages for each interval
        perc_values = [round((values[i] / count_total) * 100, 1) for i in range(len(values))]

# Define the category labels with corresponding percentages
    categories = [
    f"0.0-0.05 \n({perc_values[0]}%)",
    f"0.05-0.1 \n({perc_values[1]}%)",
    f"0.1-0.15 \n({perc_values[2]}%)",
    f"0.15-0.2 \n({perc_values[3]}%)",
    f"0.2-0.3 \n({perc_values[4]}%)",
    f"0.3-0.4 \n({perc_values[5]}%)",
    f"0.4-0.5 \n({perc_values[6]}%)",
    f"0.5-0.6 \n({perc_values[7]}%)",
    f"0.6-0.7 \n({perc_values[8]}%)",
    f"0.7-0.8 \n({perc_values[9]}%)",
    f"0.8-0.9 \n({perc_values[10]}%)",
    f"0.9-1.0 \n({perc_values[11]}%)",
    f"1.0-1.2 \n({perc_values[12]}%)",
    f"1.2-1.4 \n({perc_values[13]}%)",
    f"1.4-1.6 \n({perc_values[14]}%)",
    f"1.6+ \n({perc_values[15]}%)"]

    plt.figure(figsize=(12, 6))  # Width x Height (justera vid behov)

    # Rotera kategorinamnen och justera avståndet
    plt.xticks(rotation=45, ha="right")
    
    # plt.tight_layout()
    
    # Skapa stapeldiagram
    plt.bar(categories, values)

    # Lägg till etiketter
    plt.xlabel('Differens mellan kamerans tro och den beräknade vinkeln, i grader:')
    plt.ylabel('Antal')
    plt.title(title)

    # Spara diagrammet till en fil
    plt.savefig(directory)

    # Visa diagrammet
    plt.show()


def categorize(tilt_percent):
    global count_total
    count_total += 1

    intervals = [
        (0.0, 0.05), (0.05, 0.1), (0.1, 0.15), (0.15, 0.2), (0.2, 0.3),
        (0.3, 0.4), (0.4, 0.5), (0.5, 0.6), (0.6, 0.7),
        (0.7, 0.8), (0.8, 0.9), (0.9, 1.0), (1.0, 1.2),
        (1.2, 1.4), (1.4, 1.6), (1.6, float('inf')) 
    ]

    for i, (low, high) in enumerate(intervals):
        if low <= abs(tilt_percent) < high:
            values[i] += 1
            return

    values[len(intervals)-1] += 1  # If tilt_percent is 1.6 or more
    

def center_to_edge_dist(image, start_point, end_point, nbr):


    # Skapa en kopia av bilden för att rita linjen
    image_with_line = image.copy()
    
    cv2.circle(image_with_line, (start_point), 19, 129, -1) 
    # SHOW IMAGE WITH CIRCLE
    if nbr == 0:
            show_image(image_with_line, 0, "mask")
    cv2.circle(image_with_line, (end_point), 19, 129, -1)
    # SHOW IMAGE WITH CIRCLE
    if nbr == 0:
            show_image(image_with_line, 0, "mask")

    cv2.line(image_with_line, start_point, end_point, 129, 1)
    if nbr == 0:
        show_image(image_with_line, 0, "mask")
    
    # Extrahera pixelvärden längs linjen
    mask = np.zeros_like(image, dtype=np.uint8)  # Skapa en mask
    if nbr == 0:
        show_image(mask, 0, "mask")

    cv2.line(mask, start_point, end_point, 255, 1)  # Dra linje på masken
    white_pixels = np.sum(image[mask == 255] == 255)  # Räkna vita pixlar

    print(f"Antal vita pixlar längs linjen: {white_pixels}")

    return white_pixels

# Resize and show image
def show_image(image, wait = 0, name = "image"):

    resize_image = cv2.resize(image, (960,720))
    cv2.imshow(f"{name}", resize_image)
    cv2.waitKey(wait)

# Makes a list of lists
def add_list(name, element): 

    global list_container

    if name not in list_container: # Adds a new list if there's not already a list with the same name 
        list_container[name] = []
        list_container[name].append(element)

    else:
        list_container[name].append(element) # adds element to excisting list with the same name 

# Makes list of lists
def string_list_container(data_directory, nbr = 1, ansats = "."):
    string_list = []

    if nbr == 2:                    # make a diagram as well if nbr == 2
        diagram_list_container(data_directory, ansats)
        print("Ansats:", ansats)

    # Iterate through the dictionary and process each list
    for name, values in list_container.items():
        list_length = len(values)  
        values.sort()                                       

        if list_length > 0:
            average_tilt = round((sum(values) / list_length), 2)  # Calculate the average tilt
            min_tilt = values[0]    # Get min tilt value
            max_tilt = values[-1]  # Get max tilt value

            # Format and store the results as a string
            string_list.append(f"\t{name}, \taverage tilt: {average_tilt}, \tmin tilt: {round(min_tilt,1)}, \tmax tilt: {round(max_tilt),1}")

    list_container.clear()  # Clear the dictionary

    with open(data_directory, "a") as fil:
            fil.write(data_directory)
    
import matplotlib.pyplot as plt
import numpy as np


def diagram_list_container(data_directory, ansats):
    data_directory = data_directory.replace('txt', ' tilt percent.jpg')  # Change file format

    # Sortera x-värdena numeriskt och bevara matchande y-värden
    sorted_items = sorted(list_container.items(), key=lambda x: float(x[0]))  # Sortera på nyckeln (x-värdet)
    x_values, y_values = zip(*sorted_items)  # Dela upp i separata listor

    # Skapa jämnt fördelade positioner för de sorterade x-värdena
    x_positions = np.arange(len(x_values))  # Numeriska positioner

    # Flatten data for plotting
    x_plot = []
    y_plot = []

    for i, values in enumerate(y_values):
        x_plot.extend([x_positions[i]] * len(values))  # Jämnt fördelade x-positioner
        y_plot.extend(values)  # Collect all values

    string = f"Tilt % distribution / Tilt angle"
    string = ansats + "\n" + string  

    # Create scatter plot
    plt.scatter(x_plot, y_plot, label="Individual Tilt Values", color="magenta", marker="o", s=100)

    plt.legend()
    plt.xlabel("Categories")  # Label x-axis
    plt.ylabel("Tilt %")  # Label y-axis
    plt.title(string)

    # Sätt x-ticks för att matcha dina kategorier, och jämnt fördela dem
    plt.xticks(x_positions, x_values, rotation=45)  
    
    plt.grid(True)  # Add grid for better visualization

    plt.savefig(data_directory)  # Save the diagram
    plt.show()  # Display the plot
