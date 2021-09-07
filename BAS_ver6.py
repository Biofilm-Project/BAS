import sys
import matplotlib
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os
import cv2
import numpy as np
from PIL import Image, ImageQt
import pandas as pd
import matplotlib.ticker as mtick
from scipy.stats import kurtosis, skew
plt.style.use('ggplot')

def selection(image):
    r = cv2.selectROI("Choose Well",image)
    #print(r)
    cropped = image[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    mask = np.zeros((cropped.shape[0],cropped.shape[1]), dtype = np.uint8)
    shapes = cropped.shape
    center = (int(shapes[1]/2) , int(shapes[0]/2))
    rad = int(shapes[1]/2)
    cv2.destroyAllWindows()
    blank_circle = cv2.circle(mask, center, rad, (255,0,0), -1)
    result = cv2.bitwise_and(cropped, cropped, mask= mask)
    #show_image(result)
    #cv2.destroyAllWindows()
    return result

def nothing(x):
    pass

def manual_thresh(image):
    thresh=0
    cv2.namedWindow("Trackbar")
    cv2.resizeWindow("Trackbar", 240,240)
    cv2.createTrackbar('Threshold','Trackbar',0,255, nothing)
    cv2.setTrackbarPos('SMax', 'Manual segmentation', 120)
    plt.hist(image.ravel(), 256, [0,256])
    plt.axvline(thresh, color = 'k', linestyle= 'dashed', linewidth=1)
    plt.show()
    print("Pre-acá")
    thresh = cv2.getTrackbarPos('Threshold','Trackbar')
    cv2.destroyAllWindows()
    print("Acá")
    return thresh

def show_image(img):
    screen_res = 1280.,720.
    scale_width = screen_res[0]/img.shape[1]
    scale_height = screen_res[1]/img.shape[0]
    scale = min(scale_width, scale_height)
    window_height = int(img.shape[1]*scale)
    window_width = int(img.shape[0]*scale)
    cv2.namedWindow('Biofilm Image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Biofilm Image', window_width, window_height)
    cv2.imshow('Biofilm Image', img)


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=12, height=9, dpi=100, axes=1):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1= None
        self.ax2= None
        self.ax3= None
        super().__init__(self.fig)

