try:
    from EXULUS_HDx_COMMAND_LIB import *
except OSError as ex:
    print("Warning:", ex)


def device_control_demo(exulus_hdx):
    print("******  device_control_demo  ******")

    # Check communication
    ack_code = [0]
    ack_code_map = {0x06: "Acknowledge", 0x09: "Not Acknowledge", 0xBB: "SPI_Busy"}
    exulus_hdx.check_communication(ack_code)
    print(f"Communication status: {ack_code_map.get(ack_code[0], 'Unknown')}")

    # Set screen horizontal flip on
    horizontal_flip = 0x01
    exulus_hdx.set_screen_horizontal_flip(horizontal_flip)

    get_horizontal_flip = [0]
    exulus_hdx.get_screen_horizontal_flip(get_horizontal_flip)
    print(f"Get screen horizontal flip status: {get_horizontal_flip[0]}")

    # Set screen vertical flip on
    vertical_flip = 0x01
    exulus_hdx.set_screen_vertical_flip(vertical_flip)

    get_vertical_flip = [0]
    exulus_hdx.get_screen_vertical_flip(get_vertical_flip)
    print(f"Get screen vertical flip status: {get_vertical_flip[0]}")

    # Set phase stroke mode to Half Wave
    phase_stroke_mode = 1
    exulus_hdx.set_phase_stroke_mode(phase_stroke_mode)

    get_phase_stroke_mode = [0]
    exulus_hdx.get_phase_stroke_mode(get_phase_stroke_mode)
    phase_stroke_mode_map = {0x00: "Full Wave", 0x01: "Half Wave"}
    print(f"Get phase stroke mode: {phase_stroke_mode_map.get(get_phase_stroke_mode[0], 'Unknown')}")

    # Set test pattern on
    test_pattern_status = 1
    exulus_hdx.set_test_pattern_status(test_pattern_status)

    get_test_pattern_status = [0]
    exulus_hdx.get_test_pattern_status(get_test_pattern_status)
    print(f"Get test pattern status: {get_test_pattern_status[0]}")

def save_default_setting_demo(exulus_hdx):
    # Save default settings to SLM
    exulus_hdx.save_default_setting()
    print("Save default settings to SLM")


def main():
    print(" *** EXULUS-HDx device control python example *** ")
    """ The EXULUS_HDx_Control can be used with context manager "with" for automatic clean up. """
    with EXULUS_HDx_Control() as exulus_hdx:
        devices = EXULUS_HDx_Control.list_devices()
        print(f"device list: {devices}")
        if len(devices) < 1:
            print('There is no device connected')
        else:
            sn = devices[0][0]
            print(f"Serial number of the first device is: {sn}")

            # Open the first device
            exulus_hdx.open(sn, 38400, 3)

            # Check if device is open
            is_open = EXULUS_HDx_Control.is_open(sn)
            print(f"Device open status: {is_open}")

            device_control_demo(exulus_hdx)
            # save_default_setting_demo(exulus_hdx)

    print("*** End ***")
    input()


main()