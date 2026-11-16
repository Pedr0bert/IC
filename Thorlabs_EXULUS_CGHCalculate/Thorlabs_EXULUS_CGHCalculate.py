import os
from ctypes import *
import logging
from enum import *

class ERROR_CODE(IntEnum):
    SUCCESS = 1
    INIT_PIX_SIZE_ERROR = -1
    CROSS_SHIFT_SIZE_ERROR = -2
    CROSS_SHIFT_BUFFER_ERROR = -3
    RAND_PHASE_FFT_BUFFER_ERROR = -4
    CGH_LIB_INIT_ERROR = -5
    CORE_CREATE_HDL_ERROR = -6
    IMG_RESIZE_BUFFER_ERROR = -7
    INDEX_IS_OUTOF_RANGE = -8
    INVALID_INPUT_ERROR = -9
    INTERNAL_ERROR = -0xEA

image_size = 0

""" Setup logger """
sdk_logger = logging.getLogger('EXULUS-CGH-Calculate')
sdk_logger.addHandler(logging.NullHandler())


def sdk_failure_message(function_name, error_code):
    error_type = ERROR_CODE(error_code).name if (error_code in range(-9, -1) or error_code == -0xEA) else "Unknown"
    failure_message = f"{function_name}() returned non-zero error code: {error_code}; error type: {error_type}. "
    return failure_message


