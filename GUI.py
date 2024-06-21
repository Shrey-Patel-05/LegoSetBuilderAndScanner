import dearpygui.dearpygui as dpg
import pandas as pd
import os 
import numpy as np
# To open up web links for instructions
import webbrowser
# To deepcopy arrays with nested structures
import copy
# Convert strings in csv to arrays
import ast
# To use my AI model
import tensorflow as tf
# For video input
import cv2
from ClassandGlobalVariabledefinitions import *
from OptimizeScript import *
from Segment_Images import *

import os
os.environ['OPENCV_AVFOUNDATION_SKIP_AUTH'] = '0'

dpg.create_context()



def SetWindowProperties(window_id):
    dpg.configure_item(window_id,width=1510, height=920,pos=(0, 24),no_move=False, no_close=True,no_collapse=True,no_resize=True)

    

def open_main_window():
    delete_all_other_open_windows()
    # Empty inventory stack in case it's not
    EmptyStack()
    with dpg.window(label="Main Menu", tag= "Main Menu"):
        SetWindowProperties("Main Menu")
        with dpg.group(tag= 'center'):
            dpg.add_image(logo_id)
            dpg.add_button(label="Inventory", callback=open_inventory_window)
            dpg.add_button(label="Build", callback=open_build_window)
            dpg.add_button(label="Options", callback=open_user_preferences_window)
        dpg.set_item_pos('center',[580,200])


def delete_all_other_open_windows():
    StopCapture()
    all_items = dpg.get_all_items()
    open_windows = []
    # get all items that are of type window
    for item in all_items:
        if dpg.get_item_info(item)["type"] == "mvAppItemType::mvWindowAppItem":
            open_windows.append(item)
    # then delete these windows
    for i in range(0,len(open_windows)):
        dpg.delete_item(open_windows[i])


def StartCapture():
    # Set start flag and get initial capture
    global scan_flags
    global vid
    vid= cv2.VideoCapture(0)
    scan_flags[0]= True

def StopCapture():
    # Set start flag
    global scan_flags
    global vid
    global current_image
    scan_flags[0]= False
    scan_flags[1]= False
    scan_flags[2]= False
    current_image =1
    # If we are actually capturing video, close the camera
    if vid is not None:
        vid.release()


def capture_snapshot():
    global scan_flags
    scan_flags[2]= True


def UseImage():
    global current_image

    # Save to different files depending on the type of photo
    if current_image==1:

        # Save snapshot as a backgorund image
        file_path = "Images/Scanned_images/Background.png"
        cv2.imwrite(file_path, cv2.cvtColor(image_to_save_data, cv2.COLOR_BGR2RGBA))

        # Increment counter and prepare to take the second photo
        current_image+=1

        # Delete the previous window
        dpg.delete_item('Scan Bricks_1')

        # Reset placeholder data for snapshots
        dpg.set_value('ScreenGrab',eastbound_data)
        open_scan_input_window()

    elif current_image ==2:

        # Save snapshot as a foreground image (one with parts)
        file_path= "Images/Scanned_images/Foreground.png"
        cv2.imwrite(file_path, cv2.cvtColor(image_to_save_data, cv2.COLOR_BGR2RGBA))

        # Reset placeholder data for snapshots
        dpg.set_value('ScreenGrab',eastbound_data)

        # Move onto identification window
        open_brick_identification_window()




def open_brick_identification_window():

    delete_all_other_open_windows()

    ExtractPartsFromImage()

    # Delete all files currently in inventory  (from stack overflow)
    os.remove("Images/Scanned_images/Foreground.png")
    os.remove("Images/Scanned_images/Background.png")

    with dpg.window(label= 'Identification', tag= 'Identification'): #no_move=True,no_resize=Tru
        SetWindowProperties('Identification')

        with dpg.texture_registry():
            # Load the image with parts outlined
            ____, ____, ____, segmented_image_data = dpg.load_image('Images/Segmented_Images/Contours_Whole/Camera_View.png')
            # Clear images for next time
            [f.unlink() for f in Path("Images/Segmented_Images/Contours_Whole/").glob("*") if f.is_file()]
            dpg.add_raw_texture(width=1920, height=1080, default_value=segmented_image_data, format=dpg.mvFormat_Float_rgba, tag="Camera_View")

        with dpg.group(horizontal=True, tag= 'center'):

            # The user's image is displayed with all the parts outlined
            with dpg.group(label= 'Camera View'):
                dpg.add_text("Camera View")
                dpg.add_image("Camera_View", width= output_width, height= output_height)

            with dpg.group(label= 'Identified'):
                dpg.add_text("Identified")
                
                # Uses the CNN model to get predictions
                PredictionList= GetPredictions()
                
                # For each prediction
                for i in range(0,len(PredictionList)):
                   
                    # add a new texture for each part
                    with dpg.texture_registry():
                        current_tag= 'part'+str(i)
                        ____, ____, ____, part_image_data = dpg.load_image(PredictionList[i][0])
                        dpg.add_raw_texture(width=128, height=128, default_value=part_image_data, format=dpg.mvFormat_Float_rgba, tag=current_tag)
                    
                    # Show the predictions and the extracted part side-by-side
                    with dpg.group(horizontal= True):                 
                        dpg.add_image(current_tag, width= 120, height= 80)
                        dpg.add_text(PredictionList[i][1])

                # Clear images for next time
                [f.unlink() for f in Path("Images/Segmented_Images/Contours_Individual/").glob("*") if f.is_file()]  


            dpg.add_button(label="Next", callback=open_brick_verification_window, user_data=None)

        dpg.set_item_pos('center',[320,20])


