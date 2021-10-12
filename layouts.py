from utils import *
from PyQt5 import QtCore, QtGui, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

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
    def __init__(self, image, *args, **kwargs):
        '''
        During the initilization, this class creates all the necessary attributes
        and acommodates the layout to show all the information in order.
        '''
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
        '''
        This function draws the image histogram in the canvas that is showed in the
        window.
        '''
        img = np.array(self.image)
        self.canvas.fig.clf()
        self.canvas.ax1 = self.canvas.fig.add_subplot(111)

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

    def draw_line(self):
        '''
        This function draws a vertical line when the user uses the input box
        is an alternative way of showing the threshold.
        '''
        value = int(self.user_input.text())
        img = np.array(self.image)
        self.canvas.fig.clf()
        self.canvas.ax1 = self.canvas.fig.add_subplot(111)
        vals, bins, _ = self.canvas.ax1.hist(img.flatten(),256, [1,255])
        self.canvas.ax1.axvline(value, color = 'k', linestyle= 'dashed', linewidth=1)
        self.canvas.draw()
        self.slider.setSliderPosition(value)

    def set_thresh(self):
        '''
        This function closes the slider window once the user has chosen the
        threshold.
        It returns the value to the main window
        '''
        self.slider_value = int(self.slider.value())
        self.close()
        return self.slider.value()