class SliderWindow(QtWidgets.QMainWindow):
    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image = image
        self.label = QtWidgets.QLabel()
        self.button = QtWidgets.QPushButton("Defined Threshold")
        self.layout = QtWidgets.QVBoxLayout()
        self.top_layout = QtWidgets.QHBoxLayout()
        self.slider = QtWidgets.QSlider()
        self.slider.setGeometry(QtCore.QRect(150,100,150,15))
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(255)
        self.slider.setSingleStep(1)
        self.user_input = QtWidgets.QLineEdit("", self)
        self.enter = QtWidgets.QPushButton("Draw Line")
        self.onlyInt = QtGui.QIntValidator()
        self.user_input.setValidator(self.onlyInt)
        #self.entry = QtWidgets.QInputDialog().getInt(self, "Integer Input Dialog", "ingrese manualmente")
        #self.entry.intMinimum(0)
        #self.entry.intMaximum(255)
        #self.entry.labelText("")
        self.canvas = MplCanvas(self, dpi=100)

        self.slider_value = None

        self.top_layout.addStretch(3)
        self.top_layout.addWidget(self.label)
        self.top_layout.addStretch(3)
        self.top_layout.addWidget(self.user_input)
        self.top_layout.addWidget(self.enter)
        self.top_layout.addWidget(self.button)
        
        self.layout.addLayout(self.top_layout)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.canvas)

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        
        self.slider.valueChanged.connect(self.set_line)
        self.button.clicked.connect(self.set_thresh)
        self.enter.clicked.connect(self.draw_line)
        self.setWindowTitle("Select Threshold")
        self.show_histogram()
        self.show()
        

    def show_histogram(self):
        img = np.array(self.image)
        self.canvas.fig.clf()
        self.canvas.ax1 = self.canvas.fig.add_subplot(111)

        vals, bins, _ = self.canvas.ax1.hist(img.flatten(),256, [1,255])
        self.canvas.draw()

    def set_line(self):
        self.label.setText("Threshold: " + str(self.slider.value()))
        img = np.array(self.image)
        print(self.slider.value())
        self.canvas.fig.clf()
        self.canvas.ax1 = self.canvas.fig.add_subplot(111)
        vals, bins, _ = self.canvas.ax1.hist(img.flatten(),256, [1,255])
        self.canvas.ax1.axvline(int(self.slider.value()), color = 'k', linestyle= 'dashed', linewidth=1)
        self.canvas.draw()

    def draw_line(self):
        value = int(self.user_input.text())
        img = np.array(self.image)
        self.canvas.fig.clf()
        self.canvas.ax1 = self.canvas.fig.add_subplot(111)
        vals, bins, _ = self.canvas.ax1.hist(img.flatten(),256, [1,255])
        self.canvas.ax1.axvline(value, color = 'k', linestyle= 'dashed', linewidth=1)
        self.canvas.draw()
        self.slider.setSliderPosition(value)

    def set_thresh(self):
        self.slider_value = int(self.slider.value())
        self.close()
        return self.slider.value()       

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        font = QtGui.QFont()
        font.setPointSize(10)

        location = os.path.dirname(os.path.realpath(__file__))
        self.location = location.replace("\\","//") +"//"

        self.choose_file = QtWidgets.QLabel("Choose Folder")
        self.choose_file.setFont(font)

        self.next_button = QtWidgets.QPushButton()
        self.previous_button = QtWidgets.QPushButton()

        self.next_button2 = QtWidgets.QPushButton()
        self.previous_button2 = QtWidgets.QPushButton()

        left_icon = QtGui.QIcon(self.location +"left-arrow.png")
        right_icon = QtGui.QIcon(self.location +"right-arrow.png")

        self.next_button.setIcon(right_icon)
        self.next_button2.setIcon(right_icon)

        self.previous_button.setIcon(left_icon)
        self.previous_button2.setIcon(left_icon)

        self.ref_index = 0
        self.bio_index = 0

        self.filename_label = QtWidgets.QLabel("")
        self.filename_label.setFont(font)

        self.filename_label2 = QtWidgets.QLabel("")
        self.filename_label2.setFont(font)

        self.choose_button = QtWidgets.QPushButton("...")
        
        self.ready_button = QtWidgets.QPushButton("Ready")
        self.ready_button.setFont(font)
        
        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.setFont(font)

        self.first_step = QtWidgets.QLabel("Choose experiment")
        self.first_step.setFont(font)
        self.first_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")

        self.second_step = QtWidgets.QLabel("Manual Segmentation")
        self.second_step.setFont(font)
        self.second_step.setStyleSheet("border: 1px solid black")

        self.third_step = QtWidgets.QLabel("Select Color Scale")
        self.third_step.setFont(font)
        self.third_step.setStyleSheet("border: 1px solid black ")

        self.fourth_step = QtWidgets.QLabel("Select Threshold")
        self.fourth_step.setFont(font)
        self.fourth_step.setStyleSheet("border: 1px solid black")

        self.fifth_step = QtWidgets.QLabel("Obtención de área")
        self.fifth_step.setFont(font)
        self.fifth_step.setStyleSheet("border: 1px solid black")

        self.ROI_button = QtWidgets.QPushButton("Segment Biofilm Well")
        self.ROI_button.setFont(font)

        self.radio_green = QtWidgets.QRadioButton("Green")
        self.radio_green.setFont(font)
        self.radio_green.setEnabled(False)
        self.radio_gray = QtWidgets.QRadioButton("Gray")
        self.radio_gray.setFont(font)
        self.radio_gray.setEnabled(False)
        #self.radio_new = QtWidgets.QRadioButton("New")
        #self.radio_new.setFont(font)
        #self.radio_new.setEnabled(False)

        self.next_step = QtWidgets.QPushButton("Confirm Color Scale")
        self.next_step.setFont(font)

        self.thresh_button = QtWidgets.QPushButton("Begin Threshold")
        self.thresh_button.setFont(font)

        self.result_button = QtWidgets.QPushButton("Show Results")
        self.result_button.setFont(font)

        self.add_button = QtWidgets.QPushButton("Add Result")
        self.add_button.setFont(font)

        self.export_button = QtWidgets.QPushButton("Export Excel")
        self.export_button.setFont(font)

        self.b_files = None
        self.c_files = None
        self.folders = None

        self.image = None
        self.image2 = None

        self.roi = None
        self.roi2 = None

        self.pix_map = None
        self.pix_map2 = None

        self.roi_map = None
        self.roi_map2 = None

        self.conv_img = None
        self.conv_img2 = None

        self.conv_map = None
        self.conv_map2 = None

        self.directory = None
        self.just_b_filename = None
        self.just_c_filename = None

        self.color_selection = None
        self.threshold = None

        self.image_color = None
        self.image_color2 = None

        self.fig = None
        self.ax = None
        self.ax2 = None
        
        self.slider_window = None

        self.result_canvas = None
        self.toolbar = None

        self.df = None

        self.export_list = list()

        self.temp = list()

        self.image_label = QtWidgets.QLabel()
        self.image_label2 = QtWidgets.QLabel()
        self.image_label3 = QtWidgets.QLabel()
        self.image_label4 = QtWidgets.QLabel()
        self.image_label5 = QtWidgets.QLabel()
        self.image_label6 = QtWidgets.QLabel()

        self.moving_box = QtWidgets.QHBoxLayout()
        self.moving_box2 = QtWidgets.QHBoxLayout()

        self.moving_box.addWidget(self.previous_button)
        self.moving_box.addWidget(self.next_button)

        self.moving_box2.addWidget(self.previous_button2)
        self.moving_box2.addWidget(self.next_button2)

        self.next_button.setHidden(True)
        self.next_button2.setHidden(True)

        self.previous_button.setHidden(True)
        self.previous_button2.setHidden(True)
        
        self.choose_box = QtWidgets.QHBoxLayout()
        self.choose_box.addWidget(self.choose_file)
        self.choose_box.addWidget(self.choose_button)
        self.choose_box.addStretch()

        self.top_box = QtWidgets.QHBoxLayout()#Tree
        
        self.first_box = QtWidgets.QVBoxLayout()
        self.second_box = QtWidgets.QVBoxLayout()
        self.third_box = QtWidgets.QVBoxLayout()
        self.fourth_box = QtWidgets.QVBoxLayout()
        self.fifth_box = QtWidgets.QVBoxLayout()

        self.right_box = QtWidgets.QVBoxLayout()
        self.second_right_box = QtWidgets.QVBoxLayout()
        self.radio_box = QtWidgets.QHBoxLayout()
        
        self.right_box.addWidget(self.image_label)
        self.right_box.addWidget(self.filename_label)
        self.right_box.addLayout(self.moving_box)
        self.right_box.addStretch()

        self.second_right_box.addWidget(self.image_label2)
        self.second_right_box.addWidget(self.filename_label2)
        self.second_right_box.addLayout(self.moving_box2)
        self.second_right_box.addStretch()

        self.first_box.addWidget(self.first_step)
        self.first_box.addLayout(self.choose_box)
        self.first_box.addLayout(self.right_box)
        self.first_box.addLayout(self.second_right_box)

        self.second_box.addWidget(self.second_step)
        self.second_box.addWidget(self.ROI_button)
        self.second_box.addWidget(self.image_label3)
        self.second_box.addWidget(self.image_label4)
        self.second_box.addStretch()
        self.ROI_button.setEnabled(False)

        self.third_box.addWidget(self.third_step)
        self.radio_box.addWidget(self.radio_green)
        self.radio_box.addWidget(self.radio_gray)
        #self.radio_box.addWidget(self.radio_new)
        self.radio_box.addStretch()
        self.third_box.addLayout(self.radio_box)
        self.third_box.addWidget(self.image_label5)
        self.third_box.addWidget(self.image_label6)
        self.third_box.addWidget(self.next_step)
        self.third_box.addStretch()
        self.next_step.setEnabled(False)
        #self.image_label5.setHidden(True)
        #self.image_label6.setHidden(True)

        self.fourth_box.addWidget(self.fourth_step)
        #self.fourth_box.addWidget(self.slider_value)
        #self.fourth_box.addWidget(self.slider)
        self.fourth_box.addWidget(self.thresh_button)
        #self.slider.setEnabled(False)
                
        self.fourth_box.addStretch()
        self.thresh_button.setEnabled(False)

        self.results_row = QtWidgets.QHBoxLayout()
        self.results_row.addWidget(self.result_button)
        self.results_row.addWidget(self.add_button)
        self.results_row.addWidget(self.export_button)
        self.results_row.addStretch()
        
        self.fifth_box.addWidget(self.fifth_step)
        self.fifth_box.addLayout(self.results_row)        
        self.result_button.setEnabled(False)
        self.add_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.fifth_box.addStretch()
        
        self.top_box.addLayout(self.first_box)
        self.top_box.addLayout(self.second_box)
        self.top_box.addLayout(self.third_box)
        self.top_box.addLayout(self.fourth_box)
        self.top_box.addLayout(self.fifth_box)

        self.choose_button.clicked.connect(self.get_image)
        self.ROI_button.clicked.connect(self.select_roi)
        self.next_step.clicked.connect(self.selecting_color)
        self.thresh_button.clicked.connect(self.thresholding)
        #self.slider.valueChanged.connect(self.set_line)
        self.previous_button.clicked.connect(self.previous_ref)
        self.next_button.clicked.connect(self.next_ref)
        self.previous_button2.clicked.connect(self.previous_bio)
        self.next_button2.clicked.connect(self.next_bio)
        self.radio_green.clicked.connect(self.show_scale)
        self.radio_gray.clicked.connect(self.show_scale)
        #self.radio_new.clicked.connect(self.show_scale)
        self.result_button.clicked.connect(self.show_results)
        self.add_button.clicked.connect(self.add_result)
        self.export_button.clicked.connect(self.export_results)

        self.layout = QtWidgets.QVBoxLayout()
        #self.top_box.addLayout(self.left_box)
        #self.top_box.addLayout(self.right_box)
        #self.top_box.addLayout(self.second_right_box)
        #self.layout.addLayout(self.multi_box)
        self.layout.addLayout(self.top_box)

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.setWindowTitle("B.A.S. Ver. 0.6")
        self.show()
    def get_image(self):
        #print(self.location)
        #dialog = QTWidgets.QFileDialog(self, "Select a folder")
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder", os.path.dirname(os.path.abspath(__file__)))

        #directory.setAttribute(Qt.WA_QuitOnClose,False)
        if not directory=='':
            directory = directory.replace("/","//")
            self.directory = directory
            self.folders = [self.directory+'//'+folder for folder in os.listdir(self.directory)]
            if len(self.folders) != 2:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage("Choose a folder with the correct distribution:"+"\n"+" 1) Biofilm 2) Reference")
                error_dialog.setWindowTitle("Error Message")
                error_dialog.exec_()
            else:
                self.b_files = [self.folders[1]+'//'+file for file in os.listdir(self.folders[1])]
                self.c_files = [self.folders[0]+'//'+file for file in os.listdir(self.folders[0])]
                self.just_b_filename = [file for file in os.listdir(self.folders[1])]
                self.just_c_filename = [file for file in os.listdir(self.folders[0])]
        
                if(len(self.c_files)>0 and len(self.b_files)>0):
                    self.next_button.setHidden(False)
                    self.next_button2.setHidden(False)
                    self.previous_button.setHidden(False)
                    self.previous_button2.setHidden(False)
                    self.previous_button.setEnabled(False)
                    self.previous_button2.setEnabled(False)
                    self.filename_label.setText("Well "+self.just_b_filename[self.ref_index].split('.')[0])
                    self.filename_label2.setText("Well "+self.just_c_filename[self.bio_index].split('.')[0])
                    image = cv2.imread(self.b_files[self.ref_index])
                    image2 = cv2.imread(self.c_files[self.bio_index])
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2RGB)
                    self.image = Image.fromarray(image)
                    self.image2 = Image.fromarray(image2)
                    self.pix_map = QtGui.QPixmap(self.b_files[self.ref_index])
                    self.pix_map2 = QtGui.QPixmap(self.c_files[self.bio_index])
                    self.pix_map = self.pix_map.scaledToHeight(240)
                    self.pix_map2 = self.pix_map2.scaledToHeight(240)
                    self.image_label.setPixmap(self.pix_map)
                    self.image_label2.setPixmap(self.pix_map2)
                    self.first_step.setStyleSheet("border: 1px solid black")
                    self.second_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")
                    self.ROI_button.setEnabled(True)
                    #self.choose_button.setEnabled(False)

    def select_roi(self):
        ref = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
        bio = cv2.cvtColor(np.array(self.image2), cv2.COLOR_RGB2BGR)

        QtWidgets.QMessageBox.about(self,"Warning Message", "1) You must press Enter once you have selected the region of interest."
                                    +"\n"+"2) If you're unsure of the selection, you can press the 'Segment Well' Button again."
                                    +"\n"+"3) Avoid closing the Segmentation Window or the main window without having made a selection, the program will close."
                                    +"\n"+"4) You must segment both images to finish the process.")
        
        just_ref = selection(ref)
        just_bio = selection(bio)

        ref_rgb = cv2.cvtColor(just_ref, cv2.COLOR_BGR2RGB)
        bio_rgb = cv2.cvtColor(just_bio, cv2.COLOR_BGR2RGB)

        self.roi = Image.fromarray(ref_rgb)
        self.roi2 = Image.fromarray(bio_rgb)

        roi_qt = ImageQt.ImageQt(self.roi)
        roi_qt2 = ImageQt.ImageQt(self.roi2)

        pix_map = QtGui.QPixmap.fromImage(roi_qt)
        pix_map2 = QtGui.QPixmap.fromImage(roi_qt2)

        self.roi_map = pix_map.scaledToHeight(240)
        self.roi_map2 = pix_map2.scaledToHeight(240)

        #self.ROI_button.setEnabled(False)
        self.radio_gray.setEnabled(True)
        self.radio_green.setEnabled(True)
        #self.radio_new.setEnabled(True)
        self.next_step.setEnabled(True)
        self.second_step.setStyleSheet("border: 1px solid black")
        self.third_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")
        self.image_label3.setPixmap(self.roi_map)
        self.image_label4.setPixmap(self.roi_map2)

        #mostrar el coso antes de tiempo
        self.show_scale()
        
        
    def show_scale(self):
        self.next_step.setEnabled(True)
        img = np.array(self.roi)
        img2 = np.array(self.roi2)
        #print("Prev")
        if(self.radio_gray.isChecked()):
            color = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            color2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
        else:
            color = img.copy()
            color[:,:,0]=0
            color[:,:,2]=0
            color2 = img2.copy()
            color2[:,:,0]=0
            color2[:,:,2]=0
        #print("Post")
        self.conv_img = Image.fromarray(color)
        self.conv_img2 = Image.fromarray(color2)

        conv_qt = ImageQt.ImageQt(self.conv_img)
        conv_qt2 = ImageQt.ImageQt(self.conv_img2)

        pix_map = QtGui.QPixmap.fromImage(conv_qt)
        pix_map2 = QtGui.QPixmap.fromImage(conv_qt2)

        self.conv_map = pix_map.scaledToHeight(240)
        self.conv_map2 = pix_map2.scaledToHeight(240)

        #self.image_label5.setHidden(False)
        #self.image_label6.setHidden(False)

        self.image_label5.setPixmap(self.conv_map)
        self.image_label6.setPixmap(self.conv_map2)
    
    def selecting_color(self):
        isGray = self.radio_gray.isChecked()
        isGreen = self.radio_green.isChecked()
        #isNew = self.radio_new.isChecked()

        if isGray:
            self.color_selection = "Gray"
        if isGreen:
            self.color_selection = "Green"

        self.thresh_button.setEnabled(True)
        self.third_step.setStyleSheet("border: 1px solid black")
        self.fourth_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")        
        
    def set_line(self):
        pass
        if self.color_selection == "Gray":
            self.image_color = cv2.cvtColor(np.array(self.roi), cv2.COLOR_RGB2GRAY)
            self.image_color2 = cv2.cvtColor(np.array(self.roi2), cv2.COLOR_RGB2GRAY)
        elif self.color_selection == "Green":
            self.image_color = np.array(self.roi[:,:,1])
            self.image_color2 = np.array(self.roi2[:,:,1])
        
    def thresholding(self):
        if self.color_selection == "Gray":
            self.image_color = cv2.cvtColor(np.array(self.roi), cv2.COLOR_RGB2GRAY)
            self.image_color2 = cv2.cvtColor(np.array(self.roi2), cv2.COLOR_RGB2GRAY)
        elif self.color_selection == "Green":
            self.image_color = np.array(self.roi)[:,:,1]
            self.image_color2 = np.array(self.roi2)[:,:,1]

        print("A")

        self.slider_window = SliderWindow(self.image_color)
        self.slider_window.show()        
        self.fourth_step.setStyleSheet("border: 1px solid black")
        self.fifth_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")
        self.result_button.setEnabled(True)
        self.ROI_button.setEnabled(True)
        
    def show_results(self):
        self.threshold = self.slider_window.slider_value
        _,wh = cv2.threshold(self.image_color, self.threshold, 255,cv2.THRESH_BINARY_INV)
        res_wh = cv2.bitwise_and(self.image_color, self.image_color, mask = wh)
        
        _, test = cv2.threshold(self.image_color2, self.threshold, 255, cv2.THRESH_BINARY_INV)
        res = cv2.bitwise_and(self.image_color2, self.image_color2, mask = test)
        total_area = len(self.image_color2[self.image_color2!=0])
        percentage = len(res[res!=0])*100/total_area

        global_mean = np.mean(self.image_color2[self.image_color2>0])
        global_median = np.median(self.image_color2[self.image_color2>0])
        global_skew = skew(self.image_color2[self.image_color2>0])
        global_kurt = kurtosis(self.image_color2[self.image_color2>0])
        just_res = res[res>0]
        res_mean = np.mean(just_res)
        res_median = np.median(just_res)
        
        just_wh = self.image_color[self.image_color>0]#todo
        wh_mean = np.mean(just_wh)
        #self.fifth_box.addWidget(self.fifth_step)
        print("A")
        #if (self.result_canvas != None and self.fifth_box != None):
        if (self.result_canvas == None):
            self.result_canvas = MplCanvas(dpi=100)
            self.toolbar = NavigationToolbar(self.result_canvas, self)
            self.fifth_box.addWidget(self.toolbar)
            self.fifth_box.addWidget(self.result_canvas)
        print("B")
        self.result_canvas.fig.clf()
        self.result_canvas.ax1 = self.result_canvas.fig.add_subplot(221)
        self.result_canvas.ax2 = self.result_canvas.fig.add_subplot(222)
        self.result_canvas.ax3 = self.result_canvas.fig.add_subplot(223)
        self.result_canvas.ax4 = self.result_canvas.fig.add_subplot(224)

        self.result_canvas.ax1.imshow(res_wh)
        self.result_canvas.ax1.title.set_text("Reference")
        self.result_canvas.ax2.hist(self.image_color.ravel(),255,[1,255])
        self.result_canvas.ax2.axvline(self.threshold, color = 'k', linestyle = 'dashed', linewidth=1)
        text_ax2 = 'Mass Center: %.3f'%wh_mean
        self.result_canvas.ax2.title.set_text(text_ax2)
        self.result_canvas.ax3.imshow(res)
        self.result_canvas.ax4.hist(self.image_color2.ravel(), 255, [1,255])
        self.result_canvas.ax4.axvline(self.threshold, color = 'k', linestyle = 'dashed', linewidth=1)
        self.result_canvas.ax3.title.set_text("Biofilm")
        showing_text = 'Proportion: %.3f'%percentage
        text_ax4 = 'Mass Center: %.3f'%res_mean
        self.result_canvas.ax4.title.set_text(showing_text+"%" + "  "+text_ax4)
        self.fifth_box.addStretch()
        self.result_canvas.draw()
        print("C")

        self.temp = list()

        name = self.just_c_filename[self.bio_index].split('.')[0]
        
        self.temp = [self.just_c_filename[self.bio_index][0], name.split('_')[0][1:], self.just_c_filename[self.bio_index],self.just_b_filename[self.ref_index], self.threshold, percentage, global_mean, global_median, res_mean,res_median,global_skew,global_kurt]
        
        self.radio_gray.setEnabled(True)
        self.radio_green.setEnabled(True)
        self.add_button.setEnabled(True)
        self.export_button.setEnabled(True)
        #self.radio_new.setEnabled(True)

    def add_result(self):

        print(self.temp)
        
        self.export_list.append(self.temp)

        self.df = pd.DataFrame(self.export_list)
        self.df.columns = ['Row', 'Column', 'File', 'Control File', 'Thresh', 'Prop', 'Global Mean', 'Global Median', 'Bio Mean', 'Bio Median', 'Global Skew', 'Global Kurt']

        print(self.df) 

        QtWidgets.QMessageBox.about(self,"Notification","The values have already been added to the .csv file, Change to another well of your choice."
                                    +"\n"+"Please follow the same step order as you have done, going from left to right."
                                    +"\n"+"Do not skip any step.")

    def export_results(self):

        experimento= self.directory.split('//')[-1]
        filename = r''+self.location+experimento+'_results.csv'
        filename = filename.replace("//","\\")
        print(filename)

        self.df.to_csv(filename, index=False, header=True)

        
        QtWidgets.QMessageBox.about(self,"Notification","The file have been exported, is located in the executable folder"
                                    +"\n"+"It follows this format: Experiment_folder_name + _results.csv"
                                    "\n"+"Overwrites any other file with the same filename, be careful.")
        
    def next_ref(self):
        ref_total = len(self.b_files)
        if(self.ref_index <= ref_total-1):
            self.ref_index +=1
            self.previous_button.setEnabled(True)
        if(self.ref_index == ref_total -1):
            self.next_button.setEnabled(False)
        self.filename_label.setText("Well "+self.just_b_filename[self.ref_index].split('.')[0])
        image = cv2.imread(self.b_files[self.ref_index])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image = Image.fromarray(image)
        self.pix_map = QtGui.QPixmap(self.b_files[self.ref_index])
        self.pix_map = self.pix_map.scaledToHeight(240)
        self.image_label.setPixmap(self.pix_map)
    def previous_ref(self):
        ref_total = len(self.b_files)
        if(self.ref_index >= 0):
            self.next_button.setEnabled(True)
            self.ref_index -=1
        if(self.ref_index == 0):
            self.previous_button.setEnabled(False)
        self.filename_label.setText("Well "+self.just_b_filename[self.ref_index].split('.')[0])
        image = cv2.imread(self.b_files[self.ref_index])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image = Image.fromarray(image)
        self.pix_map = QtGui.QPixmap(self.b_files[self.ref_index])
        self.pix_map = self.pix_map.scaledToHeight(240)
        self.image_label.setPixmap(self.pix_map)

    def next_ref(self):
        ref_total = len(self.b_files)
        if(self.ref_index <= ref_total-1):
            self.ref_index +=1
            self.previous_button.setEnabled(True)
        if(self.ref_index == ref_total -1):
            self.next_button.setEnabled(False)
        self.filename_label.setText("Well "+self.just_b_filename[self.ref_index].split('.')[0])
        image = cv2.imread(self.b_files[self.ref_index])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image = Image.fromarray(image)
        self.pix_map = QtGui.QPixmap(self.b_files[self.ref_index])
        self.pix_map = self.pix_map.scaledToHeight(240)
        self.image_label.setPixmap(self.pix_map)

    def next_bio(self):
        bio_total = len(self.c_files)
        if(self.bio_index <= bio_total-1):
            self.bio_index +=1
            self.previous_button2.setEnabled(True)
        if(self.bio_index == bio_total -1):
            self.next_button2.setEnabled(False)        
        self.filename_label2.setText("Well "+self.just_c_filename[self.bio_index].split('.')[0])
        image = cv2.imread(self.c_files[self.bio_index])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image2 = Image.fromarray(image)
        self.pix_map2 = QtGui.QPixmap(self.c_files[self.bio_index])
        self.pix_map2 = self.pix_map2.scaledToHeight(240)
        self.image_label2.setPixmap(self.pix_map2)
    def previous_bio(self):
        bio_total = len(self.c_files)
        if(self.bio_index > 0):
            self.bio_index -=1
            self.previous_button2.setEnabled(True)
        if(self.bio_index == 0):
            self.previous_button2.setEnabled(False)
        self.filename_label2.setText("Well "+self.just_c_filename[self.bio_index].split('.')[0])
        image = cv2.imread(self.c_files[self.bio_index])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.image2 = Image.fromarray(image)
        self.pix_map2 = QtGui.QPixmap(self.c_files[self.bio_index])
        self.pix_map2 = self.pix_map2.scaledToHeight(240)
        self.image_label2.setPixmap(self.pix_map2)
    
    def clear_image(self):
        pass
    def analyze_image(self):
        pass

app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
#app.setQuitOnLastWindowClosed(False)
#app.processEvents()
app.exec_()
