try:
    from Thorlabs_EXULUS_Display import *
    import numpy as np
except OSError as ex:
    print("Warning:",ex)
import time

def display_demo(displayobj, screen_list):
    print("******  display_demo  ******")

    # get the default IDs of the second screen
    second_screen_info = screen_list[1]
    second_monitor_info = str(second_screen_info[2])
    print("second_monitor_info", second_monitor_info)
    adapter_id = [0]
    monitor_id = [0]
    ret = displayobj.get_default_ID(second_monitor_info.encode("utf-8"), adapter_id, monitor_id)
    if not ret:
        print(f"Default IDs of screen {second_monitor_info} is not found!")
    else:
        print(f"Default IDs of screen {second_monitor_info} is: adapter ID: {adapter_id[0]} and monitor ID: {monitor_id[0]}.")

    # Create a D2D displayer of the second screen.
    displayobj.create_D2D_displayer(adapter_id[0], monitor_id[0])

    # Get the displayer's adapter_id and monitor_id.
    displayer_adapter_id = [0]
    displayer_monitor_id = [0]
    displayobj.get_D2D_displayer_screen_ID(displayer_adapter_id, displayer_monitor_id)
    print(f"The displayer's adapter_id: {displayer_adapter_id[0]} and monitor_id: {displayer_monitor_id[0]}")

    # Get the screen size.
    width = [0]
    height = [0]
    displayobj.get_D2D_displayer_size(width, height)
    print(f"The screen size is width: {width[0]} and height: {height[0]}")

    # Display a red and 50% transparent BGRA image on it for 5 seconds.
    width = 1920
    height = 1200
    image = np.zeros((height, width, 4), dtype=np.uint8)
    color = (0, 0, 255, 128)
    image[:, :] = color
    stride = width * 4
    displayobj.display_image(image, width, height, stride)
    time.sleep(5)

def main():
    print(" *** EXULUS SEx display python example *** ")
    """ The Display can be used with context manager "with" for automatic clean up. """
    with Display() as displayobj:
        screen_list = displayobj.get_display_monitors()
        print(f"screen list: {screen_list}")
        """ To avoid occlusion, if there is only one monitor, do not execute  """
        if len(screen_list) <= 1:
          print('There is only one screen detected!')
        else:
          print(screen_list)
          display_demo(displayobj, screen_list)

    print("*** End ***")
    input()

main()
