import cv2 as cv
import numpy as np
import os
from matplotlib import pyplot as plt
from PIL import ImageGrab
import pyautogui
import time
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

X_OFFSET = 320
Y_OFFSET = 74

TESSERACT_CONFIG = r'--oem 3 --psm 6'

execution_path = os.getcwd()

tree_img = cv.imread(os.path.join(execution_path , "assets/first_match.png"), cv.IMREAD_UNCHANGED)
tree_img_2 = cv.imread(os.path.join(execution_path , "assets/second_match.png"), cv.IMREAD_UNCHANGED)
tree_img_3 = cv.imread(os.path.join(execution_path , "assets/third_match.png"), cv.IMREAD_UNCHANGED)

gray_tree = cv.cvtColor(tree_img, cv.COLOR_BGR2GRAY)
gray_tree_2 = cv.cvtColor(tree_img_2, cv.COLOR_BGR2GRAY)
gray_tree_3 = cv.cvtColor(tree_img_3, cv.COLOR_BGR2GRAY)

threshold = .33

current_screen = 0
map_coordinates =[{
    "x": 885,
    "y": 1990
},
{
    "x": 1948,
    "y": 548
}]
client_size = {
    "height": 992,
    "width": 1280
}
methods = ['cv.TM_CCOEFF']
old_coordinates = [0,0]
old_coordinates_second_screen = [0,0]

def find_points():
    for meth in methods:
        h, w = tree_img.shape[:-1]
        world_img = pyautogui.screenshot(region=(X_OFFSET, Y_OFFSET, 1250, 938))
        world_img = cv.cvtColor(np.array(world_img), cv.COLOR_RGB2BGR)
        gray_world = cv.cvtColor(world_img, cv.COLOR_BGR2GRAY)
        res = cv.matchTemplate(gray_world, gray_tree, cv.TM_CCOEFF_NORMED)
        yloc, xloc = np.where(res >= threshold)
        print("Before second chance", len(yloc))
        if len(yloc) <= 0:
            print("No points found with tree_img_1")
            print("***SECOND CHANCE***")
            h, w = tree_img_2.shape[:-1]
            res = cv.matchTemplate(gray_world, gray_tree_2, cv.TM_CCOEFF_NORMED)
            yloc, xloc = np.where(res >= threshold)
            print("Here after second chance", len(yloc))
        if len(yloc) <= 0:
            print("No points found with tree_img_1 and tree_image_2")
            print("***THIRD CHANCE***")
            res = cv.matchTemplate(gray_world, gray_tree_3, cv.TM_CCOEFF_NORMED)
            yloc, xloc = np.where(res >= threshold)
            rellocate_character()
            world_img = pyautogui.screenshot(region=(X_OFFSET, Y_OFFSET, 1250, 938))
            world_img = cv.cvtColor(np.array(world_img), cv.COLOR_RGB2BGR)
            gray_world = cv.cvtColor(world_img, cv.COLOR_BGR2GRAY)
            res = cv.matchTemplate(gray_world, gray_tree, cv.TM_CCOEFF_NORMED)
            yloc, xloc = np.where(res >= threshold)
            print("After walking", len(yloc))
        if len(yloc) <= 0:
            print("FINISHED. NO POINTS FOUND")
            return {
                "x": 0,
                "y": 0
            }
        else:
            return click(xloc, yloc, w, h)

def click(xloc, yloc, w, h):
    if current_screen == 1:
        current_coordinates = old_coordinates
    else:
        current_coordinates = old_coordinates_second_screen
    index = 0
    if current_coordinates[0] == xloc[0] and current_coordinates[1] == yloc[0]:
        index = len(xloc) - 1
        pyautogui.hotkey('f1')
        print(xloc)
        print(xloc[index], yloc[index])
    mouse_x = xloc[index] + (w/2)
    mouse_y = yloc[index] + (h/2)
    current_coordinates[0] = xloc[index]
    current_coordinates[1] = yloc[index]
    print("Click to: ", mouse_x, mouse_y)
    pyautogui.dragTo(mouse_x + X_OFFSET, mouse_y + Y_OFFSET)
    pyautogui.hotkey('f1')
    pyautogui.mouseDown(); pyautogui.mouseUp()
    next_direction = {
        "x": 100 * (1 if mouse_x + X_OFFSET > (client_size['width']/2 + X_OFFSET) else -1),
        "y": 50 * (1 if mouse_y + Y_OFFSET > (client_size['height']/2 + Y_OFFSET) else -1)
    }
    print("Click relative to: ", next_direction['x'], next_direction['y'])
    return next_direction

def get_coordinates():
    pyautogui.hotkey('alt', 'm')
    coordinates_img = pyautogui.screenshot(region=(X_OFFSET + 1130, Y_OFFSET + 42, 70, 22))
    pyautogui.hotkey('alt', 'm')
    coordinates_img = cv.cvtColor(np.array(coordinates_img), cv.COLOR_RGB2BGR)
    text_coordinates = pytesseract.image_to_string(coordinates_img, config=TESSERACT_CONFIG)
    return {
        "x": int(text_coordinates.replace(" ", "").split(",")[0]),
        "y": int(text_coordinates.replace(" ", "").split(",")[1])
    }