def RemoveBrickScan(sender):
    ScanInventory,Part= dpg.get_item_user_data(sender)
    ScanInventory.Remove(Part)
    open_brick_verification_window(ScanInventory)


def finish_scan_steps(sender):
    ScanInventory= dpg.get_item_user_data(sender)

    #For all parts in the temporary inventory
    for parts in ScanInventory.GetListOfAllNodes():
        node= UserInventory.SearchForPartsInInventory(str(parts[0]))

        # If the brick is not already in inventory
        if node == None:
            UserInventory.Insert(parts[0],str(parts[1]))

        else:
            # If the brick is already in inventory, update its quantity
            UserInventory.ChangeQuantity(parts[0],int(parts[1]))

    open_view_inventory_window()


def SetQuantityBrickScan(sender):
     
     ScanInventory, Part,Original_Quantity= dpg.get_item_user_data(sender)

     # Work out difference between values 
     Quantity= dpg.get_value("input_int")-Original_Quantity

     # Only if user correction/ AI prediction is positive
     if dpg.get_value("input_int")>0:
        ScanInventory,___= ScanInventory.ChangeQuantity(Part,Quantity)

     open_brick_verification_window(ScanInventory)
     


def ChangeQuantityBrickScanWindow(sender):
    # Get parameters
    ScanInventory, Part, Quantity= dpg.get_item_user_data(sender)

    with dpg.window(label="Change Quantity", modal= True):

        # Allow user to change the quantity
        with dpg.group(horizontal=True):
            dpg.add_text(Part)
            dpg.add_input_int(tag= "input_int", default_value= int(Quantity), width=100)

        # dpg.get_value("input_int") is the new quantity , int(Quantity) is the original
        dpg.add_button(label= "Confirm", callback=SetQuantityBrickScan, user_data=[ScanInventory,Part,int(Quantity)])



def open_brick_verification_window(sender):

    # Check to see of sender is the refrence to Scaninventory or the actual scaninventory
    if sender.__class__.__name__ == 'Inventory':
        ScanInventory=sender
    else:
        ScanInventory=dpg.get_item_user_data(sender)
        if ScanInventory == None:
            ScanInventory= ReturnScanBricks()

    delete_all_other_open_windows()

    with dpg.window(label="Brick Verification",tag="Brick Verification"):
        SetWindowProperties("Brick Verification")
        
        values= ScanInventory.GetListOfAllNodes()

        with dpg.group(tag= 'center'):
            dpg.add_image(logo_id)
            dpg.set_item_pos(dpg.last_item(),[580,100])
            dpg.add_button(label="Confirm", callback=finish_scan_steps,user_data=ScanInventory)

            with dpg.table(header_row=True,row_background=True,borders_innerH=True, borders_outerH=True, borders_innerV=True,borders_outerV=True, width=1000):
                dpg.add_table_column(label= "Part ID")
                dpg.add_table_column(label= "Quantity")
                dpg.add_table_column(label= "Delete")

                # For all parts scanned
                for i in range(0, len(values)):
                    with dpg.table_row():
                        # PartID
                        dpg.add_text(values[i][0])
                        # Quantity 
                        dpg.add_button(label= values[i][1], callback=ChangeQuantityBrickScanWindow, user_data=[ScanInventory, values[i][0], values[i][1]] )
                        # Delete prediction
                        dpg.add_button(label= "Delete", callback= RemoveBrickScan, user_data=[ScanInventory, values[i][0]] )

        dpg.set_item_pos('center',[225,200])

        

def ReturnScanBricks():
        # Defines the temporary inventory
        ScanInventory= Inventory(50)

        # While there are predicted parts
        while InventoryStack.Peek() != None:

            # Get each predicted [PartID,Quantity]
            brick= InventoryStack.Peek()
            # Search for the part in inventory
            node= ScanInventory.SearchForPartsInInventory(brick[0])

            # If the brick is not already in inventory
            if node == None:
                ScanInventory.Insert(brick[0],str(brick[1]))
                InventoryStack.Pop()

            else:
                # If the brick is already in inventory, update its quantity
                ScanInventory.ChangeQuantity(brick[0],1)
                InventoryStack.Pop()

        return ScanInventory
        


def open_scan_input_window():

    with dpg.window(tag= 'Scan Bricks_' +str(current_image),label= 'Scan Bricks',width=720,height=1080):
        SetWindowProperties('Scan Bricks_' +str(current_image))

        dpg.add_button(label="Return", callback=open_add_inventory_window)

        with dpg.group(tag= 'center'):

            # First box is camera output
            dpg.add_text(f"Below is your camera output!")
            with dpg.group(horizontal=True):
                dpg.add_image('texture_tag',width=output_width,height=output_height)
                dpg.add_button(label='Say Cheese!', callback=capture_snapshot)

            if current_image==1:
                dpg.add_text(f"Below is the background image")
            elif current_image ==2:
                dpg.add_text(f"Below is the image of your Parts")

            # Second box is camera snapshots
            with dpg.group(horizontal=True):
                dpg.add_image('ScreenGrab',width=output_width,height=output_height)
                dpg.add_button(label= "Use This Image?", callback=UseImage)
        dpg.set_item_pos('center',[440,20])


