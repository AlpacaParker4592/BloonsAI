import pygetwindow as gw
import pyscreenshot as ImageGrab
import platform

def getScreenShot(prog_name: str):  # Get Screenshot image & position where get shot
    titles = gw.getAllTitles()
    title = "Ruffle - bloons.swf"

    if prog_name in titles and platform.system() == "Windows":
        window = gw.getWindowsWithTitle(prog_name)[0]
        left, top = window.topleft
        right, bottom = window.bottomright
        left, top, right, bottom = left+10, top+50, right-7, bottom-7
        image = ImageGrab.grab(bbox=(left, top, right, bottom))
        print("ScreenShotMessage: Image Captured")
        print("Game Position - Left: {0}, Top: {1}, Right: {2}, Bottom: {3}".format(left,top,right,bottom))
        return image, {"left": left, "top": top, "right": right, "bottom": bottom}
    elif not title in titles:
        print("ScreenShotMessage: No Programs named {}.".format(title))
        return None, None
    else:
        print("ScreenShotMessage: This platform is NOT Windows.")
        return None, None