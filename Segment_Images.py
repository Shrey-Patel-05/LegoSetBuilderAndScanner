import cv2
import numpy as np
from pathlib import Path



def ProcessCenteredImage(unprocessed_image):

    # Opening the primary image (used in background) 
    background = cv2.imread('Images/Logos/Black_img.png')
    background= np.resize(background,[int(unprocessed_image.shape[0]*2.4),int(unprocessed_image.shape[1]*2.4)])
    

    # Work out midpoints of both images
    background_image_mid=[int(background.shape[0]/2),int(background.shape[1]/2)]
    unprocessed_image_mid= [int(unprocessed_image.shape[0]/2),int(unprocessed_image.shape[1]/2)]

    
    # index from top right of center box, to bottom right
    for i in range(background_image_mid[0]-unprocessed_image_mid[0], background_image_mid[0]+unprocessed_image_mid[0]+1):
        for j in range(background_image_mid[1]-unprocessed_image_mid[1], background_image_mid[1]+unprocessed_image_mid[1]+1):
            background[i][j]= unprocessed_image[i-(background_image_mid[0]-unprocessed_image_mid[0])-1][j-(background_image_mid[1]-unprocessed_image_mid[1])-1]
        
    
    processed_image= cv2.resize(background, (128, 128),interpolation=cv2.INTER_CUBIC)
    
    return processed_image
   


def ImagePreProcessing(img_fg):
    
    #load a background, so we can extract it and make it easy to detect the object.
    img_bg=cv2.imread('Images/Scanned_images/Background.png')

    #make both images grey and calculate difference to identify bricks
    img_bg_gray=cv2.cvtColor(img_bg, cv2.COLOR_BGR2GRAY)
    img_gray=cv2.cvtColor(img_fg, cv2.COLOR_BGR2GRAY)
    diff_gray=cv2.absdiff(img_bg_gray,img_gray)

    # applying a blur filter reduces image noise and 'smooths' edges 
    diff_gray_blur = cv2.GaussianBlur(diff_gray,(5,5),0)

    # performs OTSU thresholding
    ___, img_tresh =  cv2.threshold(diff_gray_blur,0,255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return img_tresh


def ExtractPartsFromImage():
    # Delete all files currently in inventory  (from stack overflow)
    [f.unlink() for f in Path("Images/Segmented_Images/Contours_Individual").glob("*") if f.is_file()]  

    img_fg= cv2.imread('Images/Scanned_images/Foreground.png')
    img_tresh= ImagePreProcessing(img_fg)


    # Finds the contours
    arr_cnt, BLANK= cv2.findContours(img_tresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Copy the example image so it does not get painted over
    img_with_allcontours=img_fg.copy()

    # Draws the contours
    cv2.drawContours(img_with_allcontours, arr_cnt, -1, (0,255,0), 30)

    cv2.imwrite('Images/Segmented_Images/Contours_Whole/Camera_View.png',img_with_allcontours)

    criticalArea= (img_with_allcontours.shape[0]*img_with_allcontours.shape[1])/2000
    

    # Iterate through contours and draw only significant contours
    brick_count=0
    for contour in arr_cnt:
        
        if cv2.contourArea(contour) > criticalArea:  # if there is a significant area, likely to a brick and not noise

            # Draw a rectangle around the contour in the visualization image
            cv2.drawContours(img_with_allcontours, [contour], -1, (0, 255, 0), 30)

            # Create a mask for the current contour
            mask = np.zeros_like(img_tresh)
            
            cv2.drawContours(mask, [contour], 0, 255, thickness=cv2.FILLED)

            # Bitwise AND operation to extract the part (as all elements are now 1s or 0s)
            part = cv2.bitwise_and(img_fg, img_fg, mask=mask)

            # Crop the centered part after finding the bounding box
            x, y, w, h = cv2.boundingRect(contour)
            centered_part = part[y: y + h, x:x + w]
            centered_part=cv2.cvtColor(centered_part, cv2.COLOR_BGR2GRAY) 
            #centered_part = centered_part[y: h+ y, x: w+ x]
            
            
            brick_count+=1
            

            # Get the centered image to have a similar style to train and test data
            final_image=ProcessCenteredImage(centered_part)

            # Save the centered brick as a separate image
            cv2.imwrite(f'Images/Segmented_Images/Contours_Individual/contour_{brick_count}_centered.png', final_image)



