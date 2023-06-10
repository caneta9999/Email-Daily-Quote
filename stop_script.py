import winreg
from dotenv import load_dotenv
import os

load_dotenv()

def deconfigure_autorun():
    key_path = os.getenv("KEY_PATH")
    value_name = os.getenv("VALUE_NAME")

    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        winreg.DeleteValue(key, value_name)
        winreg.CloseKey(key)
        print("Autorun deconfigured successfully.")
    except FileNotFoundError:
        print("Autorun configuration not found.")

deconfigure_autorun()