def open_scan_inventory_window():
    delete_all_other_open_windows()
    StartCapture()


def open_type_inventory_window():

    delete_all_other_open_windows()
    with dpg.window(label="Type Inventory",tag="Type Inventory"):
        SetWindowProperties("Type Inventory")

        with dpg.group(tag= 'center'):

            dpg.add_image(logo_id)

            # Input field(s)
            with dpg.group(horizontal=True):
                    dpg.add_text("Part ID:")
                    dpg.add_input_text(tag= "PartID_Input",hint="Enter Here", width= 100)
                    dpg.add_text("Quantity:")
                    dpg.add_input_int(tag= "Quantity_Input", width= 100)  

            dpg.add_button(label="Add Part", callback=AddToStack)
            dpg.add_button(label="Redo Add Part", callback=remove_from_inventory_stack_window)
            dpg.add_button(label="Exit", callback=open_add_inventory_window)

        dpg.set_item_pos('center',[580,200])
    

def open_add_inventory_window():

    delete_all_other_open_windows()
    # Empty inventory stack in case it's not
    EmptyStack()    
    
    with dpg.window(label="Type or Scan?", tag="Type or Scan?"):
        SetWindowProperties("Type or Scan?")

        with dpg.group(tag= 'center'):
            dpg.add_image(logo_id)
            dpg.add_button(label="Scan", callback=open_scan_inventory_window)
            dpg.add_button(label="Type", callback=open_type_inventory_window)
            dpg.add_button(label="Exit", callback=open_inventory_window)
        dpg.set_item_pos('center',[580,200])

def open_inventory_window():
    delete_all_other_open_windows()
    # Empty inventory stack in case it's not
    EmptyStack()
    with dpg.window(label="Inventory", tag="Inventory"):
        SetWindowProperties("Inventory")
        with dpg.group(tag= 'center'):
            dpg.add_image(logo_id)
            dpg.add_button(label="View", callback=open_view_inventory_window)
            dpg.add_button(label="Add Parts", callback=open_add_inventory_window)
            dpg.add_button(label="Exit", callback=open_main_window)
    dpg.set_item_pos('center',[580,200])


def open_save_inventory_window():
    with dpg.window(modal=True):
        SaveInventory()
        dpg.add_text('Inventory is saved')


def open_view_inventory_window():
     delete_all_other_open_windows()
     # Empty inventory stack in case it's not
     EmptyStack()

     values= UserInventory.GetListOfAllNodes()

     with dpg.window(label="View Inventory",tag="View Inventory"):
        SetWindowProperties("View Inventory")
        with dpg.group(tag= 'center'):
            dpg.add_image(logo_id)
            dpg.set_item_pos(dpg.last_item(),[580,100])
            with dpg.group(horizontal=True):
                dpg.add_button(label="Exit", callback=open_inventory_window)
                dpg.add_button(label= "Edit Inventory", callback=open_edit_inventory_window)
                dpg.add_button(label= 'Save Inventory', callback=open_save_inventory_window)

            with dpg.table(header_row=True,row_background=True, borders_innerH=True, borders_outerH=True, borders_innerV=True,  borders_outerV=True, width=1000):
                dpg.add_table_column(label= "Part ID")
                dpg.add_table_column(label= "Quantity")

                # Add partID and quantities of inventory
                for i in range(0, len(values)):
                    with dpg.table_row():
                        for j in range(0, 2):
                            dpg.add_text(values[i][j])
             
        dpg.set_item_pos('center',[225,200])

def open_edit_inventory_window():    
     delete_all_other_open_windows()
     # Empty inventory stack in case it's not
     EmptyStack()
     with dpg.window(label="Edit Inventory",tag="Edit Inventory"):
        SetWindowProperties("Edit Inventory")
        with dpg.group(tag= 'center'):
            dpg.add_image(logo_id)
            dpg.add_button(label="View", callback=open_view_inventory_window)
            dpg.add_button(label="Add Parts", callback=open_add_inventory_window)
            dpg.add_button(label="Delete Parts", callback=open_delete_inventory_window)
            dpg.add_button(label="Return", callback=open_view_inventory_window)
        dpg.set_item_pos('center',[580,200])

def open_delete_inventory_window():
     delete_all_other_open_windows()
     # Empty inventory stack in case it's not
     EmptyStack()
     with dpg.window(label="Delete Parts",tag="Delete Parts"):
        SetWindowProperties("Delete Parts")    
        with dpg.group(tag= 'center'):
            dpg.add_image(logo_id)
            dpg.add_input_text(tag= "PartID_To_Delete",hint="Enter Here", width= 100)
            dpg.add_button(label="Delete Part", callback=DeletePartGUI)
            dpg.add_button(label="Return", callback=open_edit_inventory_window)
        dpg.set_item_pos('center',[580,200])


