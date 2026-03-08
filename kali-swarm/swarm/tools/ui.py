try:
    import pyautogui
    # PyAutoGUI provides cross-platform mouse/keyboard control.
    # Needs valid X11 Display context in Kali.
    pyautogui.FAILSAFE = True
except ImportError:
    pyautogui = None

import time

class UITools:
    @staticmethod
    def click(x, y):
        """Move to x,y and click."""
        if not pyautogui:
            return "[Error] pyautogui not installed or X11 not running"
        try:
            pyautogui.moveTo(x, y, duration=0.2)
            pyautogui.click()
            return f"[Success] Clicked at {x}, {y}"
        except Exception as e:
            return f"[UI Error] click failed: {e}"

    @staticmethod
    def type_text(text, enter=False):
        """Type given text."""
        if not pyautogui:
            return "[Error] pyautogui not installed"
        try:
            pyautogui.typewrite(text, interval=0.05)
            if enter:
                pyautogui.press('enter')
            return f"[Success] Typed text: {text}"
        except Exception as e:
            return f"[UI Error] type_text failed: {e}"

    @staticmethod
    def screenshot(save_path="screencap.png"):
        """Take a full screenshot to the local filesystem."""
        if not pyautogui:
            return "[Error] pyautogui not installed"
        try:
            img = pyautogui.screenshot()
            img.save(save_path)
            return f"[Success] Screenshot saved at {save_path}"
        except Exception as e:
            return f"[UI Error] screenshot failed: {e}"

    @staticmethod
    def get_screen_size():
        """Get resolution of primary monitor."""
        if not pyautogui:
            return "[Error] pyautogui not installed"
        try:
            width, height = pyautogui.size()
            return f"[Success] Screen resolution: {width}x{height}"
        except Exception as e:
            return f"[UI Error] Could not determine resolution: {e}"
