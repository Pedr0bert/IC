import os
from ctypes import *
import logging

""" Setup logger """
sdk_logger = logging.getLogger('EXULUS-CGH-Display')
sdk_logger.addHandler(logging.NullHandler())

class Display:
    DisplayLib = None
    isLoad = False

    @staticmethod
    def load_library(path):
        try:
            Display.DisplayLib = cdll.LoadLibrary(path)
            Display.isLoad = True
        except OSError as os_error:
            raise SDKError(f"{os_error} Unable to load library - Make sure the libraries placed in your project or "
                           "adding the directory with the libraries to the PATH. Make sure to use correct python "
                           "interpreter(bitness:64).")

    def __init__(self):
        lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "D2D_Display.dll")
        if not Display.isLoad:
            Display.load_library(lib_path)
        self.DisplayLib.CreateD2DDisplayer.restype = c_void_p
        self.DisplayLib.DisplayImage.argtypes = [c_int64, c_void_p, c_int, c_int, c_int]
        self.DisplayLib.GetD2DDisplayerScreenID.argtypes = [c_int64, POINTER(c_int), POINTER(c_int)]
        self.DisplayLib.GetD2DDisplayerSize.argtypes = [c_int64, POINTER(c_int), POINTER(c_int)]
        self.DisplayLib.DestroyD2DDisplayer.argtypes = [c_int64]
        self.displayer = None

    """ with statement functionality """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.displayer is not None:
            self.destroy_D2D_displayer()

    @staticmethod
    def get_display_monitors():
        """List all the available screens on this computer.
        Returns:
            The number of screens list, each screen item is adapter ID/monitor ID/device info.
        """
        try:
            if Display.isLoad:
                str1 = create_string_buffer(10240)
                Display.DisplayLib.GetDisplayMonitors(str1)
                screen_list = []
                screenStr = str1.value.decode("utf-8", "ignore").rstrip('\x00').split(',')
                length = len(screenStr)
                i = 0
                screenInfo = ["", "", ""]
                while i < length:
                    str2 = screenStr[i].split('&')
                    if str2 != ['']:
                        for j in range(0, 3):
                            screenInfo[j] = str2[j]
                        screen_list.append(screenInfo.copy())
                        i += 1
                    else:
                        break
                return screen_list
        except Exception as exception:
            sdk_logger.error("Could not get display monitors: " + str(exception))
            raise exception

    @staticmethod
    def get_default_ID(device_info, adapter_id, monitor_id):
        """Get the default adapter ID and monitor ID of the screen.
        Args:
            device_info: device info of the screen.
            adapter_id: the adapter ID.
            monitor_id: the monitor ID
        Returns:Status
                false: no result found
                true: result found
        """
        try:
            if Display.isLoad:
                adapter_id_val = c_int(0)
                monitor_id_val = c_int(0)
                ret = Display.DisplayLib.GetDefaultID(c_char_p(device_info), byref(adapter_id_val), byref(monitor_id_val))
                adapter_id[0] = adapter_id_val.value
                monitor_id[0] = monitor_id_val.value
                return ret
        except Exception as exception:
            sdk_logger.error("Could not get default ID: " + str(exception))
            raise exception

    def create_D2D_displayer(self, adapter_id, monitor_id):
        """Create a D2D displayer.
        Args:
            adapter_id: the ID of the adapter for display.
            monitor_id: the ID of the monitor for display.
        Returns:
            Pointer to the D2D displayer.
        """
        try:
            if Display.isLoad:
                self.displayer = Display.DisplayLib.CreateD2DDisplayer(c_int(adapter_id), c_int(monitor_id))
                return self.displayer
        except Exception as exception:
            sdk_logger.error("Could not create D2D displayer: " + str(exception))
            raise exception

    def destroy_D2D_displayer(self):
        """Destroy the D2D displayer.
        """
        try:
            Display.DisplayLib.DestroyD2DDisplayer(self.displayer)
        except Exception as exception:
            sdk_logger.error("Could not destroy D2D displayer: " + str(exception))
            raise exception

    def get_D2D_displayer_size(self, width, height):
        """Get the screen size of the D2D displayer.
        Args:
            width: the screen width.
            height: the screen height.
        """
        try:
            width_val = c_int(0)
            height_val = c_int(0)
            Display.DisplayLib.GetD2DDisplayerSize(self.displayer, byref(width_val), byref(height_val))
            height[0] = height_val.value
            width[0] = width_val.value
        except Exception as exception:
            sdk_logger.error("Could not get D2D displayer size: " + str(exception))
            raise exception

    def get_D2D_displayer_screen_ID(self, adapter_id, monitor_id):
        """Get the screen ID of the D2D displayer.
        Args:
            adapter_id: the adapter ID.
            monitor_id: the monitor ID.
        """
        try:
            adapter_id_val = c_int(0)
            monitor_id_val = c_int(0)
            Display.DisplayLib.GetD2DDisplayerScreenID(self.displayer, byref(adapter_id_val), byref(monitor_id_val))
            monitor_id[0] = monitor_id_val.value
            adapter_id[0] = adapter_id_val.value
        except Exception as exception:
            sdk_logger.error("Could not get D2D displayer screen ID: " + str(exception))
            raise exception

    def display_image(self, data, width, height, stride):
        """Display a BGRA image to the D2D displayer.
        Args:
            data: BGRA image data buffer.
            width: image width.
            height: image height.
            stride: image stride.
        """
        try:
            data_pointer = data.ctypes.data_as(c_void_p)
            Display.DisplayLib.DisplayImage(self.displayer, data_pointer, c_int(width), c_int(height), c_int(stride))
        except Exception as exception:
            sdk_logger.error("Could not display image: " + str(exception))
            raise exception

class SDKError(Exception):
    def __init__(self, message):
        sdk_logger.debug(message)
        super().__init__(message)


