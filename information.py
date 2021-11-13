import pyautogui as pgui
import time

while True:
    time.sleep(5)
    coor = pgui.size()

    pgui.moveTo(coor[0] / 2, coor[1] / 2)
