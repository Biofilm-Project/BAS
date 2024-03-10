import sys
import matplotlib
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import os
import cv2
import numpy as np
from datetime import date
from PIL import Image, ImageQt
import pandas as pd
import matplotlib.ticker as mtick
from scipy.stats import kurtosis, skew
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.style.use('ggplot')

class InitialWindow(QtWidgets.QMainWindow):
    signal = QtCore.pyqtSignal(str)
    
    def __init__(self, *args, **kwargs):
    
        super().__init__(*args, **kwargs)
        
        location = os.path.dirname(os.path.realpath(__file__))
        self.selected_file = None
        myQWidget = QtWidgets.QWidget()
        
        self.pix_map = QtGui.QPixmap(os.path.join(location, 'welcome_log2.jpeg'))
        
        self.image_label = QtWidgets.QLabel("")
        self.image_label.setPixmap(self.pix_map)
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        self.app_label = QtWidgets.QLabel("B.A.S")
        self.app_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.app_label.setFont(QtGui.QFont('Arial', 64, QtGui.QFont.Bold))
        
        self.new_button = QtWidgets.QPushButton("Start new csv file")
        self.new_button.setToolTip('Select a directory where to position the results.')
        
        self.load_button = QtWidgets.QPushButton("Load csv file")
        self.load_button.setToolTip("Select a previously generated csv file to continue modifying it.")
        
        root_layout = QtWidgets.QVBoxLayout()
        second_row  = QtWidgets.QHBoxLayout()
        new_layout  = QtWidgets.QHBoxLayout()
        load_layout = QtWidgets.QHBoxLayout()
        
        myQWidget.setLayout(root_layout)
        self.setCentralWidget(myQWidget)
        
        new_layout.addWidget(self.new_button)
        load_layout.addWidget(self.load_button)
        
        second_row.addLayout(new_layout)
        second_row.addLayout(load_layout)
        
        root_layout.addWidget(self.image_label, stretch = 2)
        root_layout.addWidget(self.app_label, stretch = 1)
        root_layout.addLayout(second_row, stretch = 4)
        
        self.new_button.clicked.connect(self.create_file)
        self.load_button.clicked.connect(self.choose_file)
        
        self.setFixedWidth(900)
        self.setFixedHeight(760)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(location, 'welcome_log2.png')))
        self.setWindowTitle('Biofilm Analysis Software')
    
    def create_file(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setNameFilter("CSV files (*.csv)")
        file_dialog.setDefaultSuffix("csv")
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            with open(file_path, 'w', newline='') as csvfile:
                # You can write header if needed
                # csv_writer = csv.writer(csvfile)
                # csv_writer.writerow(['Column1', 'Column2', 'Column3'])
                pass
            #print(f"CSV file created: {file_path}")
        
        self.selected_file = file_path
        self.signal.emit('Open SecondWindow')
        self.close()
    
    def choose_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Select a file',
                                                        os.path.dirname(os.path.abspath(__file__)),
                                                        "Comma-separated values (*.csv)")
        
        if file !='':
            self.selected_file = file
            self.signal.emit('Open SecondWindow')
            self.close()

