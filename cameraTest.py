import dearpygui.dearpygui as dpg
from PIL import Image
import cv2
import numpy as np
import array 
from Segment_Images import *


dpg.create_context()

# Flags are start,capturing, take_capture
scan_flags= [False,False,False]
output_width= 600
output_height= 400
current_image=1
global image_to_save_data
global vid

# FROM DEARPYGUI DOCUMENTATION - creating dummy data for the texture registry
texture_data = []
for i in range(0, 100 * 100):
    texture_data.append(0)
    texture_data.append(0)
    texture_data.append(0)
    texture_data.append(0)
###############################################################################
    
with dpg.texture_registry():
    dpg.add_raw_texture(width= 1920, height=1080,default_value=texture_data, format= dpg.mvFormat_Float_rgba,tag= 'texture_tag')
    # Will serve as a placeholder for snapshots
    ___, ___, ___, eastbound_data = dpg.load_image("Images/Logos/EastboundAndDown.jpg")
    dpg.add_raw_texture(width=1920, height=1080, default_value=eastbound_data, format=dpg.mvFormat_Float_rgba, tag="ScreenGrab")
  




def StartCapture():
    # Set start flag and get intial capture
    global scan_flags
    global vid
    vid= cv2.VideoCapture(0)
    scan_flags[0]= True

def StopCapture():
    # Set start flag
    global scan_flags
    scan_flags[0]= False



def capture_snapshot():
    global scan_flags
    scan_flags[2]= True



def delete_all_other_open_windows():
    all_items = dpg.get_all_items()
    open_windows = []
    # get all items that are of type window
    for item in all_items:
        if dpg.get_item_info(item)["type"] == "mvAppItemType::mvWindowAppItem":
            open_windows.append(item)
    # then delete these windows
    for i in range(0,len(open_windows)):
        dpg.delete_item(open_windows[i])
        




def UseImage():
    global current_image
    # Save to different files depending on the type of photo
    if current_image==1:
        file_path = "Images/Scanned_images/Background.png"
        cv2.imwrite(file_path, cv2.cvtColor(image_to_save_data, cv2.COLOR_BGR2RGBA))

        # Increment counter and prepare to take the second photo
        current_image+=1
        # Delete the previous window
        dpg.delete_item('Scan Bricks_1')
        dpg.set_value('ScreenGrab',eastbound_data)
        open_scan_input_window()

    elif current_image ==2:
        file_path= "Images/Scanned_images/Foreground.png"
        cv2.imwrite(file_path, cv2.cvtColor(image_to_save_data, cv2.COLOR_BGR2RGBA))
        open_brick_identification_window()






def open_brick_identification_window():
    delete_all_other_open_windows()
    ExtractPartsFromImage()
    with dpg.window(label= 'Identification'):
        dpg.add_text('Camera View')
        with dpg.texture_registry():
            width, height, channels, data = dpg.load_image('Images/Segmented_Images/Contours_Whole/Camera_View.png')
            dpg.add_raw_texture(width=1920, height=1080, default_value=data, format=dpg.mvFormat_Float_rgba, tag="Camera_View")
        dpg.add_image("Camera_View", width= output_width, height= output_height)
        


def open_scan_input_window():
    with dpg.window(tag= 'Scan Bricks_' +str(current_image),label= 'Scan Bricks',width=720,height=1080):
        dpg.add_text(f"Below is your camera output!")
        dpg.add_image('texture_tag',width=output_width,height=output_height)
        dpg.add_button(label='Say Cheese!', callback=capture_snapshot)
        if current_image==1:
            dpg.add_text(f"Below is the background image")
        elif current_image ==2:
            dpg.add_text(f"Below is the image of your Parts")
        dpg.add_image('ScreenGrab',width=output_width,height=output_height)
        dpg.add_button(label= "Use This Image?", callback=UseImage)


with dpg.window(label= 'Test',width=720,height=1080):
    dpg.add_button(label= "Start Capture?")
    


dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
while dpg.is_dearpygui_running():
    # If we have just pressed start
    if scan_flags[0]== True and scan_flags[1]== False:
        open_scan_input_window()
        scan_flags[1]= True

    # After we have pressed start 
    elif scan_flags[0] == True and scan_flags[1]== True:
        ret, frame= vid.read()
        if ret:
            #From BGR to RGBA
            data = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            # Turns data 1-D
            data_ravel= data.ravel()
            # numpy float array
            data_float= np.asfarray(data_ravel, dtype='f')
            # Normalize data
            texture_data= np.true_divide(data_float,255)

            # Will run normally
            if scan_flags[2]== False:
                dpg.set_value('texture_tag',texture_data)

            # Take a snapshot of the camera input at this exact moment
            elif scan_flags[2]== True:
                # This will be used to save the image
                image_to_save_data= frame 
                # Update ScreenGrab with the latest photo
                dpg.set_value('ScreenGrab',texture_data)
                scan_flags[2]=False
            


        
    
    dpg.render_dearpygui_frame()

dpg.destroy_context()



'''
Quantities,PartID
3,34165
10,2420
2,10021
1,20003
2,10011
1,10001
2,10003
1,10024
2,10000
1,10032
3,10009

'''