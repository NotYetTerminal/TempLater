# I am not a professional programmer so excuse my variable names
# if you know a better way to do things feel free change it
# import the necessary packages
import pyautogui as pgui
import math
from PIL import Image
import glob

def calibrate(rainbow):
    
    # gets mouse position
    Mx, My = pgui.position()
    
    # gets the reference images
    image_list = []
    for files in glob.glob('images\\*.png'):
        im = Image.open(files)
        image_list.append(im)
    
    first = []
    nottemp = []
    tup = 0
    temping =[]
    
    # find all occurences of reference image
    for pos in pgui.locateAllOnScreen(image_list[4]):
        first.append(pos)
    
    if 0 < len(first):
        
        #extracts the x and y coordinates
        for i in range(0, len(first)):
            for pos in first[i]:
                tup-=-1
                
                # finds center of each marker
                if tup < 2:
                    Cx, Cy, = pgui.center(first[i])
                    Cx = Cx - Mx
                    Cy = Cy - My
                    nottemp.append([Cx, Cy])
                    
                elif 3 < tup:
                    tup = 0
                    
                else:
                    continue
                
        # uses pythagoras to calculate closest marker
        for i in range(0, len(first)):
            temping.append(round(math.sqrt((((abs(nottemp[i][0]))^2) + ((abs(nottemp[i][1]))^2))), 5))
        
        # moves mouse into position
        jump = temping.index(min(temping))
        pgui.move(nottemp[jump][0], nottemp[jump][1])
        
        # centers the marker and mouse
        pgui.click()
        pgui.keyDown('shift')
        pgui.press('del')
        pgui.keyUp('shift')
        pgui.press('c')
        pgui.moveTo(1, 1)
        
        try:
            # checks for the type of ui
            try:
                Tx, Ty = pgui.locateCenterOnScreen(image_list[0])
                Tx -= 3
            except TypeError:
                Tx, Ty = pgui.locateCenterOnScreen(image_list[1])
                Tx -= 4
            Sx, Sy = pgui.locateCenterOnScreen(image_list[3])
            del Sx
            
        except TypeError:
            return 11
        
        CenterY = int((Sy - Ty)/2 + Ty)
        pgui.moveTo(Tx, CenterY)
        
        try:
            pgui.moveTo(pgui.locateCenterOnScreen(image_list[5]))
        except:
            return 11
        
        # selects the rail to build from
        try:
            rainbow = int(rainbow)
        except:
            return 10
        
        pgui.mouseDown()
        pgui.move(0, 20)
        pgui.move(0, rainbow*10)
        pgui.mouseUp()
        pgui.moveTo(Tx, CenterY)
        
        caliblist = [0, 1, 2, 3, -1, -2, -3]
        
        # checks to see if everything is as planned
        for i in caliblist:
            pgui.move(0,i)
            
            if pgui.position() == pgui.locateCenterOnScreen(image_list[2]):
                calibrate.Bx = Tx
                calibrate.By = CenterY
                return 20
                
            pgui.moveTo(Tx, CenterY)
                
        return 13
        
    
    else:
        return 12
    
# does the error handling and returns a 10 if error occurs, 20 if calibration successful, 2 retry
def initcalib(colourt):
    Qx, Qy = pgui.position()
    check = calibrate(colourt)
    duf = ''
    if 10 <= check < 20:
        if check == 10:
            pgui.alert(text='Unkown reference!\nCheck settings.', title='ERROR')
            return 0
        elif check == 11:
            duf = ("No GUI found! Use normal sized base menu bar and status bar graphics.\n"
                   "Use the resolutions given in the settings.\n"
                   "640x480 and 720x480 higher supported.")
        elif check == 12:
            pgui.alert(text='No marker found!\nMove map or mouse.', title='ERROR')
            return 0
        elif check == 13:
            duf = 'Mouse in marker not found!'
            
    elif 20 <= check < 30:
        if check == 20:
            return 1
            
    else:
        pgui.alert(text='WHAT DID YOU DO TO MAKE THIS HAPPEN? DO YOU KNOW HOW LONG I SPENT DEBUGGING THIS AND CATCHING ALL THE DIFFERENT ERRORS.\n'
                        'Well done you found a bug. Are you happy now?', title='Do you feel proud? Calibrator unkown ERROR', button='Collect my prize')
        return 0
    
    if pgui.confirm(text=('Error calibrating: ' + duf + '\nRetry?'), title='ERROR') == 'OK':
        pgui.moveTo(Qx, Qy)
        return 2
    else:
        return 0
        
# used for debbuging
if __name__ == '__main__':
    #calibrate(2)
    initcalib(2)