def center_mouse():
    print("Moving mouse to: ", client_size['width']/2 + X_OFFSET, client_size['height']/2 + Y_OFFSET)
    pyautogui.dragTo(client_size['width']/2 + X_OFFSET, client_size['height']/2 + Y_OFFSET)

def target_reached():
    allowed_offset = {
        "x": 4,
        "y": 3
    }
    character_coordinates = get_coordinates()
    target_coordinates = map_coordinates[current_screen - 1]
    coordinates_reached = {
        "x": False,
        "y": False
    }
    print("Character coordinates: ", character_coordinates['x'], character_coordinates['y'])
    print("Target coordinates: ", target_coordinates['x'], target_coordinates['y'])
    allowed_x = [target_coordinates['x'] - allowed_offset['x'], target_coordinates['x'] + allowed_offset['x']]
    print(allowed_x)
    coordinates_reached['x'] = True if (character_coordinates['x'] >= (target_coordinates['x'] - allowed_offset['x']) and character_coordinates['x'] <= (target_coordinates['x'] + allowed_offset['x'])) else False
    coordinates_reached['y'] = True if character_coordinates['y'] >= (target_coordinates['y'] - allowed_offset['y']) and character_coordinates['y'] <= (target_coordinates['y'] + allowed_offset['y']) else False
    return coordinates_reached
    
def rellocate_character():
    character_coordinates = get_coordinates()
    target_coordinates = map_coordinates[current_screen - 1]
    current_target_reached = False
    mouse_offset = {
        "x": 120 * (1 if target_coordinates['x'] > character_coordinates['x'] else -1),
        "y": 80 * (1 if target_coordinates['y'] > character_coordinates['y'] else -1)
    }
    old_target_coordinates = {
        "x": 0,
        "y": 0
    }
    while not current_target_reached:
        try:
            center_mouse()
            character_coordinates = get_coordinates()
            target_coordinates_reached = target_reached()
            
            if character_coordinates['x'] == old_target_coordinates['x'] and character_coordinates['y'] == old_target_coordinates['y']:
                print("Same coordinates")
                if target_coordinates_reached['x']:
                    mouse_offset['y'] += 10 * (1 if target_coordinates['y'] > character_coordinates['y'] else -1)
                else:
                    mouse_offset['x'] += 15* (1 if target_coordinates['x'] > character_coordinates['x'] else -1)
            else:
                mouse_offset = {
                    "x": 120 * (1 if target_coordinates['x'] > character_coordinates['x'] else -1),
                    "y": 80 * (1 if target_coordinates['y'] > character_coordinates['y'] else -1)
                }
            print(target_coordinates_reached)
            if target_coordinates_reached['x'] and target_coordinates_reached['y']:
                print("All true")
                current_target_reached = True
            elif target_coordinates_reached['x']:
                print("X TRUE")
                pyautogui.moveRel(0, mouse_offset['y'])
                pyautogui.mouseDown(); pyautogui.mouseUp()
            else:
                print("NOTHING TRUE")
                pyautogui.moveRel(mouse_offset['x'], 0)
                pyautogui.mouseDown(); pyautogui.mouseUp()
            old_target_coordinates = character_coordinates
        except:
            print("An error ocurred while rellocating character")

def print_all_rectangles(xloc, yloc, cv, world_img):
    if len(yloc) > 0:
        for(x, y) in zip(xloc, yloc):
            print(x,y)
            cv.rectangle(world_img, (x,y), (x + w, y + h), (0, 255, 255), 2)
        cv.imshow('World', world_img)
        cv.waitKey()
        cv.destroyAllWindows()

def print_grouped_rectangles(xloc, yloc, cv, world_img, w, h):
    rectangles = []
    for(x, y) in zip(xloc, yloc):
        rectangles.append([int (x), int(y), int(w), int(h)])
        rectangles.append([int (x), int(y), int(w), int(h)])
    rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)
    for(x, y, w, h) in rectangles:
        print(x,y)
        cv.rectangle(world_img, (x,y), (x + w, y + h), (0, 255, 255), 2)
    cv.imshow('World', world_img)
    cv.waitKey()
    cv.destroyAllWindows()


def get_graphic(res, method, cv, img, meth):
    min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv.rectangle(img,top_left, bottom_right, 255, 2)
    plt.subplot(121),plt.imshow(res,cmap = 'gray')
    plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
    plt.subplot(122),plt.imshow(img,cmap = 'gray')
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.suptitle(meth)
    plt.show()

next_direction = [{
    "x": 0,
    "y": 0
},
{
    "x": 0,
    "y": 0
}]

screens=[{
    "window_coordinates":{
        "x": 550,
        "y": 960
    }
},
{
    "window_coordinates":{
        "x": 750,
        "y": 960
    }
}]

def collect(next_direction):
    center_mouse()
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.moveRel(next_direction['x'], next_direction['y'])
    pyautogui.mouseDown(); pyautogui.mouseUp()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'a')

while True:
    for i, screen in enumerate(screens):
        current_screen = i + 1
        pyautogui.click(640, 1060)
        pyautogui.click(screen['window_coordinates']['x'], screen['window_coordinates']['y'])
        collect(next_direction[i])
        next_direction[i] = find_points()
        if i == (len(screens) - 1):
            time.sleep(13)
        else:
            time.sleep(1)