def DeletePartGUI():
    with dpg.window(label="Part Removed", modal= True, pos=[580,200]):
        PartID_To_Delete_Value= dpg.get_value("PartID_To_Delete")
        if UserInventory.SearchForPartsInInventory(PartID_To_Delete_Value) != None:
            UserInventory.Remove(PartID_To_Delete_Value)
            dpg.add_text(f"Part {PartID_To_Delete_Value} has been removed from Inventory")
        else:
            dpg.add_text(f"Part {PartID_To_Delete_Value} not in Inventory")
        
    

def AddToStack():

    # Get the part values
    part_id_value = dpg.get_value("PartID_Input")
    quantity_value = dpg.get_value("Quantity_Input")
    if quantity_value <1:
        return
    # Create a message for the popup
    popup_message = f"{quantity_value} of Part {part_id_value} has been added"

    # Add to the stack
    stack_item = [part_id_value, quantity_value]
    InventoryStack.Push(stack_item)

    # Clear values (for future use)
    dpg.set_value("PartID_Input","")
    dpg.set_value("Quantity_Input",0)

    with dpg.window(label='Part Added!', modal= True, pos=[580,200]):
        dpg.add_text(popup_message)



def remove_from_inventory_stack_window():
    part= InventoryStack.Peek()
    # If user has actually typed parts
    if part != None:
        with dpg.window(label='Remove Part?',tag= 'Center',modal=True):
            # Make sure the user does not accidentally undo their actions
            with dpg.group(horizontal=True):
                dpg.add_text("Are you sure you want to remove " + str(part[1])+ " of  part "+ str(part[0]) + " ?")
                dpg.add_button(label= "Yes", callback= RemoveFromInventoryStack)
                dpg.add_button(label= "No", callback= open_type_inventory_window)
        dpg.set_item_pos('Center', [580,200])


def RemoveFromInventoryStack():
    InventoryStack.Pop()
    open_type_inventory_window()

def EmptyStack():

    while InventoryStack.Peek() != None:

        brick= InventoryStack.Peek()
        # Search for the brick in inventory
        node= UserInventory.SearchForPartsInInventory(brick[0])

        # If the brick is not already in inventory
        if node == None:
            UserInventory.Insert(brick[0],str(brick[1]))
            InventoryStack.Pop()
        else:
            # If the brick is already in inventory, update its quantity
            UserInventory.ChangeQuantity(brick[0],int(brick[1]))
            InventoryStack.Pop()




def GetPredictions():

    label_dictionary =   {0: '14719', 1: '15672', 2: '18654', 3: '2357',4: '2420',5: '2780',6: '27925',7: '3001', 8: '3002',9: '3003', 10: '3004',11: '3005',12: '3010',13: '3020', 14: '3021',15: '3022',16: '3023',17: '3024',18: '3037',19: '3038',20: '3039',21: '3040',22: '3045',23: '3046',24: '3062',25: '3063',26: '3068',27: '3069',28: '3070',29: '3298',30: '33909',31: '3622',32: '3623',33: '3659',34: '3675',35: '3700',36: '3794',37: '4150',38: '41677',39: '41678',40: '4274',41: '4286', 42: '43093',43: '43857',44: '4490',45: '54200',46: '6143',47: '6632',48: '85984',49: '99301'}
    
    loaded_model = tf.keras.models.load_model('CNN_Model')
    
    # Will store the predictions and image they relate to
    image_prediction=[]

    # Get the number of extracted parts
    num_of_parts = len([f for f in os.listdir('Images/Segmented_Images/Contours_Individual/')])

    for i in range(1, num_of_parts+1):

        file_path= 'Images/Segmented_Images/Contours_Individual/contour_'+str(i)+'_centered.png'

        segmented_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

        # Resize the image if needed
        segmented_image = cv2.resize(segmented_image, (128, 128))

        # Convert the image to a format suitable for predictions
        segmented_image_array = tf.keras.utils.img_to_array(segmented_image)

        # Returns the predction (but not as a part ID)
        number_result= loaded_model.predict(np.expand_dims(segmented_image_array, axis=0))

        # Convert the prediction to a partID
        result= np.argmax(number_result)
        result= label_dictionary.get(result)

        InventoryStack.Push([result,1])

        image_prediction.append([file_path,result])

    return image_prediction





#################################################################################################################################################
###################### Build widgets ############################################################################################################
#################################################################################################################################################



def open_build_window():
    delete_all_other_open_windows()
    # Empty inventory stack in case it's not
    EmptyStack()

    with dpg.window(label="Build", tag="Build"):
        SetWindowProperties("Build")

        with dpg.group(tag= 'center'):
            dpg.add_image(logo_id)
            dpg.add_button(label="Build a MOC", callback=open_set_view_window, user_data='MOC SETS')
            dpg.add_button(label="Build an Official Lego Set", callback=open_set_view_window, user_data='OFFICIAL SETS')
            dpg.add_button(label="My Builds", callback=open_my_saved_sets)
            dpg.add_button(label="Return", callback=open_main_window)  
        dpg.set_item_pos('center',[580,200])




