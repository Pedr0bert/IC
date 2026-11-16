import os
from ctypes import *
import logging

""" Setup logger """
sdk_logger = logging.getLogger('EXULUS-HDx-Control')
sdk_logger.addHandler(logging.NullHandler())

def sdk_failure_message(function_name, error_code):
    failure_message = f"{function_name}() returned non-zero error code: {error_code}. "
    return failure_message


class EXULUS_HDx_Control:
    HDxControlLib = None
    isLoad = False

    @staticmethod
    def load_library(path):
        try:
            EXULUS_HDx_Control.HDxControlLib = cdll.LoadLibrary(path)
            EXULUS_HDx_Control.isLoad = True
        except OSError as os_error:
            raise SDKError(f"{os_error} Unable to load library - Make sure the libraries placed in your project or "
                           "adding the directory with the libraries to the PATH. Make sure to use correct python "
                           "interpreter(bitness:64).")

    def __init__(self):
        lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EXULUS_HD_Control.dll")
        if not EXULUS_HDx_Control.isLoad:
            EXULUS_HDx_Control.load_library(lib_path)
        self.HDxControlLib.list.argtypes = [c_char_p, c_int]
        self.HDxControlLib.open.argtypes = [c_char_p, c_int, c_int]
        self.HDxControlLib.is_open.argtypes = [c_char_p]
        self.HDxControlLib.close.argtypes = [c_int]
        self.HDxControlLib.GetHdl.argtypes = [c_char_p]
        self.HDxControlLib.set_timeout.argtypes = [c_int, c_int]
        self.HDxControlLib.check_communication.argtypes = [c_int, POINTER(c_ubyte)]
        self.HDxControlLib.get_screen_horizontal_flip.argtypes = [c_int, POINTER(c_ubyte)]
        self.HDxControlLib.set_screen_horizontal_flip.argtypes = [c_int, c_ubyte]
        self.HDxControlLib.get_screen_vertical_flip.argtypes = [c_int, POINTER(c_ubyte)]
        self.HDxControlLib.set_screen_vertical_flip.argtypes = [c_int, c_ubyte]
        self.HDxControlLib.get_phase_stroke_mode.argtypes = [c_int, POINTER(c_ubyte)]
        self.HDxControlLib.set_phase_stroke_mode.argtypes = [c_int, c_ubyte]
        self.HDxControlLib.get_test_pattern_status.argtypes = [c_int, POINTER(c_ubyte)]
        self.HDxControlLib.set_test_pattern_status.argtypes = [c_int, c_ubyte]
        self.HDxControlLib.save_default_setting.argtypes = [c_int]
        self.hdl = -1

    """ with statement functionality """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.hdl >= 0:
            self.close()

    @staticmethod
    def list_devices():
        """List all connected EXULUS HDx devices.
        Returns:
            The EXULUS device list, each device item is [serialNumber, EXULUSType]
        """
        try:
            ret = -1
            if EXULUS_HDx_Control.isLoad:
                str_val = create_string_buffer(1024)
                ret = EXULUS_HDx_Control.HDxControlLib.list(str_val, 1024)
                if ret < 0:
                    raise SDKError(sdk_failure_message("list_devices", ret))
                devices_str = str_val.value.decode("utf-8").split(',')
                devices = []
                dev_info = ["", ""]
                for i, item in enumerate(devices_str):
                    if i % 2 == 0:
                        if item != '':
                            dev_info[0] = item
                        else:
                            continue
                    else:
                        dev_info[1] = item
                        devices.append(dev_info.copy())
                return devices
        except Exception as exception:
            sdk_logger.error("Could not list devices: " + str(exception))
            raise exception

    @staticmethod
    def is_open(serial_no):
        """Check opened status of a specified device.
        Args:
            serial_no: serial number of the device to be checked.
        Return:
            0: port is not opened; 1: port is opened.
        """
        try:
            ret = -1
            if EXULUS_HDx_Control.isLoad:
                ret = EXULUS_HDx_Control.HDxControlLib.is_open(c_char_p(serial_no.encode('utf-8')))
                if ret < 0:
                    raise SDKError(sdk_failure_message("is_open", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not check if device is open: " + str(exception))
            raise exception

    def open(self, serial_no, n_baud, timeout):
        """Open a connection to a specified device.
        Args:
            serial_no: serial number of the device to be opened.
            n_baud: bit per second of port.
            timeout: set timeout value in (s).
        Return:
            non-negative number: handle number returned on success.
            negative number: failure
        """
        try:
            ret = -1
            if EXULUS_HDx_Control.isLoad:
                ret = EXULUS_HDx_Control.HDxControlLib.open(c_char_p(serial_no.encode('utf-8')), c_int(n_baud), c_int(timeout))
                if ret >= 0:
                    self.hdl = ret
                else:
                    self.hdl = -1
                    raise SDKError(sdk_failure_message("open", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not open device: " + str(exception))
            raise exception

    @staticmethod
    def get_handle(serial_no):
        """Get the handle of a specified device.
        Args:
            serial_no: serial number of the device to check.
        Return:
            non-negative number: valid handle.
            -1: no handle found
        """
        try:
            ret = -1
            if EXULUS_HDx_Control.isLoad:
                ret = EXULUS_HDx_Control.HDxControlLib.GetHdl(c_char_p(serial_no.encode('utf-8')))
                if ret < 0:
                    raise SDKError(sdk_failure_message("get_handle", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not get handle: " + str(exception))
            raise exception

    def close(self):
        """Close the currently opened connection.
        Return:
            0: success; negative number: failed.
        """
        try:
            ret = -1
            if self.hdl >= 0:
                ret = EXULUS_HDx_Control.HDxControlLib.close(self.hdl)
                if ret < 0:
                    raise SDKError(sdk_failure_message("close", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not close device: " + str(exception))
            raise exception

    def set_timeout(self, timeout):
        """Set time out value for read or write process.
        Args:
            timeout: time out value.
        Return:
            0: success; negative number: failed.
        """
        try:
            ret = -1
            if self.hdl >= 0:
                ret = EXULUS_HDx_Control.HDxControlLib.set_timeout(self.hdl, c_int(timeout))
                if ret < 0:
                    raise SDKError(sdk_failure_message("set_timeout", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not set timeout: " + str(exception))
            raise exception

    def check_communication(self, ack_code):
        """Check SLM communication status.
        Args:
            ack_code: output list to receive acknowledge code
                      (0x06: Acknowledge, 0x09: Not Acknowledge, 0xBB: SPI_Busy).
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                code = c_ubyte(0)
                ret = EXULUS_HDx_Control.HDxControlLib.check_communication(self.hdl, byref(code))
                if ret != 0:
                    raise SDKError(sdk_failure_message("check_communication", ret))
                else:
                    ack_code[0] = code.value
            return ret
        except Exception as exception:
            sdk_logger.error("Could not check communication: " + str(exception))
            raise exception

    def get_screen_horizontal_flip(self, flip):
        """Get screen horizontal flip.
        Args:
            flip: output list to receive flip status (0x00: Off, 0x01: On).
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                flip_val = c_ubyte(0)
                ret = EXULUS_HDx_Control.HDxControlLib.get_screen_horizontal_flip(self.hdl, byref(flip_val))
                if ret != 0:
                    raise SDKError(sdk_failure_message("get_screen_horizontal_flip", ret))
                else:
                    flip[0] = flip_val.value
            return ret
        except Exception as exception:
            sdk_logger.error("Could not get screen horizontal flip: " + str(exception))
            raise exception

    def set_screen_horizontal_flip(self, flip):
        """Set screen horizontal flip.
        Args:
            flip: flip status (0x00: Off, 0x01: On).
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                ret = EXULUS_HDx_Control.HDxControlLib.set_screen_horizontal_flip(self.hdl, c_ubyte(flip))
                if ret != 0:
                    raise SDKError(sdk_failure_message("set_screen_horizontal_flip", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not set screen horizontal flip: " + str(exception))
            raise exception

    def get_screen_vertical_flip(self, flip):
        """Get screen vertical flip.
        Args:
            flip: output list to receive flip status (0x00: Off, 0x01: On).
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                flip_val = c_ubyte(0)
                ret = EXULUS_HDx_Control.HDxControlLib.get_screen_vertical_flip(self.hdl, byref(flip_val))
                if ret != 0:
                    raise SDKError(sdk_failure_message("get_screen_vertical_flip", ret))
                else:
                    flip[0] = flip_val.value
            return ret
        except Exception as exception:
            sdk_logger.error("Could not get screen vertical flip: " + str(exception))
            raise exception

    def set_screen_vertical_flip(self, flip):
        """Set screen vertical flip.
        Args:
            flip: flip status (0x00: Off, 0x01: On).
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                ret = EXULUS_HDx_Control.HDxControlLib.set_screen_vertical_flip(self.hdl, c_ubyte(flip))
                if ret != 0:
                    raise SDKError(sdk_failure_message("set_screen_vertical_flip", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not set screen vertical flip: " + str(exception))
            raise exception

    def get_phase_stroke_mode(self, mode):
        """Get current phase stroke mode.
        Args:
            mode: output list to receive phase stroke mode (0x00: Full Wave, 0x01: Half Wave).
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                loc = c_ubyte(0)
                ret = EXULUS_HDx_Control.HDxControlLib.get_phase_stroke_mode(self.hdl, byref(loc))
                if ret != 0:
                    raise SDKError(sdk_failure_message("get_phase_stroke_mode", ret))
                else:
                    mode[0] = loc.value
            return ret
        except Exception as exception:
            sdk_logger.error("Could not get phase stroke mode: " + str(exception))
            raise exception

    def set_phase_stroke_mode(self, mode):
        """Set phase stroke mode.
        Args:
            mode: phase stroke mode (0x00: Full Wave, 0x01: Half Wave).
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                ret = EXULUS_HDx_Control.HDxControlLib.set_phase_stroke_mode(self.hdl, c_ubyte(mode))
                if ret != 0:
                    raise SDKError(sdk_failure_message("set_phase_stroke_mode", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not set phase stroke mode: " + str(exception))
            raise exception

    def get_test_pattern_status(self, status):
        """Get test pattern status.
        Args:
            status: output list to receive test pattern status (0x00: Off, 0x01: On).
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                sta = c_ubyte(0)
                ret = EXULUS_HDx_Control.HDxControlLib.get_test_pattern_status(self.hdl, byref(sta))
                if ret != 0:
                    raise SDKError(sdk_failure_message("get_test_pattern_status", ret))
                else:
                    status[0] = sta.value
            return ret
        except Exception as exception:
            sdk_logger.error("Could not get test pattern status: " + str(exception))
            raise exception

    def set_test_pattern_status(self, status):
        """Set test pattern status.
        Args:
            status: test pattern status (0x00: Off, 0x01: On).
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                ret = EXULUS_HDx_Control.HDxControlLib.set_test_pattern_status(self.hdl, c_ubyte(status))
                if ret != 0:
                    raise SDKError(sdk_failure_message("set_test_pattern_status", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not set test pattern status: " + str(exception))
            raise exception

    def save_default_setting(self):
        """Save default settings to SLM.
        Return:
            0: success; negative number: failed.
            -1: time out;
            -2: invalid string buffer;
        """
        try:
            ret = -1
            if self.hdl >= 0:
                ret = EXULUS_HDx_Control.HDxControlLib.save_default_setting(self.hdl)
                if ret != 0:
                    raise SDKError(sdk_failure_message("save_default_setting", ret))
            return ret
        except Exception as exception:
            sdk_logger.error("Could not save default setting: " + str(exception))
            raise exception


class SDKError(Exception):
    def __init__(self, message):
        sdk_logger.debug(message)
        super().__init__(message)
