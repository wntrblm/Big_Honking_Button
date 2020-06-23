import io
import time
import os
import subprocess
import utils
import shutil
import zipfile

import requests


JLINK_PATH = "C:\Program Files (x86)\SEGGER\JLink\JLink.exe"
assert os.path.exists("bootloader.bin")
assert os.path.exists("firmware.uf2")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIRMWARE_DIR = os.path.join(ROOT_DIR, "firmware")
LIB_DIR = os.path.join(FIRMWARE_DIR, "lib")
EXAMPLES_DIR = os.path.join(ROOT_DIR, "examples")

FILES_TO_DEPLOY = {
    "https://raw.githubusercontent.com/theacodes/Winterbloom_VoltageIO/master/winterbloom_voltageio.py": "lib",
    os.path.join(FIRMWARE_DIR, "winterbloom_bhb"): "lib",
    os.path.join(ROOT_DIR, "samples"): ".",
    os.path.join(ROOT_DIR, "examples"): ".",
    os.path.join(FIRMWARE_DIR, "LICENSE"): ".",
    os.path.join(FIRMWARE_DIR, "README.HTM"): ".",
    os.path.join(ROOT_DIR, "examples/default.py"): "code.py",
}


def program_bootloader():
    print("========== PROGRAMMING BOOTLOADER ==========")
    subprocess.check_call(
        [JLINK_PATH, "-device", "ATSAMD21G18", "-autoconnect", "1", "-if", "SWD", "-speed", "4000", "-CommanderScript", "flash-bootloader.jlink"]
    )


def program_circuitpython():
    print("========== PROGRAMMING CIRCUITPYTHON ==========")
    input("Connect usb cable, press enter.")
    bootloader_drive = utils.find_drive_by_name("HONKBOOT")
    utils.copyfile("firmware.uf2", os.path.join(bootloader_drive, "NEW.uf2"))


def deploy_circuitpython_code():
    print("========== DEPLOYING CODE ==========")
    # Wait for the circuitpython drive to show up.
    time.sleep(5)
    cpy_drive = utils.find_drive_by_name("CIRCUITPY")

    utils.clean_pycache(FIRMWARE_DIR)
    utils.clean_pycache(EXAMPLES_DIR)

    os.makedirs(os.path.join(cpy_drive, "lib"), exist_ok=True)

    for src, dst in FILES_TO_DEPLOY.items():
        if src.startswith("https://"):
            if '.zip' in src:
                http_src, zip_path = src.rsplit(':', 1)

                zip_data = io.BytesIO(requests.get(http_src).content)

                with zipfile.ZipFile(zip_data, "r") as zipfh:
                    file_data = zipfh.read(zip_path)
                
                dst = os.path.join(dst, os.path.basename(zip_path))
                with open(os.path.join(cpy_drive, dst), "wb") as fh:
                    fh.write(file_data)
            
            else:
                file_data = requests.get(src).content
                _, file_name = src.rsplit('/', 1)
                dst = os.path.join(dst, file_name)
                with open(os.path.join(cpy_drive, dst), "wb") as fh:
                    fh.write(file_data)
                
        else:
            if os.path.isdir(src):
                dst = os.path.join(cpy_drive, dst, os.path.basename(src))
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, os.path.join(cpy_drive, dst))

        print(f"Copied {src} to {dst}")
    
    utils.flush(cpy_drive)
    

def main():
    try:
        bootloader_drive = utils.find_drive_by_name("HONKBOOT")
    except:
        bootloader_drive = None
    
    try:
        circuitpython_drive = utils.find_drive_by_name("CIRCUITPY")
    except:
        circuitpython_drive = None

    if not circuitpython_drive and not bootloader_drive:
        program_bootloader()
    
    if not circuitpython_drive:
        program_circuitpython()

    if circuitpython_drive and os.path.exists(os.path.join(circuitpython_drive, "code.py")):
        if input("redeploy code? y/n: ").strip() == "y":
            deploy_circuitpython_code()
    else:
        deploy_circuitpython_code()


if __name__ == "__main__":
    main()