def open_set_view_window(sender):
     type_of_set = dpg.get_item_user_data(sender)

     if type_of_set:
        delete_all_other_open_windows()
        # Empty inventory stack in case it's not
        EmptyStack()

        with dpg.window(label=type_of_set, tag=type_of_set):
            SetWindowProperties(type_of_set)

            dpg.add_button(label="Return", callback=open_build_window) 

            with dpg.table(header_row=True,row_background=True,   borders_innerH=True, borders_outerH=True, borders_innerV=True,  borders_outerV=True,width=1000):
                dpg.add_table_column(label= "Set Name")
                dpg.add_table_column(label= "Percentage of set you can build")

                # Find the parts the user has, and the parts the user does not
                if type_of_set== "MOC SETS":
                    SetList= SearchForPartsInSets(MOCdf,'MOC')
                else:
                    SetList= SearchForPartsInSets(OFFICIALdf,'OFFICIAL')

                # Sort sets by PValue descending
                SetList= MergeSort(SetList)
                
                for i in range(0, len(SetList)):
                    with dpg.table_row():
                        # Set Name
                        dpg.add_button(label=SetList[i].Name, callback=open_set_information_window, user_data=[SetList[i],type_of_set])
                        # The percenatge of the parts the user has
                        dpg.add_text(str(int((1 - SetList[i].PValue) * 100)) + '%')
                
    
def open_browser(sender):
    url = dpg.get_item_user_data(sender)
    webbrowser.open(url)


def open_set_information_window(sender):
     
     current_set,type_of_set = dpg.get_item_user_data(sender)

     # If set exists...
     if current_set:
        delete_all_other_open_windows()
        EmptyStack()

        # Set total and costs
        current_set.SetTotal()
        current_set.SetCost()

        with dpg.window(label="View More",tag="View More"):
            SetWindowProperties("View More")
            dpg.add_button(label='Save Set?', callback=SaveSet,user_data=[current_set,[],type_of_set])
            dpg.add_text(current_set.Name)

            with dpg.group(horizontal=True):
                dpg.add_text("Total Parts Required: "+ str(current_set.Total_Needed))
                dpg.add_text("Cost to build: " + str(current_set.Cost))

            dpg.add_text('Parts Possessed')
            with dpg.collapsing_header(label= "Parts Possessed"):               
                    DisplayPartsListsTables(current_set.PartsPossessed)

            dpg.add_text('Parts Required')
            with dpg.collapsing_header(label= "Parts Required"):   
                    DisplayPartsListsTables(current_set.PartsRequired)

            dpg.add_button(label="Instructions (@ Rebrickable.com)", callback=open_browser, user_data=current_set.SetURL)
            dpg.add_button(label= "Optimize?", callback=OptimizeSet, user_data=[current_set,type_of_set])
            dpg.add_button(label="Return", callback=open_set_view_window,user_data=type_of_set) 


def SaveSet(sender):
    current_set,substitutions, type_of_set= dpg.get_item_user_data(sender)
    # Read the CSV file into a DataFrame
    csv_path = "CSV's/SavedSets.csv"
    df = pd.read_csv(csv_path)

    # Remove any old versions of the set
    for names in df['Set Name']:
        if names == current_set.Name:
            df = df[df['Set Name'] != names]
            break

    # Define the new row
    new_row= {'Set Type':type_of_set ,'Set Name':current_set.Name, 'Set URL': current_set.SetURL,'Total Needed': current_set.Total_Needed,'Cost': current_set.Cost, 'PValue': current_set.PValue ,'Parts Possessed':current_set.PartsPossessed,'Parts Required':current_set.PartsRequired,'Substitutions':substitutions}
    # Combine to existing dataframe
    new_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_df], ignore_index=True)

    # Save dataframe
    df.to_csv("CSV's/SavedSets.csv", index=False, encoding='utf-8')

def open_my_saved_sets():
    delete_all_other_open_windows()
    EmptyStack()

    with dpg.window(label="My Sets",tag="My Sets"):
        SetWindowProperties("My Sets")
        dpg.add_button(label="Return", callback=open_build_window) 
        df= pd.read_csv("CSV's/SavedSets.csv")

        columns= list(df.columns)
        columns.append('Delete?')
        with dpg.table(header_row=True,row_background=True, borders_innerH=True, borders_outerH=True, borders_innerV=True, borders_outerV=True,width=1000):
                    
            for m in range(0,len(columns)):
                dpg.add_table_column(label= columns[m])

            # add_table_next_column will jump to the next row once it reaches the end of the columns
            for i in range(0, len(df)):
                with dpg.table_row():
                    for k in range(0,len(columns)):
                        match k:
                            case 0|1|3|4|5:
                                dpg.add_button(label=list(df.iloc[i])[k], callback=view_my_saved_sets_attributes, user_data=[columns[k],list(df.iloc[i])[k]])
                            
                            # Often too large to be dislayed in the table directly
                            case 2|6|7|8:
                                dpg.add_button(label='Click To View', callback=view_my_saved_sets_attributes, user_data=[columns[k],list(df.iloc[i])[k]])
                            
                            case 9:
                                dpg.add_button(label='DELETE', callback=delete_saved_set, user_data=[list(df.iloc[i])[1]])
                            


