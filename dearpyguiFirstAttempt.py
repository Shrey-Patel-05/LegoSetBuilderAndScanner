
'''


import dearpygui.dearpygui as dpg

dpg.create_context()

width, height, channels, data = dpg.load_image("Images/Segmented_Images/Contours_Individual/contour_5_centered.png")

with dpg.texture_registry(show=True):
    texture_id = dpg.add_dynamic_texture(width=width, height=height, default_value=data)

with dpg.window(label="Tutorial"):
    dpg.add_image(texture_id)
    width, height, channels, data = dpg.load_image("Images/Segmented_Images/Contours_Individual/contour_1_centered.png")
    dpg.configure_item(texture_id, default_value=data)
    
    dpg.add_image(texture_id)


dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()




import dearpygui.dearpygui as dpg
import cv2
import numpy as np

# Create a context
dpg.create_context()

# Open the video capture
vid = cv2.VideoCapture(0)

# Set up the frame size
frame_width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
frame_height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
video_fps = vid.get(cv2.CAP_PROP_FPS)

# Dummy data for the texture registry
texture_data = np.zeros((int(frame_height), int(frame_width), 4), dtype=np.float32)

# Function to capture and save snapshot
def capture_and_save_snapshot():
    # Capture the current frame
    ret, frame = vid.read()
    if ret:
        # From BGR to RGBA
        data = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        # Normalize data
        texture_data[:] = np.true_divide(data, 255)

        # Save the snapshot
        file_path = dpg.get_value("Filepath")
        if file_path:
            cv2.imwrite(file_path, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            print(f"Snapshot saved to: {file_path}")
        else:
            print("Please enter a valid file path.")


# Set up the texture registry
with dpg.texture_registry():
    dpg.add_raw_texture(width=int(frame_width), height=int(frame_height), default_value=texture_data,
                        format=dpg.mvFormat_Float_rgba, tag='texture_tag')

# Add a button to trigger the snapshot capture
# Explicitly set the parent to the viewport
with dpg.window(label= 'hello'):
    dpg.add_image('texture_tag')
    dpg.add_button(label="Capture Snapshot", callback=lambda sender, app_data: capture_and_save_snapshot(), parent="Custom Title")
    # Add an input text for file path
    dpg.add_input_text(tag="Filepath", default_value="Images/Scanned_images/parts_image.png")


# Create a viewport
dpg.create_viewport(title='Custom Title', width=int(frame_width), height=int(frame_height))

# Show the viewport
dpg.setup_dearpygui()
dpg.show_viewport()

while dpg.is_dearpygui_running():
    ret, frame = vid.read()
    if ret:
        # From BGR to RGBA
        data = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        # Normalize data
        texture_data[:] = np.true_divide(data, 255)

        # Update the texture data
        dpg.set_value('texture_tag', texture_data)

    dpg.render_dearpygui_frame()

# Release resources
vid.release()
dpg.destroy_context()

'''

'''
import dearpygui.dearpygui as dpg

dpg.create_context()

with dpg.window(label="Tutorial", pos=(20, 50), width=275, height=225) as win1:
    t1 = dpg.add_input_text(default_value="some text")
    t2 = dpg.add_input_text(default_value="some text")
    with dpg.child_window(height=100):
        t3 = dpg.add_input_text(default_value="some text")
        dpg.add_input_int()
    dpg.add_input_text(default_value="some text")

with dpg.window(label="Tutorial", pos=(320, 50), width=275, height=225) as win2:
    dpg.add_input_text(default_value="some text")
    dpg.add_input_int()

with dpg.theme() as global_theme:

    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_Button,  (255, 163, 26), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Border,  (255, 163, 26), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive,  (37, 37, 38), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg,  (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text,  (255, 255, 255), category=dpg.mvThemeCat_Core)
        #dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

    with dpg.theme_component(dpg.mvInputInt):
        dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (140, 255, 23), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)

dpg.bind_theme(global_theme)

dpg.show_style_editor()

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()



import dearpygui.dearpygui as dpg
import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
dpg.create_context()


# add a font registry
with dpg.font_registry():
    # first argument ids the path to the .ttf or .otf file
    default_font = dpg.add_font("/System/Library/Fonts/Supplemental/Rockwell.ttc", 12)
    second_font = dpg.add_font("/Users/shrey/Downloads/GlossySheenRegular-L35oy.ttf", 12)


with dpg.window(label="Font Example", height=200, width=200):
    dpg.add_input_text(label="", hint="Enter Part ID Here")
    dpg.add_input_int(label="Quantity")
    dpg.add_button(label="Add To Inventory")
    b2 = dpg.add_button(label="Secondary font")
    dpg.add_button(label="default")

    # set font of specific widget
    dpg.bind_font(default_font)
    dpg.bind_item_font(b2, second_font)






dpg.show_font_manager()

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()


#dpg.show_style_editor()

'''