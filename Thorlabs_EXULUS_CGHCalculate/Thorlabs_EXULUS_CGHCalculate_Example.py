try:
    from Thorlabs_EXULUS_CGHCalculate import *
except OSError as ex:
    print("Warning:",ex)
import cv2 as cv
import numpy as np
import tkinter as tk
from tkinter import filedialog

 
def main():
    print(" *** EXULUS CGH calculate python example *** ")
    screen_width = 1920
    screen_height = 1080

    """ The CGHCalculate can be used with context manager "with" for automatic clean up. """
    with CGHCalculate() as cgh_calculate_obj:
        root = tk.Tk()
        root.withdraw()

        # open an image
        filepath=filedialog.askopenfilename(title='Please choose an image')
        print('Filepath',filepath)
        img = cv.imread(filepath)
        print(f"image shape: {img.shape}")
        img0 = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
        cv.imshow("Image",img0)
        cv.waitKey(0)

        # image resize
        sp = img0.shape
        image_height = sp[0]
        image_width = sp[1]
        flat_gray = img0.flatten()
        nsrcr = flat_gray
        dst= [0] * (screen_width * screen_height)

        cgh_calculate_obj.cgh_image_resize(nsrcr, image_width, image_height, dst, screen_width, screen_height, 0, 255)
        print('Image resize succeed')

        cgh_calculate_obj.cgh_core_init()
        print('Init finished')

        cgh_calculate_obj.cgh_core_create()
        print('Core Create finished')

        cgh_calculate_obj.cgh_core_update_all(screen_width, screen_height, 0.0000064, 0.00000155, 0.25)
        print('Update parameters succeed')

        cgh_calculate_obj.cgh_core_calc(dst, 0.000005162)
        print('Calculate CGH finished')

        # display the calculated image
        flat_numpy_array = np.array(dst)
        gray_image = flat_numpy_array.reshape(screen_height, screen_width)

        uint8_img = gray_image.astype(np.uint8)
        cv.imshow('uint8_img', uint8_img)
        print(uint8_img)
        cv.waitKey(0)

    print("*** End ***")
    input()

main()