def delete_saved_set(sender):
    # Access the name and present in correct format
    name =dpg.get_item_user_data(sender)[0]
    
    # Load the csv as a dataframe
    csv_path = "CSV's/SavedSets.csv"
    df = pd.read_csv(csv_path)

    # Remove the set
    for names in df['Set Name']:
        if names == name:
            df = df[df['Set Name'] != name]
            break

    df.to_csv("CSV's/SavedSets.csv", index=False, encoding='utf-8')
    open_my_saved_sets()


def view_my_saved_sets_attributes(sender):
    column, information= dpg.get_item_user_data(sender)
    with dpg.window(label= column,tag= column,modal=True,no_close=True):
        
        if column== 'Set URL':
            dpg.add_button(label="Instructions (@ Rebrickable.com)", callback=open_browser, user_data=information)

        # Use Abstract Syntax Trees to represent the strings as arrays
        elif column== 'Parts Possessed' or column== 'Parts Required':
            DisplayPartsListsTables(ast.literal_eval(information))
        elif column == 'Substitutions':
            open_substiutions_table(ast.literal_eval(information))
        else:
            dpg.add_text(information)

        dpg.add_button(label="Close", callback=open_my_saved_sets) 
       


def DisplayPartsListsTables(current_set_list):
    if current_set_list != []:
        with dpg.table(header_row=True,row_background=True, borders_innerH=True, borders_outerH=True, borders_innerV=True,  borders_outerV=True,width=1000):
            dpg.add_table_column(label= "Part ID")
            dpg.add_table_column(label= "Dimensions")
            dpg.add_table_column(label= "Quantity")
            # add_table_next_column will jump to the next row once it reaches the end of the columns
            for m in range(0, len(current_set_list)):
                with dpg.table_row():
                        dpg.add_text(current_set_list[m][0])
                        # Add dimensions (if possible)
                        dimension=  PartIDDimensionTable.Search(current_set_list[m][0]).value if PartIDDimensionTable.Search(current_set_list[m][0]) is not None else 'N/A'
                        if dimension== None:
                            dpg.add_text('N/A')
                        else:  
                            dpg.add_text(dimension)
                        dpg.add_text(current_set_list[m][1])  


def open_set_information_after_optimize_window(current_set,type_of_set,partsSubstituted):
     
     if current_set:
        delete_all_other_open_windows()
        # Set total and costs
        current_set.SetTotal()
        current_set.SetCost()
        
        with dpg.window(label="View More",tag="View More"):
                SetWindowProperties("View More")
                dpg.add_button(label='Save Set', callback=SaveSet,user_data=[current_set,partsSubstituted,type_of_set] )
                dpg.add_text(current_set.Name)
                with dpg.group(horizontal=True):
                    dpg.add_text("Total Parts Required: "+ str(current_set.Total_Needed))
                    dpg.add_text("Cost to build: " + str(current_set.Cost))
                with dpg.collapsing_header(label= 'Parts Possessed'):               
                    DisplayPartsListsTables(current_set.PartsPossessed)
                with dpg.collapsing_header(label= 'Parts Required'):   
                    DisplayPartsListsTables(current_set.PartsRequired)
                with dpg.collapsing_header(label= 'Substitutions'):   
                    open_substiutions_table(partsSubstituted)
                dpg.add_button(label="Instructions (@ Rebrickable.com)", callback=open_browser, user_data=current_set.SetURL)
                dpg.add_button(label="Return", callback=open_set_view_window,user_data=type_of_set) 