class ScreenHandler(QtWidgets.QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.first_window = InitialWindow()
        self.second_window = None
        self.first_window.signal.connect(self.change_window)
        self.first_window.show()
    
    @QtCore.pyqtSlot(str)
    def change_window(self, event):
        if event == 'Open SecondWindow':
            self.second_window = MainWindow(self.first_window.selected_file) #add the selected file
            self.second_window.signal.connect(self.change_window)
            self.second_window.setStyleSheet("QMainWindow { border: 1px solid black; }")
            self.second_window.show()
            
        elif event == 'Change SecondWindow file':
        
            new_file = self.second_window.new_file
            self.second_window = MainWindow(new_file)
            self.second_window.setStyleSheet("QMainWindow { border: 1px solid black; }")

            #self.second_window.info_box.exec_()
            self.second_window.show()


def circular_selection(image, idd):
    '''
    Function to perform the manual crop in the image.

    This crop has a circular shape as the ROI has that shape.
    You select the borders of the ROI, and this function
    obtains the coordinates of the selected radius. 
    
    '''
    img=image
    
    if idd == 0:
        cv2.namedWindow('Reference Well', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Reference Well', (1280,720))
        imS = cv2.resize(img, (1280,720))
        r = cv2.selectROI("Reference Well",img)
        
    else:
        cv2.namedWindow('Growth Well', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Growth Well', (1280, 720))
        imS = cv2.resize(img, (1280,720))
        r = cv2.selectROI('Growth Well', img) #[Top_X, Top_Y, Bottom_X, Bottom_Y]


    #print(r)
    #print(cv2.resize(r, (img.shape[0], img.shape[1])))
    #r = [0,0,0,0]
    #
    #print(r)
    cropped = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    mask = np.zeros((cropped.shape[0],cropped.shape[1]), dtype = np.uint8)
    shapes = cropped.shape
    center = (int(shapes[1]/2) , int(shapes[0]/2))
    rad = int(shapes[1]/2)
    cv2.destroyAllWindows()
    blank_circle = cv2.circle(mask, center, rad, (255,0,0), -1)
    result = cv2.bitwise_and(cropped, cropped, mask= mask)
    return result

def square_selection(image, idd):
    '''
    Function to perform the manual crop in the image.

    This crop has a circular shape as the ROI has that shape.
    You select the borders of the ROI, and this function
    obtains the coordinates of the selected radius. 
    
    '''
    img=image    

    if idd == 0:
        cv2.namedWindow('Reference Well', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Reference Well', (1280,720))
        imS = cv2.resize(img, (1280,720))
        r = cv2.selectROI("Reference Well",img,showCrosshair = False)
        
    else:
        cv2.namedWindow('Growth Well', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Growth Well', (1280, 720))
        imS = cv2.resize(img, (1280,720))
        r = cv2.selectROI('Growth Well', img, showCrosshair = False) #[Top_X, Top_Y, Bottom_X, Bottom_Y]

    #print(r)
    #print(cv2.resize(r, (img.shape[0], img.shape[1])))
    #r = [0,0,0,0]
    #
    #print(r)
    cropped = img[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    mask = np.ones((cropped.shape[0],cropped.shape[1]), dtype = np.uint8)
    shapes = cropped.shape
    #center = (int(shapes[1]/2) , int(shapes[0]/2))
    #rad = int(shapes[1]/2)
    cv2.destroyAllWindows()
    #cv2.imshow('A', cropped)
    #blank_square = cv2.rectangle(mask, , (255,0,0), -1)
    result = cv2.bitwise_and(cropped, cropped, mask= mask)
    return result


def nothing(x):
    pass

def manual_thresh(image):
    '''
    Function to create the window for the manual thresh selection

    This window shows the image histogram with a trackbar and an input.

    This trackbar has a range of 256 values (0 -255), as the images
    contain 8-bit information.

    A vertical line is drawn in the figure, and it represents the value
    of the manual threshold.

    Once the value is selected, this function return the threshold to the
    main window.

    '''
    thresh=0
    cv2.namedWindow("Trackbar")
    cv2.resizeWindow("Trackbar", 240,240)
    cv2.createTrackbar('Threshold','Trackbar',0,255, nothing)
    cv2.setTrackbarPos('SMax', 'Manual segmentation', 120)
    plt.hist(image.ravel(), 256, [0,256])
    plt.axvline(thresh, color = 'k', linestyle= 'dashed', linewidth=1)
    plt.show()
    thresh = cv2.getTrackbarPos('Threshold','Trackbar')
    cv2.destroyAllWindows()
    return thresh

def show_image(img):
    '''
    Function to show an image with a resolution of 1280x720 pixels
    '''
    
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
    #MplCanvas is a class that contains all the attributes related to the
    #canvas drawn in the main UI.
    def __init__(self, parent=None, width=12, height=9, dpi=100, axes=1):
        '''
        During the initilization of the class, a figure with 3 axes is
        created. This can be modified in other versions. 
        '''
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax1= None
        self.ax2= None
        self.ax3= None
        super().__init__(self.fig)

class SliderWindow(QtWidgets.QMainWindow):
    #SliderWindow is a class that containts all the attributes related to the
    #window created during the threshold selection. This window contains
    #a canvas, an slider and an input box.
    def __init__(self, image, color, *args, **kwargs):
        '''
        During the initilization, this class creates all the necessary attributes
        and acommodates the layout to show all the information in order.
        '''
        super().__init__(*args, **kwargs)
        self.image = image
        self.label = QtWidgets.QLabel()
        self.button = QtWidgets.QPushButton("Confirm Threshold")
        self.recommended_label = QtWidgets.QLabel("Recommended Thresh: " + str(np.floor(np.percentile(self.image[self.image>0],0.05))))
        #self.recommended_label.setAlignment(QtCore.AlignHCenter)
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
        self.onlyInt = QtGui.QIntValidator(0,255, self)
        self.user_input.setValidator(self.onlyInt)
        self.canvas = MplCanvas(self, dpi=100)
        self.slider_value = None
        self.color = color

        self.middle_layout = QtWidgets.QHBoxLayout()

        self.middle_layout.addWidget(self.recommended_label)
        self.middle_layout.setAlignment(QtCore.Qt.AlignCenter)
        #self.middle_layout.addStretch()

        self.top_layout.addStretch(3)
        self.top_layout.addWidget(self.label)
        self.top_layout.addStretch(3)
        self.top_layout.addWidget(self.user_input)
        self.top_layout.addWidget(self.enter)
        self.top_layout.addWidget(self.button)
        
        self.layout.addLayout(self.top_layout)
        self.layout.addWidget(self.slider)
        self.layout.addStretch()
        self.layout.addLayout(self.middle_layout)
        self.layout.addStretch()
        self.layout.addWidget(self.canvas)
        self.layout.setAlignment(QtCore.Qt.AlignHCenter)

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        
        self.slider.valueChanged.connect(self.set_line)
        self.button.clicked.connect(self.set_thresh)
        self.enter.clicked.connect(lambda ch, p=0: self.draw_line(p))
        self.user_input.returnPressed.connect(self.on_space_pressed)
        #self.user_input.returnPressed.connect(lambda:self.draw_line2())
        self.setWindowTitle("Select Threshold")
        self.show_histogram()
        self.show()
    
    def on_space_pressed(self):
        thresh = int(self.user_input.text())
        img = np.array(self.image)
        self.canvas.fig.clf()
        self.canvas.ax1 = self.canvas.fig.add_subplot(111)
        vals, bins, _ = self.canvas.ax1.hist(img.flatten(),256, [1,255])
        self.canvas.ax1.axvline(thresh, color = 'k', linestyle= 'dashed', linewidth=1)
        self.canvas.draw()
        self.slider.setSliderPosition(thresh)
        #self.draw_line(0)

    def show_histogram(self):
        '''
        This function draws the image histogram in the canvas that is showed in the
        window.
        '''
        img = np.array(self.image)
        self.canvas.fig.clf()
        self.canvas.ax1 = self.canvas.fig.add_subplot(111)
        self.canvas.ax1.set_title('Histogram for ' +self.color+' Channel for Reference Image')
        self.canvas.ax1.set_xlabel('Pixel Value')
        self.canvas.ax1.set_ylabel('Frequency [N]')

        vals, bins, _ = self.canvas.ax1.hist(img.flatten(),256, [1,255])
        self.canvas.draw()

    def set_line(self):
        '''
        This function draws a vertical line that represents tha selected value
        with the slider.
        '''
        self.label.setText("Threshold: " + str(self.slider.value()))
        self.canvas.fig.clf()
        self.show_histogram()
        self.canvas.ax1.axvline(int(self.slider.value()), color = 'k', linestyle= 'dashed', linewidth=1)
        self.canvas.draw()

    def draw_line(self, idx):
        '''
        This function draws a vertical line when the user uses the input box
        is an alternative way of showing the threshold.
        '''
        try:
            print(idx)
            value = int(self.user_input.text())
            print(value)
            img = np.array(self.image)
            self.canvas.fig.clf()
            self.canvas.ax1 = self.canvas.fig.add_subplot(111)
            vals, bins, _ = self.canvas.ax1.hist(img.flatten(),256, [1,255])
            self.canvas.ax1.axvline(value, color = 'k', linestyle= 'dashed', linewidth=1)
            self.canvas.draw()
            self.slider.setSliderPosition(value)
        except:
            pass
    
    def set_thresh(self):
        '''
        This function closes the slider window once the user has chosen the
        threshold.
        It returns the value to the main window
        '''
        self.slider_value = int(self.slider.value())
        self.close()
        return self.slider.value()

class TableWindow(QtWidgets.QMainWindow):
    def __init__(self, dataframe, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.widget = QtWidgets.QWidget()
        self.scroll = QtWidgets.QScrollArea()
        self.layout = QtWidgets.QVBoxLayout()
        self.datatable = QtWidgets.QTableWidget()

        self.df = dataframe
        self.datatable.setColumnCount(self.df.shape[1])
        self.datatable.setRowCount(self.df.shape[0])

        self.datatable.setHorizontalHeaderLabels(self.df.columns)
        #self.datatable.horizontalHeaderItem().setTextAlignment(Qt.AlignHCenter)

        for i in range(self.df.shape[0]):
            for j in range(self.df.shape[1]):
                self.datatable.setItem(i,j,QtWidgets.QTableWidgetItem(str(self.df.iloc[i, j])))
        self.scroll.setWidget(self.datatable)
        self.layout.addWidget(self.datatable)
        
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.setWindowTitle("Result Dataframe")
        self.show()

class WelcomeDialog(QtWidgets.QDialog):
    def __init__(self, parent = None, *args, **kwargs):
        super().__init__(parent)
        location = os.path.dirname(os.path.realpath(__file__))
        self.setWindowIcon(QtGui.QIcon(os.path.join(location, 'welcome_log2.png')))
        self.setWindowTitle('Welcome')
        
        # Add the logo to the message box
        logo_label = QtWidgets.QLabel()
        logo_pixmap = QtGui.QPixmap(os.path.join(location, 'welcome_log2.png'))  # Replace "path/to/your/logo.png" with the actual path to your logo
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignCenter)

        # Add welcome message to the layout
        welcome_label = QtWidgets.QLabel(self)
        welcome_label.setText("Welcome to BAS!")
        welcome_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Add instructions to the layout
        instructions_label = QtWidgets.QLabel(self)
        instructions_label.setText('Here are some brief instructions to get you started:\n1.'+
                                   'Select the reference/blank well.\n2. Select the growth well.\n3.'+
                                   'Select the geometry of the Region of Interest (ROI).\n4.'+
                                   'Apply a manual crop to the ROI of each image.\n5. Select the color transformation option.\n6.'+ 
                                   'Define the threshold value according to the blank histogram.\n7.'+
                                   'Apply the manual thresholding.\n8. Obtain the results. \n9. Add the results to the csv file if satisfactory.')
        instructions_label.setAlignment(QtCore.Qt.AlignCenter)   
        #'<a href="https://github.com/your_username/your_repository">Click here to visit the GitHub repository</a>'
        #Add link to the Github repo
        link_label = QtWidgets.QLabel()
        link_label.setText('For more information and detailed usage examples, please visit our '+
                               '<a href="https://github.com/Biofilm-Project/BAS">GitHub repository</a>.')
        link_label.setAlignment(QtCore.Qt.AlignCenter)
        link_label.setOpenExternalLinks(True)
        link_label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        #self.info_box.addWidget(QtWidgets.QMessageBox.Ok)
        
        message_layout = QtWidgets.QVBoxLayout()
        message_layout.addWidget(logo_label)
        message_layout.addWidget(welcome_label)
        message_layout.addWidget(instructions_label)
        message_layout.addWidget(link_label)
        #message_layout.addWidget(QtWidgets.QMessageBox.Ok)
        
        self.setLayout(message_layout)        

class MainWindow(QtWidgets.QMainWindow):
    signal = QtCore.pyqtSignal(str)
    def __init__(self, filename, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #Setting up font size
        font = QtGui.QFont()
        font.setPointSize(10)

        #Getting executable/main.py file location
        location = os.path.dirname(os.path.realpath(__file__))
        self.location = location.replace("\\","//") +"//"
        
        self.menubar = self.menuBar()
        self.file_menu = self.menubar.addMenu('File')
        self.data_menu = self.menubar.addMenu('Data')
        self.help_menu = self.menubar.addMenu('Help')
        
        self.open_action = QtWidgets.QAction('Open csv file', self)
        self.file_menu.addAction(self.open_action)
        self.open_action.triggered.connect(self.open_file)
        
        self.showData_action = QtWidgets.QAction('Show Data', self)
        self.showData_action.triggered.connect(self.show_dataframe)
        self.data_menu.addAction(self.showData_action)
        
        self.getHelp_action = QtWidgets.QAction('Show B.A.S Instructions')
        self.help_menu.addAction(self.getHelp_action)
        self.getHelp_action.triggered.connect(self.open_HelpDialog)
        
        #Settin up widgets --- Main UI
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

        self.current_folder = 0

        self.ref_index = 0
        self.bio_index = 0

        self.filename_label = QtWidgets.QLabel("")
        self.filename_label.setFont(font)

        self.filename_label2 = QtWidgets.QLabel("")
        self.filename_label2.setFont(font)

        self.choose_button = QtWidgets.QPushButton("...")
        
        self.ready_button = QtWidgets.QPushButton("Ready")
        self.ready_button.setFont(font)

        self.next_folder = QtWidgets.QPushButton('Next Folder')
        self.previous_folder = QtWidgets.QPushButton('Prev Folder')
        
        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.setFont(font)

        self.first_step = QtWidgets.QLabel("Choose Work Space")
        self.first_step.setFont(font)
        self.first_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")

        self.second_step = QtWidgets.QLabel("Manual Cropping")
        self.second_step.setFont(font)
        self.second_step.setStyleSheet("border: 1px solid black")

        self.third_step = QtWidgets.QLabel("Select Color Scale")
        self.third_step.setFont(font)
        self.third_step.setStyleSheet("border: 1px solid black ")

        self.fourth_step = QtWidgets.QLabel("Select Threshold")
        self.fourth_step.setFont(font)
        self.fourth_step.setStyleSheet("border: 1px solid black")

        self.fifth_step = QtWidgets.QLabel("Output")
        self.fifth_step.setFont(font)
        self.fifth_step.setStyleSheet("border: 1px solid black")

        self.new_ref_button = QtWidgets.QPushButton('Crop New Reference ROI')
        self.new_ref_button.setFont(font)

        self.new_growth_button = QtWidgets.QPushButton('Crop New Growth ROI')
        self.new_growth_button.setFont(font)

        self.ROI_button = QtWidgets.QPushButton("Crop Region of Interest")
        self.ROI_button.setFont(font)

        self.auto_crop = QtWidgets.QPushButton('Automatic ROI Crop')
        self.auto_crop.setFont(font)
        
        self.geometry_groupbox = QtWidgets.QGroupBox('Cropping Geometry Options')

        self.square_radio = QtWidgets.QRadioButton("Square ROI")
        self.square_radio.setFont(font)
        #self.square_radio.setEnabled(False)
        self.square_radio.setChecked(False)
        self.circular_radio = QtWidgets.QRadioButton("Circular ROI")
        self.circular_radio.setFont(font)
        #self.circular_radio.setEnabled(False)
        self.circular_radio.setChecked(False)
        
        self.shape_box = QtWidgets.QHBoxLayout()
        self.shape_box.addWidget(self.circular_radio)
        self.shape_box.addWidget(self.square_radio)
        #self.shape_box.addStretch()
        
        self.geometry_groupbox.setLayout(self.shape_box)
        self.geometry_groupbox.setEnabled(False)
        
        self.color_groupbox = QtWidgets.QGroupBox('Color Transformation Options')
        
        self.radio_green = QtWidgets.QRadioButton("Green")
        self.radio_green.setFont(font)
        #self.radio_green.setEnabled(False)
        self.radio_green.setChecked(False)
        self.radio_gray = QtWidgets.QRadioButton("Gray")
        self.radio_gray.setFont(font)
        #self.radio_gray.setEnabled(False)
        self.radio_green.setChecked(False)
        
        self.color_box = QtWidgets.QHBoxLayout()
        self.color_box.addWidget(self.radio_green)
        self.color_box.addWidget(self.radio_gray)
        #self.color_box.addStretch()
        
        self.color_groupbox.setLayout(self.color_box)
        self.color_groupbox.setEnabled(False)

        self.next_step = QtWidgets.QPushButton("Confirm Color Scale")
        self.next_step.setFont(font)

        self.thresh_button = QtWidgets.QPushButton("Set Threshold")
        self.thresh_button.setFont(font)

        self.remove_button = QtWidgets.QPushButton('Apply Threshold')
        self.remove_button.setFont(font)

        #self.result_button = QtWidgets.QPushButton("Show Results")
        #self.result_button.setFont(font)

        self.add_button = QtWidgets.QPushButton("Add Result")
        self.add_button.setFont(font)
        
        self.state_label = QtWidgets.QLabel("... on file '___result.csv - currently 0 rows")
        self.state_label.setFont(font)

        #self.table_button = QtWidgets.QPushButton('Show csv file')
        #self.table_button.setFont(font)

        #self.export_button = QtWidgets.QPushButton("Export Excel")
        #self.export_button.setFont(font)

        self.initial_round = True

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

        self.contador_ref = 0
        
        self.color_selection = None
        self.threshold = None
        
        self.image_color = None
        self.image_color2 = None

        self.fig = None
        self.ax = None
        self.ax2 = None
        
        self.slider_window = None
        self.table_window = None

        self.result_canvas = None
        self.toolbar = None

        self.export_name = filename
        self.new_file = None
        
        try:
            self.df = pd.read_csv(self.export_name)
        except:
            self.df = None
        self.welcome_dialog = None

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

        self.previous_folder.setEnabled(False)
        self.next_folder.setEnabled(False)

        self.top_box = QtWidgets.QHBoxLayout()#Tree
        
        self.first_box = QtWidgets.QVBoxLayout()
        self.second_box = QtWidgets.QVBoxLayout()
        self.third_box = QtWidgets.QVBoxLayout()
        self.fourth_box = QtWidgets.QVBoxLayout()
        self.fifth_box = QtWidgets.QVBoxLayout()

        self.right_box = QtWidgets.QVBoxLayout()
        self.second_right_box = QtWidgets.QVBoxLayout()
        
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
        self.second_box.addWidget(self.geometry_groupbox)
        self.second_box.addWidget(self.ROI_button)
        self.second_box.addWidget(self.image_label3)
        self.second_box.addWidget(self.new_ref_button)
        self.second_box.addWidget(self.image_label4)
        self.second_box.addWidget(self.new_growth_button)
        self.second_box.addStretch()
        self.ROI_button.setEnabled(False)
        self.new_ref_button.setVisible(False)
        self.new_growth_button.setVisible(False)

        self.third_box.addWidget(self.third_step)
        self.third_box.addWidget(self.color_groupbox)
        self.third_box.addWidget(self.image_label5)
        self.third_box.addWidget(self.image_label6)
        self.third_box.addWidget(self.next_step)
        self.third_box.addStretch()
        self.next_step.setEnabled(False)
        
        self.fourth_box.addWidget(self.fourth_step)
        self.fourth_box.addWidget(self.thresh_button)
        self.fourth_box.addWidget(self.remove_button)
                
        self.fourth_box.addStretch()
        self.thresh_button.setEnabled(False)
        self.remove_button.setEnabled(False)

        self.results_row = QtWidgets.QHBoxLayout()
        #self.results_row.addWidget(self.result_button)
        self.results_row.addWidget(self.add_button)
        self.results_row.addWidget(self.state_label)
        #self.results_row.addWidget(self.table_button)
        self.state_label.setVisible(False)
        #self.table_button.setEnabled(False)
        #self.results_row.addWidget(self.export_button)
        self.results_row.addStretch()
        
        self.fifth_box.addWidget(self.fifth_step)
        self.fifth_box.addLayout(self.results_row)        
        #self.result_button.setEnabled(False)
        self.add_button.setEnabled(False)
        #self.export_button.setEnabled(False)
        self.fifth_box.addStretch()
        
        self.top_box.addLayout(self.first_box)
        self.top_box.addLayout(self.second_box)
        self.top_box.addLayout(self.third_box)
        self.top_box.addLayout(self.fourth_box)
        self.top_box.addLayout(self.fifth_box)

        self.choose_button.clicked.connect(self.get_image)

        self.ROI_button.clicked.connect(lambda ch, p=0: self.select_roi(p))
        self.new_ref_button.clicked.connect(lambda ch, p=1: self.select_roi(p))
        self.new_growth_button.clicked.connect(lambda ch, p=2: self.select_roi(p))
        
        self.next_step.clicked.connect(self.selecting_color)
        self.thresh_button.clicked.connect(self.thresholding)
        self.previous_button.clicked.connect(self.previous_ref)
        self.next_button.clicked.connect(self.next_ref)
        self.previous_button2.clicked.connect(self.previous_bio)
        self.next_button2.clicked.connect(self.next_bio)
        self.radio_green.clicked.connect(self.show_scale)
        self.radio_gray.clicked.connect(self.show_scale)
        #self.result_button.clicked.connect(self.show_results)
        self.remove_button.clicked.connect(self.execute_thresh)
        self.add_button.clicked.connect(self.add_result)
        #self.table_button.clicked.connect(self.show_dataframe)
        #self.export_button.clicked.connect(self.export_results)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.top_box)

        self.widget = QtWidgets.QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(location, 'welcome_log2.png')))
        self.setWindowTitle('Biofilm Analysis Software')

        #self.setFixedHeight(840)
        self.show()
        
    def open_file(self):
    
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select a file",
                                                            os.path.dirname(os.path.abspath(__file__)),
                                                            "Comma-separated values (*.csv)")
        
        
        if file !='':
            self.new_file = file
            self.signal.emit('Change SecondWindow file')
            #print(self.new_file)
            self.close()
            
    def open_HelpDialog(self):
    
        self.welcome_dialog = WelcomeDialog()
        self.welcome_dialog.exec_()
            
    def get_image(self):
        '''
        Initial function in the Main UI that allows the user to choose a particular directory/folder for further analysis.
        During this function, multiple attributes are filled, such as the directory and all the filenames inside it.
        Also, shows the first images (reference and biofilm) following an alphabetical order.

        If the user chooses an empty directory or something alike, there'll be an error dialog with a set of instructions.        
        '''
        
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select a folder", os.path.dirname(os.path.abspath(__file__)))
        if not directory=='':
            directory = directory.replace("/","//")
            self.directory = directory
            self.folders = [self.directory+'//'+folder for folder in os.listdir(self.directory) if folder[-4:]!='.txt']
            #print(self.folders)
            if len(self.folders) == 0:
                error_dialog = QtWidgets.QErrorMessage()
                error_dialog.showMessage("Choose a folder with the correct distribution:"+"\n"+" 1) Biofilm 2) Reference")
                error_dialog.setWindowTitle("Error Message")
                error_dialog.exec_()
            else:
                self.b_files = [self.directory+'//'+file for file in os.listdir(self.directory)]
                self.c_files = [self.directory+'//'+file for file in os.listdir(self.directory)]
                self.just_b_filename = [file for file in os.listdir(self.directory)]
                self.just_c_filename = [file for file in os.listdir(self.directory)]
        
                if(len(self.c_files)>0 and len(self.b_files)>0):
                    self.next_button.setHidden(False)
                    self.next_button2.setHidden(False)
                    self.previous_button.setHidden(False)
                    self.previous_button2.setHidden(False)
                    self.previous_button.setEnabled(False)
                    self.previous_button2.setEnabled(False)
                    self.filename_label.setText("Reference Well "+self.just_b_filename[self.ref_index].split('.')[0])
                    self.filename_label2.setText("Growth Well "+self.just_c_filename[self.bio_index].split('.')[0])
                    self.update_image_label(self.b_files[self.ref_index], True)
                    self.update_image_label(self.c_files[self.bio_index], False)                    
                    self.first_step.setStyleSheet("border: 1px solid black")
                    self.second_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")
                    self.ROI_button.setEnabled(True)
                    self.previous_folder.setEnabled(True)
                    self.next_folder.setEnabled(True)
                    self.check_csv()
                    self.geometry_groupbox.setEnabled(True)
                    
                    #self.choose_button.setEnabled(False)

    def check_csv(self):
        experimento= self.directory.split('//')[-1]
        #filename = r''+self.export_name#self.location+experimento+'_results.csv'
        #filename = filename.replace("//","\\")
        #self.export_name = filename

        try:
            self.df = pd.read_csv(self.export_name)
            self.export_list = [self.df.loc[x,:].values.tolist() for x in range(0,self.df.shape[0])]
            rows = self.df.shape[0]
            print(self.df)
        except:
            self.export_list = list()
            rows = 0
        self.state_label.setVisible(True)
        self.update_state_label(experimento, rows)

    def update_state_label(self, exp, rows):
    
        filename = self.export_name.split('/')[-1]
        if rows>1:
            end = 'rows'
        else:
            end = 'row'
        self.state_label.setText('... on file '+filename + ' - currently '+str(rows)+end)
        #self.table_button.setEnabled(True)
                    
    def select_roi(self, order):
        '''
        This function allows the manual segmentation of the ROI.
        It calls another function (selection) and return the coordinates of the ROI.
        Finally, it shows the result images in the main UI.
        '''

        isCircular = self.circular_radio.isChecked()
        isSquare = self.square_radio.isChecked()
        
        if order == 0:
            #print(order)
            ref = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
            bio = cv2.cvtColor(np.array(self.image2), cv2.COLOR_RGB2BGR)
            if self.initial_round == True:
                QtWidgets.QMessageBox.about(self,"Warning Message", "1) You must press Enter once you have selected the region of interest."
                                        +"\n"+"2) If you're unsure of the selection, you can press the 'Segment Well' Button again."
                                        +"\n"+"3) Avoid closing the Segmentation Window or the main window without having made a selection, the program will close."
                                        +"\n"+"4) You must segment both images to finish the process.")

            if isCircular:
                just_ref = circular_selection(ref,0)
                just_bio = circular_selection(bio,1)
            else:
                just_ref = square_selection(ref,0)
                just_bio = square_selection(bio,1)
                
            ref_rgb = cv2.cvtColor(just_ref, cv2.COLOR_BGR2RGB)
            bio_rgb = cv2.cvtColor(just_bio, cv2.COLOR_BGR2RGB)

            self.update_ROI_pair([ref_rgb, bio_rgb], 2)
        
            self.color_groupbox.setEnabled(True)
            self.next_step.setEnabled(True)
            self.new_ref_button.setVisible(True)
            self.new_growth_button.setVisible(True)
            self.ROI_button.setVisible(False)
            self.contador_ref = 1
        
            
        elif order == 1:
            
            image = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
            if isCircular:
                just_ROI = circular_selection(image,order-1)
            else:
                just_ROI = square_selection(image,order-1)
            ref_rgb = cv2.cvtColor(just_ROI, cv2.COLOR_BGR2RGB)
            self.update_one_ROI(order, ref_rgb)

        else:

            image = cv2.cvtColor(np.array(self.image2), cv2.COLOR_RGB2BGR)
            if isCircular:
                just_ROI = circular_selection(image,order-1)
            else:
                just_ROI = square_selection(image,order-1)
            bio_rgb = cv2.cvtColor(just_ROI, cv2.COLOR_BGR2RGB)
            self.update_one_ROI(order, bio_rgb)

        self.second_step.setStyleSheet("border: 1px solid black")
        self.third_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")
        #Show scale
        self.show_scale()
        
    def show_scale(self):
        '''
        This function select the channel of interest (Green or Gray) and then update the pair
        of color images in the main UI.
        '''
        self.next_step.setEnabled(True)
        img = np.array(self.roi)
        img2 = np.array(self.roi2)
        
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

        self.update_ROI_pair([color, color2], 3)

    def update_one_ROI(self, order, image):
        if order == 1:
            self.roi = Image.fromarray(image)
            roi_qt = ImageQt.ImageQt(self.roi)
            pix_map = QtGui.QPixmap.fromImage(roi_qt)
            self.roi_map = pix_map.scaledToHeight(240)
            self.image_label3.setPixmap(self.roi_map)
            
        else:
            self.roi2 = Image.fromarray(image)
            roi_qt = ImageQt.ImageQt(self.roi2)
            pix_map = QtGui.QPixmap.fromImage(roi_qt)
            self.roi_map2 = pix_map.scaledToHeight(240)
            self.image_label4.setPixmap(self.roi_map2)
            

    def update_ROI_pair(self, imgs, col=2):
        '''
        This function updates both cropped images from the second and third step.
        '''

        if col==2:
            self.roi = Image.fromarray(imgs[0])
            self.roi2= Image.fromarray(imgs[1])
            roi_qt = ImageQt.ImageQt(self.roi)
            roi_qt2 = ImageQt.ImageQt(self.roi2)

            pix_map = QtGui.QPixmap.fromImage(roi_qt)
            pix_map2 = QtGui.QPixmap.fromImage(roi_qt2)

            self.roi_map = pix_map.scaledToHeight(240)
            self.roi_map2 = pix_map2.scaledToHeight(240)

            self.image_label3.setPixmap(self.roi_map)
            self.image_label4.setPixmap(self.roi_map2)

        else:
            conv_qt = ImageQt.ImageQt(Image.fromarray(imgs[0]))
            conv_qt2 = ImageQt.ImageQt(Image.fromarray(imgs[1]))

            pix_map = QtGui.QPixmap.fromImage(conv_qt)
            pix_map2 = QtGui.QPixmap.fromImage(conv_qt2)

            self.conv_map = pix_map.scaledToHeight(240)
            self.conv_map2 = pix_map2.scaledToHeight(240)

            self.image_label5.setPixmap(self.conv_map)
            self.image_label6.setPixmap(self.conv_map2)


        
    def selecting_color(self):
        '''
        This function enables the thresholding button, once the user has decided
        in a particular channel of interest.
        '''
        isGray = self.radio_gray.isChecked()
        isGreen = self.radio_green.isChecked()

        if isGray:
            self.color_selection = "Gray"
        if isGreen:
            self.color_selection = "Green"

        self.thresh_button.setEnabled(True)
        self.third_step.setStyleSheet("border: 1px solid black")
        self.fourth_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")        
        
    def thresholding(self):
        '''
        This function update the image color array based on the user selection.
        Then, it calls the slider window so the user can interact with it
        and choose a threshold value.
        '''
        if self.color_selection == "Gray":
            self.image_color = cv2.cvtColor(np.array(self.roi), cv2.COLOR_RGB2GRAY)
            self.image_color2 = cv2.cvtColor(np.array(self.roi2), cv2.COLOR_RGB2GRAY)
        elif self.color_selection == "Green":
            self.image_color = np.array(self.roi)[:,:,1]
            self.image_color2 = np.array(self.roi2)[:,:,1]


        self.slider_window = SliderWindow(self.image_color, self.color_selection)
        self.slider_window.show()
        self.fourth_step.setStyleSheet("border: 1px solid black")
        self.fifth_step.setStyleSheet("background-color: lightgreen; border: 1px solid black")
        #self.result_button.setEnabled(True)
        #self.ROI_button.setEnabled(True)
        self.remove_button.setEnabled(True)

    def execute_thresh(self):

        if self.color_selection == 'Gray':
            self.image_color = cv2.cvtColor(np.array(self.roi), cv2.COLOR_RGB2GRAY)
            self.image_color2 = cv2.cvtColor(np.array(self.roi2), cv2.COLOR_RGB2GRAY)
            self.show_results()
        elif self.color_selection == 'Green':
            #print('A')
            self.image_color = np.array(self.roi)[:,:,1]
            self.image_color2 = np.array(self.roi2)[:,:,1]
            self.show_results()
        
    def show_results(self):
        '''
        This function perform all the operations neccessary for the image analysis
        and extracts the features of interest.
        Then it shows the canvas with the result images and their corresponding histogram.
        '''
        self.threshold = self.slider_window.slider_value
        #print('B')
        #print(self.threshold)
        _,wh = cv2.threshold(self.image_color, self.threshold, 255,cv2.THRESH_BINARY_INV)
        res_wh = cv2.bitwise_and(self.image_color, self.image_color, mask = wh)
        
        _, test = cv2.threshold(self.image_color2, self.threshold, 255, cv2.THRESH_BINARY_INV)
        res = cv2.bitwise_and(self.image_color2, self.image_color2, mask = test)

        total_area = len(self.image_color2[self.image_color2!=0])
        percentage = len(res[res!=0])*100/total_area

        #print('C')
        
        global_mean = np.mean(self.image_color2[self.image_color2>0])
        global_median = np.median(self.image_color2[self.image_color2>0])
        global_skew = skew(self.image_color2[self.image_color2>0])
        global_kurt = kurtosis(self.image_color2[self.image_color2>0])
        just_res = res[res>0]
        res_mean = np.mean(just_res)
        res_median = np.median(just_res)

        #print('D')
        
        just_wh = self.image_color[self.image_color>0]#todo
        wh_mean = np.mean(just_wh)
                
        if (self.result_canvas == None):
            self.result_canvas = MplCanvas(dpi=100)
            self.toolbar = NavigationToolbar(self.result_canvas, self)
            self.fifth_box.addWidget(self.toolbar)
            self.fifth_box.addWidget(self.result_canvas)

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

        self.temp = list()

        name = self.just_c_filename[self.bio_index].split('.')[0]

        today = str(date.today().strftime('%d/%m/%y'))
        
        self.temp = [self.just_c_filename[self.bio_index][0], name.split('_')[0][1:], self.just_c_filename[self.bio_index],self.just_b_filename[self.ref_index], self.color_selection, self.threshold, percentage, global_mean, global_median, res_mean,res_median,global_skew,global_kurt, today]

        self.setFixedWidth(2220)
        
        self.radio_gray.setEnabled(True)
        self.radio_green.setEnabled(True)
        self.add_button.setEnabled(True)
        #self.export_button.setEnabled(True)

    def add_result(self):
        '''
        This function creates a pandas Dataframe that contains all the features extracted of the images used during the analysis.
        It updates with each comparison.
        '''
        
        self.export_list.append(self.temp)

        self.df = pd.DataFrame(self.export_list)
        self.df.columns = ['Row', 'Column', 'File', 'Control File', 'Color', 'Thresh', 'Prop', 'Global Mean', 'Global Median', 'Bio Mean', 'Bio Median', 'Global Skew', 'Global Kurt', 'Date']
        self.update_state_label(self.directory.split('//')[-1], self.df.shape[0])
        self.export_results()

        if self.initial_round == True:
            QtWidgets.QMessageBox.about(self,"Notification","The values have already been added to the .csv file, Change to another well of your choice."
                                        +"\n"+"Please follow the same step order as you have done, going from left to right."
                                        +"\n"+"Do not skip any step.")

    def export_results(self):
        '''
        This function allows the export of the Dataframe once the user has decided to stop using the UI.
        The export location will be the same directory of the BAS_ver6.py or .exe for ease of location.
        '''

        #experimento= self.directory.split('//')[-1]
        #filename = r''+self.location+experimento+'_results.csv'
        #filename = filename.replace("//","\\")
        #self.export_name = filename

        self.df.to_csv(self.export_name, index=False, header=True)

        if self.initial_round == True:
            QtWidgets.QMessageBox.about(self,"Notification","The file have been exported"+
                                        "\n"+"Overwrites any other file with the same filename, be careful.")
            self.initial_round == False
    def show_dataframe(self):
        try:
            self.table_window = TableWindow(self.df)
            self.table_window.show()
        except:
            pass
    
    def update_image_label(self, file, ref=False):
        '''
        This function updates both images of the first step (image exploration) and allows the user to
        freely choose the image of interest (reference and biofilm).
        '''
        if type(file)==str:
            image = cv2.imread(file)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
            if(ref==True):
                self.image = Image.fromarray(image)
                self.pix_map = QtGui.QPixmap(file)
                self.pix_map = self.pix_map.scaledToHeight(240)
                self.image_label.setPixmap(self.pix_map)
            else:
                self.image2 = Image.fromarray(image)
                self.pix_map2 = QtGui.QPixmap(file)
                self.pix_map2 = self.pix_map2.scaledToHeight(240)
                self.image_label2.setPixmap(self.pix_map2)

            
    def next_ref(self):
        '''
        This function increment the index of the image of interest and shows the next reference image
        in the main UI.
        '''
        ref_total = len(self.b_files)
        if(self.ref_index <= ref_total-1):
            self.ref_index +=1
            self.previous_button.setEnabled(True)
        if(self.ref_index == ref_total -1):
            self.next_button.setEnabled(False)
        self.filename_label.setText("Reference Well "+self.just_b_filename[self.ref_index].split('.')[0])
        self.update_image_label(self.b_files[self.ref_index], True)

    def previous_ref(self):
        '''
        This function disminish the index of the image of interest and shows the previous reference
        image in the main UI.
        '''
        ref_total = len(self.b_files)
        if(self.ref_index >= 0):
            self.next_button.setEnabled(True)
            self.ref_index -=1
        if(self.ref_index == 0):
            self.previous_button.setEnabled(False)
        self.filename_label.setText("Reference Well "+self.just_b_filename[self.ref_index].split('.')[0])
        self.update_image_label(self.b_files[self.ref_index], True)

    def next_bio(self):
        '''
        This funtion increment the index of the image of interest and shows the next biofilm image
        in the main UI.
        '''
        bio_total = len(self.c_files)
        if(self.bio_index <= bio_total-1):
            self.bio_index +=1
            self.previous_button2.setEnabled(True)
        if(self.bio_index == bio_total -1):
            self.next_button2.setEnabled(False)        
        self.filename_label2.setText("Growth Well "+self.just_c_filename[self.bio_index].split('.')[0])
        self.update_image_label(self.c_files[self.bio_index], False)
        
    def previous_bio(self):
        '''
        This functions disminish the index of the image of interest and shows the previous biofilm
        image in the main UI.
        '''
        bio_total = len(self.c_files)
        if(self.bio_index > 0):
            self.bio_index -=1
            self.next_button2.setEnabled(True)
        if(self.bio_index == 0):
            self.previous_button2.setEnabled(False)
        self.filename_label2.setText("Growth Well "+self.just_c_filename[self.bio_index].split('.')[0])
        self.update_image_label(self.c_files[self.bio_index], False)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    main_widget = ScreenHandler()
    app.exec_()

