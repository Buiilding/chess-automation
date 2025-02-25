import pyautogui
from screeninfo import get_monitors
class MouseController:
    def move_mouse(self, from_x, from_y, to_x, to_y):
        monitors = get_monitors()
        second_monitor = monitors[self.screen_index]
        second_monitor_offset_x = second_monitor.x
        second_monitor_offset_y = second_monitor.y
        adjusted_from_x = from_x + second_monitor_offset_x
        adjusted_from_y = from_y + second_monitor_offset_y
        adjusted_to_x = to_x + second_monitor_offset_x
        adjusted_to_y = to_y + second_monitor_offset_y
        pyautogui.moveTo(adjusted_from_x, adjusted_from_y)
        pyautogui.mouseDown()
        pyautogui.moveTo(adjusted_to_x, adjusted_to_y)
        pyautogui.mouseUp()
        # self.scanning = True