def OptimizeSet(sender):
    # Fetch set and get key attributes
    Current_Set, type_of_set= dpg.get_item_user_data(sender)
    
    partsRequired=copy.deepcopy(Current_Set.PartsRequired)
    partsPossessed=copy.deepcopy(Current_Set.PartsPossessed)
    partsSubstituted=[]
    KeepInventory=UserInventory.Copy()
    for parts in partsPossessed:
        KeepInventory,__= KeepInventory.ChangeQuantity(parts[0],1)

    # We use the original list as refrence as we remove from partsRequired as the program runs
    for i in range(0,len(Current_Set.PartsRequired)):
    #for i, part in enumerate(list(partsRequired)):
        
        #Find the dimensions of the part required (and get them in the standard format)

        Target_Brick_NonMatrix = PartIDDimensionTable.Search(Current_Set.PartsRequired[i][0]).value if PartIDDimensionTable.Search(Current_Set.PartsRequired[i][0]) is not None else 'N/A'
        if Target_Brick_NonMatrix != 'N/A':
            Target_Brick=PartIDDimensionTable.DimensionsToMatrix(Target_Brick_NonMatrix)
        else:
            Target_Brick= None

        achieved_quantity=0
        unable= False
        
        while achieved_quantity < int(Current_Set.PartsRequired[i][1]) and unable == False:
            Result= False
            if Target_Brick != None:
                # Optimize a brick
                if len(Target_Brick) ==2:
                    ReturnInventory=KeepInventory.Copy()
                    Target_Brick= RearrangeDimensions(Target_Brick[0],Target_Brick[1])
                    if Target_Brick[0]<3:
                        Result,ReturnInventory= Optimize(Target_Brick, -1, ReturnInventory,DimensionPartIDTable,  Use_Plates, False,False)
                # Optimize a plate
                elif len(Target_Brick) ==3 and Target_Brick[2] == 1.3 and Use_Plates== True:
                    # We only need to modify first two dimensions
                    ReturnInventory=KeepInventory.Copy()
                    FirstTwo= RearrangeDimensions(Target_Brick[0],Target_Brick[1])
                    Target_Brick[0],Target_Brick[1]=FirstTwo[0],FirstTwo[1]
                    if Target_Brick[0]<3:
                        # The call this subroutine - which works on the 3rd dimensions in 1/3's
                        Result,ReturnInventory = PlateSubstitutions((Target_Brick[0],Target_Brick[1]),-1,ReturnInventory,DimensionPartIDTable,False,1)
                    
                # Succesful optimization
                if  Result == True:
                    # Return the discrepancies between the two inventories (ie the parts used in substitutions)
                    SubstituteWithList= GetSubstiutionList(ReturnInventory,KeepInventory, PartIDDimensionTable)
                    # We add the brick/dimensions we want to replace, and the substitutons in a list for future viewing
                    partsSubstituted.append([Current_Set.PartsRequired[i][0],Target_Brick_NonMatrix,SubstituteWithList])
                    # Add to our parts possessed now
                    partsPossessed= AddSubstitutionsToPartsPossessed(partsPossessed, SubstituteWithList)
                    # Reduce the qauntity of this part required
                    partsRequired[i][1]= str(int(partsRequired[i][1])-1)
                    achieved_quantity+=1
                    # 'Save' changes
                    KeepInventory= ReturnInventory.Copy()     
                else:
                    
                    unable= True
            else:
                unable = True
    
    # Remove any parts now fully found
    partsRequired= [arr for arr in partsRequired if arr[1] != '0']

    Current_Set.PartsRequired= copy.deepcopy(partsRequired)

    
    for parts in partsPossessed:

        # Map first elements of each part/quantity array to a new list
        partsPossesedFirstElements= [arr[0] for arr in Current_Set.PartsPossessed]

        # Add the parts we need to use for substitutions
        if parts[0] in partsPossesedFirstElements:
            Current_Set.PartsPossessed[partsPossesedFirstElements.index(parts[0])][1]=  str(int(Current_Set.PartsPossessed[partsPossesedFirstElements.index(parts[0])][1]) + int(parts[1]))
        else:
            Current_Set.PartsPossessed.append(parts)
    
    open_set_information_after_optimize_window(Current_Set,type_of_set,partsSubstituted)


def open_substiutions_table(partsSubstituted):

    for i in range(0,len(partsSubstituted)):
        dpg.add_text(f"We can substitute one of {partsSubstituted[i][0]} - a {partsSubstituted[i][1]} -  with ...")  
        with dpg.table(header_row=True,row_background=True, borders_innerH=True, borders_outerH=True, borders_innerV=True,  borders_outerV=True,width=1000):
                dpg.add_table_column(label= "Part ID")
                dpg.add_table_column(label= "Dimensions")
                dpg.add_table_column(label= "Quantity")

                for m in range(0, len(partsSubstituted[i][2])):
                    with dpg.table_row():
                        for n in range(0,3):
                            dpg.add_text(partsSubstituted[i][2][m][n])     
    

def AddSubstitutionsToPartsPossessed(partsPossessed, SubstituteWithList):
    for substitutions in SubstituteWithList:
        # Get each element into the correct format (dimensions not needed)
        add_part_quantity= [substitutions[0],substitutions[2]]
        partsPossessed.append(add_part_quantity)
    return partsPossessed

            

##############################################################################################################################################################################################
###################################### User Options ##########################################################################################################################################
##############################################################################################################################################################################################


def open_user_preferences_window():
    delete_all_other_open_windows()
    # Empty inventory stack in case it's not
    EmptyStack()
    with dpg.window(label='User Preferences',tag='User Preferences'):
        SetWindowProperties('User Preferences')
        with dpg.group(tag= 'center'):
            dpg.add_image(logo_id)

            # Toggle between using and not using plates in Optimization
            with dpg.group(horizontal=True):
                    dpg.add_text('Use Plates in Optimization')
                    dpg.add_checkbox(default_value=Use_Plates,callback=lambda: globals().update(Use_Plates=not Use_Plates))

            # Set color theming
            dpg.add_text()
            text_theme= dpg.add_color_picker(label="Pick Text Color",width=100, height=100, no_alpha=True, no_inputs=True,no_small_preview=True, no_tooltip=True, default_value=(255,255,255))     
            button_theme= dpg.add_color_picker(label="Pick Button Color",width=100, height=100, no_alpha=True, no_inputs=True,no_small_preview=True, no_tooltip=True, default_value=(255, 163, 26))
            title_theme= dpg.add_color_picker(label="Pick Title Color",width=100, height=100, no_alpha=True, no_inputs=True,no_small_preview=True, no_tooltip=True, default_value=(37, 37, 38))        
            background_theme= dpg.add_color_picker(label="Pick Background Color",width=100, height=100, no_alpha=True, no_inputs=True,no_small_preview=True, no_tooltip=True, default_value=(0,0,0))
            border_theme= dpg.add_color_picker(label="Pick Border Color",width=100, height=100, no_alpha=True, no_inputs=True,no_small_preview=True, no_tooltip=True,default_value= (255, 163, 26) )    
            with dpg.group(horizontal=True):#,pos= [150,480]):    
                dpg.add_button(label="Apply Change", callback= set_gui_colors,  user_data=[background_theme,border_theme,title_theme,text_theme,button_theme]) 
                dpg.add_button(label= "Restore Default", callback= restore_default_colors)
            dpg.add_text()
            dpg.add_button(label="Return", callback= open_main_window)

        dpg.set_item_pos('center',[580,200])

