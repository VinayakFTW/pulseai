from pulse_tools.general_tools import take_screenshot_and_save, web_search
import webbrowser as wb

def screenshot():
    return take_screenshot_and_save()

def open_browser():
    wb.open("https://www.google.com")
    return "Browser opened."