class CGHCalculate:
    CGHCalLib = None
    isLoad = False
    cgh_core_init_state = False

    @staticmethod
    def load_library(path):
        try:
            CGHCalculate.CGHCalLib = cdll.LoadLibrary(path)
            CGHCalculate.isLoad = True
        except OSError as os_error:
            raise SDKError(f"{os_error} Unable to load library - Make sure the libraries placed in your project or "
                           "adding the directory with the libraries to the PATH. Make sure to use correct python "
                           "interpreter(bitness:64).")

    def __init__(self):
        lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cgh_lib.dll")
        if not CGHCalculate.isLoad:
            CGHCalculate.load_library(lib_path)
        self.CGHCalLib.cgh_core_close.argtypes = [c_int]
        self.CGHCalLib.cgh_core_calc.argtypes = [c_int, POINTER(c_ubyte), c_float]
        self.CGHCalLib.cgh_core_update_all.argtypes = [c_int, c_int, c_int, c_float, c_float, c_float]
        self.CGHCalLib.cgh_core_update_distance.argtypes = [c_int, c_float]
        self.CGHCalLib.cgh_image_resize.argtypes = [POINTER(c_ubyte), c_int, c_int, POINTER(c_ubyte), c_int, c_int, c_int, c_ubyte]
        self.hdl = -1

    """ with statement functionality """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.hdl >= 0:
            self.cgh_core_close()

    @staticmethod
    def cgh_core_init():
        """Initialize cgh library.
        Returns:
            SUCCESS: success; CGH_LIB_INIT_ERROR: initialize lib failed;
        """
        try:
            ret = -1
            if not CGHCalculate.cgh_core_init_state:
                ret = CGHCalculate.CGHCalLib.cgh_lib_init()
                if ret == 1:
                    CGHCalculate.cgh_core_init_state = True
                else:
                    raise SDKError(sdk_failure_message("cgh_lib_init", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not initialize cgh library: " + str(exception))
            raise exception

    def cgh_core_create(self):
        """Create cgh core before calculate.
        Returns:
            non-negative number: hdl number returned successfully;
            negative number: failed.
        """
        try:
            ret = -1
            if CGHCalculate.isLoad:
                ret = CGHCalculate.CGHCalLib.cgh_core_create()
                if ret >= 0:
                    self.hdl = ret
                else:
                    self.hdl = -1
                    raise SDKError(sdk_failure_message("cgh_core_create", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not create cgh core before calculate: " + str(exception))
            raise exception

    def cgh_core_close(self):
        """Close the created cgh core by hdl
        Returns:
            SUCCESS: success; other number: failed.
        """
        try:
            ret = -1
            if self.hdl >= 0:
                ret = CGHCalculate.CGHCalLib.cgh_core_close(self.hdl)
                if ret != 1:
                    raise SDKError(sdk_failure_message("cgh_core_close", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not close the created cgh core: " + str(exception))
            raise exception

    def cgh_core_calc(self, buffer, stroke_m):
        """Calculate the cgh image
        Args:
            buffer: input image buffer, the result buffer with same pointer.
            stroke_m: it's according to the wavelength.
        Returns:
            SUCCESS: success; other number: failed.
        """
        try:
            ret = -1
            if self.hdl >= 0:
                buffer_val = (c_ubyte * image_size)()
                ret = CGHCalculate.CGHCalLib.cgh_core_calc(self.hdl, buffer_val, c_float(stroke_m))
                if ret != 1:
                    raise SDKError(sdk_failure_message("cgh_core_calc", ret))
                else:
                    for i in range(0, image_size):
                        buffer[i] = buffer_val[i]
            return ret
        except Exception as exception:
            sdk_logger.error("Could not calculate the cgh image: " + str(exception))
            raise exception

    def cgh_core_update_all(self, w_pixel, h_pixel, pix_size_m, distance, wavelength):
        """Set all parameters for cgh core
        Args:
            w_pixel: horizontal pixel number of LCD panel.
            h_pixel: vertical pixel number of LCD panel.
            pix_size_m: physical pixel size of LCD panel, unit meter.
            distance: focus distance, unit meter.
            wavelength: wavelength of light, unit meter.
        Returns:
            SUCCESS: success; other number : failed.
        """
        try:
            ret = -1
            if self.hdl >= 0:
                ret = CGHCalculate.CGHCalLib.cgh_core_update_all(self.hdl, c_int(w_pixel), c_int(h_pixel), c_float(pix_size_m),
                                                                 c_float(distance), c_float(wavelength))
                global image_size
                image_size = w_pixel * h_pixel
                if ret != 1:
                    raise SDKError(sdk_failure_message("cgh_core_update_all", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not update all for cgh core: " + str(exception))
            raise exception

    def cgh_core_update_distance(self, distance):
        """Set distance for cgh core.
        Args:
            distance: focus distance, unit meter.
        Returns:
            SUCCESS: success; other number: failed.
        """
        try:
            ret = -1
            ret = CGHCalculate.CGHCalLib.cgh_core_update_distance(self.hdl, c_float(distance))
            if ret != 1:
                raise SDKError(sdk_failure_message("cgh_core_update_distance", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not update distance for cgh core: " + str(exception))
            raise exception

    @staticmethod
    def cgh_image_resize(src_buf, src_width, src_height, dst_buf, dst_width, dst_height, mode, background_color):
        """Resize image
        Args:
            src_buf: point of source 8 byte image buffer.
            src_width: width of source image.
            src_height: height of source image.
            dst_buf: point of destination 8 byte image buffer.
            dst_width: width of destination image.
            dst_height: height of destination image.
            mode: resize mode
            background_color: set background color for center/fill mode.
        Returns:
            SUCCESS: success; other number: failed.
        """
        try:
            ret = -1
            src_size = src_width * src_height
            src_buf_val = (c_ubyte * src_size)(*src_buf)
            dst_size = dst_width * dst_height
            dst_buf_val = (c_ubyte * dst_size)()
            ret = CGHCalculate.CGHCalLib.cgh_image_resize(src_buf_val, c_int(src_width), c_int(src_height), dst_buf_val,
                                                          c_int(dst_width), c_int(dst_height), c_int(mode),
                                                          c_ubyte(background_color))
            if ret != 1:
                raise SDKError(sdk_failure_message("CghImageResize", ret))
            else:
                for j in range(0, dst_size):
                    dst_buf[j] = dst_buf_val[j]
            return ret
        except Exception as exception:
            sdk_logger.error("Could not resize image: " + str(exception))
            raise exception

class SDKError(Exception):
    def __init__(self, message):
        sdk_logger.debug(message)
        super().__init__(message)