def set_gui_colors(sender):
    rgbA= dpg.get_item_user_data(sender)
    # Get color value in int array RGB form
    colors=[]
    for color in rgbA:
            color_item=[0,0,0]
            color_item[0],color_item[1], color_item[2],__= dpg.get_value(color)
            color_item= [int(color_item) for color_item in color_item]
            colors.append(color_item)

    # new color data
    color_data = {dpg.mvThemeCol_Button: colors[4], dpg.mvThemeCol_TitleBgActive: colors[2],dpg.mvThemeCol_Border: colors[1], dpg.mvThemeCol_WindowBg: colors[0], dpg.mvThemeCol_Text: colors[3]}

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
             # Apply color settings
            for key, value in color_data.items():
                dpg.add_theme_color(key, value, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5)
            dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.5)
    dpg.bind_theme(global_theme)


def restore_default_colors():
    # original color data
    color_data = {dpg.mvThemeCol_Button: (255, 163, 26), dpg.mvThemeCol_TitleBgActive: (37, 37, 38), dpg.mvThemeCol_Border: (255, 163, 26), dpg.mvThemeCol_WindowBg: (0, 0, 0), dpg.mvThemeCol_Text: (255, 255, 255)}
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):

             # apply default settings
            for key, value in color_data.items():
                dpg.add_theme_color(key, value, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5)
            dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.5)
    dpg.bind_theme(global_theme)



with dpg.theme() as global_theme:
    with dpg.theme_component(dpg.mvAll):
        
        dpg.add_theme_color(dpg.mvThemeCol_Button,  (255, 163, 26), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,  (37, 37, 38), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border,  (255, 163, 26), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg,  (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text,  (255, 255, 255), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5)
        dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.5)

dpg.bind_theme(global_theme)




    

with dpg.font_registry():
    # first argument ids the path to the .ttf or .otf file
    default_font = dpg.add_font("Arial Black.ttf", 18)
# set font of specific widget
dpg.bind_font(default_font)






################### FROM DEARPYGUI DOCUMENTATION - creating dummy data for the texture registry##################
texture_data = []
for i in range(0, 100 * 100):
    texture_data.append(0)
    texture_data.append(0)
    texture_data.append(0)
    texture_data.append(0)
dummy_values= texture_data[:]
###################################################################################################################


with dpg.texture_registry():
    width, height, channels, data = dpg.load_image('Images/Logos/logo.png')
    logo_id = dpg.add_static_texture(width, height, data)
    dpg.add_raw_texture(width= 1920, height=1080,default_value=texture_data, format= dpg.mvFormat_Float_rgba,tag= 'texture_tag')
    ___, ___, channels, eastbound_data = dpg.load_image("Images/Logos/EastboundAndDown.jpg")
    dpg.add_raw_texture(width=1920, height=1080, default_value=eastbound_data, format=dpg.mvFormat_Float_rgba, tag="ScreenGrab")


with dpg.window(label="Main Menu",width=1510, height=920,pos=(0, 24),no_move=True, no_close=True,no_collapse=True,no_resize=True):
    LoadInventory()
    with dpg.group(tag= 'center'):
        dpg.add_image(logo_id)
        dpg.add_button(label="Inventory", callback=open_inventory_window)
        dpg.add_button(label="Build", callback=open_build_window)
        dpg.add_button(label="Options", callback=open_user_preferences_window)
    dpg.set_item_pos('center',[580,200])


with dpg.viewport_menu_bar():
    with dpg.menu(label="Main Menu"):
        dpg.add_menu_item(label="Inventory", callback=open_inventory_window)
        dpg.add_menu_item(label="Build", callback=open_build_window)
        dpg.add_menu_item(label="Settings", callback=open_user_preferences_window)
    
    with dpg.menu(label="Inventory"):
        dpg.add_menu_item(label="View", callback=open_view_inventory_window)
        dpg.add_menu_item(label="Add parts", callback=open_add_inventory_window)

    with dpg.menu(label="Build"):
        dpg.add_menu_item(label="Build a MOC", callback= open_set_view_window,user_data='MOC')
        dpg.add_menu_item(label="Build an official LEGO set", callback= open_set_view_window,user_data='OFFICIAL')
        dpg.add_menu_item(label="My Sets", callback=open_my_saved_sets)
    dpg.add_menu_item(label="Settings", callback=open_user_preferences_window)


dpg.create_viewport(title='BrickedUp', width=1080, height=720)
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


