import os
import sys

import wintertools.fs
import wintertools.jlink
import wintertools.circuitpython
import wintertools.fw_fetch
import wintertools.uf2_to_bin


DEVICE_NAME = "winterbloom_big_honking_button"
USB_DEVICE_ID = "239A:6005"
JLINK_DEVICE = "ATSAMD21G18"
JLINK_SCRIPT = "scripts/flash.jlink"

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIRMWARE_DIR = os.path.join(ROOT_DIR, "firmware")
LIB_DIR = os.path.join(FIRMWARE_DIR, "lib")
EXAMPLES_DIR = os.path.join(ROOT_DIR, "examples")

FILES_TO_DOWNLOAD = {
    "https://raw.githubusercontent.com/theacodes/Winterbloom_VoltageIO/master/winterbloom_voltageio.py": "winterbloom_voltageio.py",
}

FILES_TO_DEPLOY = {
    wintertools.fs.cache_path("winterbloom_voltageio.py"): "lib",
    os.path.join(FIRMWARE_DIR, "winterbloom_bhb"): "lib",
    os.path.join(ROOT_DIR, "samples"): ".",
    os.path.join(ROOT_DIR, "examples"): ".",
    os.path.join(FIRMWARE_DIR, "LICENSE"): ".",
    os.path.join(FIRMWARE_DIR, "README.HTM"): ".",
    os.path.join(ROOT_DIR, "examples/default.py"): "code.py",
}


def program_firmware():
    print("========== PROGRAMMING FIRMWARE ==========")

    print("Checking for latest bootloader & firmware...")

    wintertools.fw_fetch.latest_bootloader(DEVICE_NAME)
    firmware_path = wintertools.fw_fetch.latest_circuitpython(DEVICE_NAME)

    wintertools.uf2_to_bin(firmware_path)

    wintertools.jlink.run(JLINK_DEVICE, JLINK_SCRIPT)


def deploy_circuitpython_code(destination=None):
    print("========== DEPLOYING CODE ==========")

    if not destination:
        print("Waiting for CIRCUITPY drive...")
        destination = wintertools.fs.wait_for_drive("CIRCUITPY")

    print("Forcing BHB into repl (workaround for CircuitPython issue #3986)")
    wintertools.circuitpython.force_into_repl(USB_DEVICE_ID)

    print("Cleaning temporary files from src directories...")
    wintertools.fs.clean_pycache(FIRMWARE_DIR)
    wintertools.fs.clean_pycache(EXAMPLES_DIR)

    print("Downloading files to cache...")
    wintertools.fs.download_files_to_cache(FILES_TO_DOWNLOAD)
    print("Copying files...")
    wintertools.fs.deploy_files(FILES_TO_DEPLOY, destination)

    print("Done copying files, resetting...")
    wintertools.circuitpython.reset_via_serial(USB_DEVICE_ID)
    print("Done!")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "publish":
        deploy_circuitpython_code("distribution")
        return

    try:
        circuitpython_drive = wintertools.fs.find_drive_by_name("CIRCUITPY")
    except EnvironmentError:
        circuitpython_drive = None

    if not circuitpython_drive:
        program_firmware()

    if circuitpython_drive and os.path.exists(
        os.path.join(circuitpython_drive, "code.py")
    ):
        if input("redeploy code? y/n: ").strip() == "y":
            deploy_circuitpython_code()
    else:
        deploy_circuitpython_code()


if __name__ == "__main__":
    main()
