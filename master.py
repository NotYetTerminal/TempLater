# This is the main python script used to start everything
# I didn't make this from scratch that's why there are not many comments
# but I did change it quite a bit and fixed some errors.
import sys
import pandas as pd

from pynput import mouse, keyboard

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QDesktopWidget, QGridLayout, QLabel,
                             QSpinBox, QFileDialog,
                             QTableWidget, QTableWidgetItem)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
import pyautogui as pgui
import calibrator as cal

class App(QWidget):
    def __init__(self, df=None):
        super().__init__()
        self.title = 'OpenTTD TempLater'
        self.width = 650
        self.height = 400

        if df is None:
            self.keyEvents = pd.DataFrame(columns=['Type', 'Button', 'Coordinates'])
        else:
            self.keyEvents = df

        self.runTimes = 1
        self.calib = 0
        
        self.mListener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll)
        self.kListener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        
        self.yup = 0
        self.refing = 0
        self.start = {}
        self.running = 0
        self.stoppingkey = 0
        
        self.initUI()

    def initUI(self):
        grid = QGridLayout()
        grid.setRowStretch(12,1)
        grid.setColumnStretch(4,1)
        self.setLayout(grid)

        self.recordButton = QPushButton('Start recording')
        grid.addWidget(self.recordButton, 0, 0)
        self.recordButton.clicked.connect(self.start_record)
        self.recordLabel = QLabel('')
        grid.addWidget(self.recordLabel, 0, 1)
        
        self.recureButton = QPushButton('Add on recursive')
        grid.addWidget(self.recureButton, 1, 0)
        self.recureButton.clicked.connect(self.calibsetter)
        
        self.stopButton = QPushButton('Stop/pause\nrecording')
        grid.addWidget(self.stopButton, 2, 0)
        self.stopButton.clicked.connect(self.stop_record)

        self.playButton = QPushButton('Run')
        grid.addWidget(self.playButton, 3, 0)
        self.playButton.clicked.connect(self.play)
        
        self.playBox = QSpinBox()
        grid.addWidget(self.playBox, 4, 1)
        self.playBox.setMinimum(1)
        self.playBox.setMaximum(1313)
        self.playBox.valueChanged.connect(self.runTimes_update)
        grid.addWidget(QLabel('Run the commands .. times'), 4, 0)
        
        grid.addWidget(QLabel('Set your building rail.\n'
                              '0 is default for basic rail.'), 5, 0)
        self.railBox = QSpinBox()
        grid.addWidget(self.railBox, 5, 1)
        self.railBox.setMinimum(0)
        self.railBox.valueChanged.connect(self.refing_update)

        self.emptyButton = QPushButton('Delete all data')
        grid.addWidget(self.emptyButton, 8, 0)
        self.emptyButton.clicked.connect(self.empty_events)

        self.emptyButton2 = QPushButton('Delete row:')
        grid.addWidget(self.emptyButton2, 9, 0)
        self.emptyButton2.clicked.connect(self.del_row)
        self.delBox = QSpinBox()
        grid.addWidget(self.delBox, 9, 1)
        self.delBox.setMinimum(1)

        self.saveButton = QPushButton('Save')
        grid.addWidget(self.saveButton, 11, 0)
        self.saveButton.clicked.connect(self.file_save)

        self.loadButton = QPushButton('Load')
        grid.addWidget(self.loadButton, 12, 0)
        self.loadButton.clicked.connect(self.file_load)
        
        self.table = QTableWidget(1, len(self.keyEvents.columns))
        self.table.setHorizontalHeaderLabels(self.keyEvents.columns)
        grid.addWidget(self.table, 0, 4, 12, 1)
        self.update_table()
        
        
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)
        self.center()
        self.show()


    def file_save(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()","","All Files (*);;CSV Files (*.csv)", options=options)
        if fileName:
            self.keyEvents.to_csv(fileName if fileName.endswith('.csv') else
                                  fileName+'.csv', index=False)
            
            self.yup = 1
            self.keyEvents = pd.read_csv(fileName if fileName.endswith('.csv') else
                                         fileName+'.csv')
            self.update_table()
            

    def file_load(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;CSV Files (*.csv)", options=options)
        if len(files) == 1 and files[0].endswith('.csv'):
            self.yup = 1
            self.keyEvents = pd.read_csv(files[0])
            self.update_table()
    

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())     
            
            
    def start_record(self):
        good = 0
        if self.calib == 0:
            refer = cal.initcalib(self.refing)
        elif self.calib == 1:
            refer = 1
            
        while good == 0:
            if refer == 0:
                good = 1
            elif refer == 1:
                good = 1
                pgui.alert(text='YAY\nCalibration successful. Starting building.\nPress ENTER')
                self.keyEvents = self.keyEvents.iloc[:-2]
                self.recordLabel.setText('<font color="red"><b>Rec.</b></font>')
                self.mListener.start()
                self.kListener.start()
            elif refer == 2:
                refer = cal.initcalib(self.refing)
                continue


    def stop_record(self):
        if self.mListener.running or self.kListener.running:
            self.recordLabel.setText('')
            self.mListener.stop()
            self.kListener.stop()

            self.mListener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll)
            self.kListener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

            self.keyEvents = self.keyEvents.iloc[:-2]
            self.file_save()
        self.update_table()

    
    def play(self):
        if self.yup == 0:
            pgui.alert(text="Please save and load the file.", title="Alert")
            return
        
        if len(self.keyEvents) == 0:
            return

        if self.mListener.running or self.kListener.running:
            self.stop_record()
        
        for run in range(self.runTimes):
            self.stoppingkey = 0
            dop = 0
            
            if dop == 1:
                return
            
            good = 0
            refer = cal.initcalib(self.refing)
            self.kListener.start()
        
            while good == 0:
                if refer == 0:
                    good = 1
                elif refer == 1:
                    self.running = 1
                    good = 1
                
                    #starts the playback
                    if run == 0:
                        rows = self.keyEvents        
                    for i, row in rows.iterrows():
                        del i
                        
                        if self.stoppingkey == 1:
                            self.running = 0
                            dop = 1
                            self.kListener.stop()
                            self.kListener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
                            pgui.mouseUp()
                            for i, row in rows.iterrows():
                                try:
                                    pgui.keyUp(row.Button)
                                except:
                                    continue
                            pgui.alert(text='Build stopped.', title='Done')
                            return
                        
                        # change str to tuple
                        if type(row.Coordinates) is str:
                            row.Coordinates = eval(row.Coordinates)
                        
                        
                        
                        if type(row.Coordinates) is tuple:
                                    
                            # makes coordinates global
                            Sx, Sy = row.Coordinates
                            Sx = Sx + cal.calibrate.Bx
                            Sy = Sy + cal.calibrate.By
                            pgui.moveTo(Sx, Sy)
                            
                            if self.calib == 1:
                                if row.Type == 'Scroll':
                                    if row.Button == 'Down':
                                        pgui.scroll(-1)
                                    elif row.Button == 'Up':
                                        pgui.scroll(1)
                                if row.Button == 'z' or row.Button == 'y':
                                    if row.Type == 'Press':
                                        pgui.keyDown(str(row.Button))
                                    elif row.Type == 'Release':
                                        pgui.keyUp(str(row.Button))
                                continue
                            
                            # uses pyautogui instead of pynput
                            if row.Type == 'Press':
                                pgui.mouseDown(button='left')
                                    
                            elif row.Type == 'Release':
                                pgui.mouseUp(button='left')
                    
                            elif row.Type == 'Scroll':
                                if row.Button == 'Down':
                                    pgui.scroll(-1)
                                elif row.Button == 'Up':
                                    pgui.scroll(1)
                                
                        else:
                            if row.Type == 'Press':
                                pgui.keyDown(str(row.Button))
                                
                            elif row.Type == 'Release':
                                pgui.keyUp(str(row.Button))
                                
                            
                elif refer == 2:
                    refer = cal.initcalib(self.refing)
                    
            self.kListener.stop()
            self.kListener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.running = 0
            
        if refer == 1:
            pgui.alert(text='Build completed.', title='Done')
            
        self.kListener.stop()
        self.kListener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.running = 0
        self.calib = 0
            
    def empty_events(self):
        if self.mListener.running or self.kListener.running:
            self.stop_record()
        self.keyEvents = self.keyEvents.iloc[0:0]
        self.update_table()

    def del_row(self):
        try:
            self.keyEvents = self.keyEvents.drop(self.delBox.value()-1)
            self.keyEvents = self.keyEvents.reset_index(drop=True)
            self.update_table()
        except:
            print('No row to delete!')
            
    def refing_update(self):
        self.refing = self.railBox.value()
        
    def runTimes_update(self):
        self.runTimes = self.playBox.value()
        
    def calibsetter(self):
        self.calib = 1
        self.runTimes = 1
        self.play()
        self.calib = 1
        self.start_record()
        self.calib = 0
        self.runTimes = self.playBox.value()
        
        
    def on_click(self, x, y, button, pressed):
        self.on_action(x, y, button, pressed)
        
    def on_scroll(self, x, y, dx, dy):
        print('scroll')
        x = x - cal.calibrate.Bx
        y = y - cal.calibrate.By
        self.keyEvents = self.keyEvents.append(
            {'Type': 'Scroll',
            'Coordinates': (x, y),
            'Button': 'Down' if dy < 0 else 'Up',
            }, ignore_index=True)
        
    def on_press(self, key):
        key = str(key)
        if self.running == 1:
            if key == 'Key.esc':
                self.stoppingkey = 1
        else:
            self.on_action(-1, -1, key, True)
            
    def on_release(self, key):
        if self.running == 0:
            self.on_action(-1, -1, key, False)
        
        
    def on_action(self, x, y, key, pressed):
        key = str(key)
        if x != -1 and y != -1:
            x = x - cal.calibrate.Bx
            y = y - cal.calibrate.By
        
        elif key[:4] == "Key.":
            key = key[4:]
            if "_" in key:
                new =[]
                new = key.split("_")
                key = new[0]
        elif key[0] == "'":
            key = key[1]
            
        if key == 'y' and pressed == True:
            pressed = 'center'
            
        if key[7:] == 'right' or key == 'left' or key == 'right' or key == 'up' or key == 'down':
            self.recordLabel.setText('')
            self.mListener.stop()
            self.kListener.stop()
            self.mListener = mouse.Listener(on_click=self.on_click)
            self.kListener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
            self.empty_events()
            pgui.alert(text='You used directional movement.\n'
                            'File corrupted restart!', title='ERROR')
        
        elif pressed == True:
            if key not in self.start:
                self.start[key] = 0
            
            for i, o in self.start.items():
                if key == i:
                    if o == 0:
                        self.start[key] = 1
                
                        self.keyEvents = self.keyEvents.append(
                            {'Type': 'Press',
                            'Coordinates':(x, y) if key[:7] == 'Button.' else None,
                            'Button': key,
                            }, ignore_index=True)
                        
                                
        elif pressed == False:
            self.start[key] = 0
            
            self.keyEvents = self.keyEvents.append(
                {'Type': 'Release',
                'Coordinates': (x, y) if key[:7] == 'Button.' else None,
                'Button': key,
                }, ignore_index=True)
            
        elif pressed == 'center':
            x, y = pgui.position()
            x = x - cal.calibrate.Bx
            y = y - cal.calibrate.By
            
            self.keyEvents = self.keyEvents.append(
                    {'Type': 'Move',
                    'Coordinates': (x, y),
                    }, ignore_index=True)
            
            pgui.keyDown('shift')
            pgui.press('del')
            pgui.keyUp('shift')
            pgui.press('c')
            pgui.keyDown('shift')
            pgui.press('f7')
            pgui.keyUp('shift')

    def update_table(self):
        self.delBox.setMaximum(max(1, len(self.keyEvents)))

        self.table.setRowCount(len(self.keyEvents))
        for i, row in self.keyEvents.iterrows():
            for j, data in enumerate(row):
                item = QTableWidgetItem(str(data))
                if j != 3:
                    item.setFlags(Qt.ItemIsEnabled)

                item.setBackground(QColor(255,255,255))
                self.table.setItem(i, j, item)


    def closeEvent(self, event):
        self.stop_record()
        event.accept()

            
if __name__ == '__main__':
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()

    ex = App()
    app.exec_()