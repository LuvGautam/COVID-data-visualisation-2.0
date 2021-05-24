'''
COVID19 DATA VISUALISATION

GUI application to visualize COVID19 data and display latest news
of the selected location.
'''

# Import Python Standard Libraries
import sys
import os
from datetime import datetime
import math
import locale
import inspect
import requests
from io import BytesIO

# Import Database related libraries 
from sqlalchemy import create_engine

import pandas as pd

import numpy as np

# Import graph plotting libraries
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
from matplotlib.dates import num2date, DateFormatter, MonthLocator
from matplotlib.ticker import FuncFormatter
from matplotlib import font_manager

import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader

import geopandas as gpd
from shapely.geometry import Point, Polygon

import seaborn as sns

# Import QApplication and the required widgets from PyQt5.QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QLineEdit, QLabel, QPushButton,
                             QTabWidget, QFrame, QComboBox,
                             QDateEdit, QTableWidget, QTableWidgetItem,
                             QScrollArea, QSpacerItem, QTabBar)
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import (QRunnable, QThreadPool, pyqtSlot,
                          pyqtSignal, QObject)

# Import function to update database
from covid19data import update_covid19_database

__version__ = '2.0'
__author__ = 'Luv Gautam'

# Set seaborn dark grey theme for seaborn plots 
#sns.set_theme(style="darkgrid")
sns.set()

# Set 'Ubuntu' as default font for all plots
font_manager.fontManager.addfont(r'.\app-resources\Ubuntu-Regular.ttf')
plt.rcParams['font.family'] = 'Ubuntu'


# Create a class to control the Tabs of QTabWidget 
class TabBar(QTabBar):
    def __init__(self, *args, **kwargs):
        QTabBar.__init__(self, *args, **kwargs)
        self.setStyleSheet('''
            QTabBar::tab {
                color: black;
                background: white;
                font: 13pt;
                min-width: 7em;
                min-height: 1.8em;
                }
                
            QTabBar::tab:!selected {
                margin-top: 4px;
                /*border-bottom: 2px solid rgb(94, 189, 247)*/;
                }

            QTabBar::tab:hover {
                background: rgb(40, 40, 40);
                color: rgb(242, 242, 242);
                }

            QTabBar::tab:selected {
                position:relative;
                border-bottom: 3px solid black;
                font-size: 13pt;
                font-weight: 600;
                }

            QTabBar {
                qproperty-drawBase: 0;
                }
            ''')

# Create a subclass of QTabWidget to setup the application's tabs
class TabWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        QTabWidget.__init__(self, *args, **kwargs)
        self.setTabBar(TabBar(self))
        #self.setTabPosition(QTabWidget.West)
##        self.setStyleSheet('''
##            QTabWidget::pane {
##                border-top: 10px solid blue;
##                }
##            ''')

# Create a subclass of QComboBox to use in options frame
class ComboBox(QComboBox):
    def __init__(self, *args, **kwargs):
        super(ComboBox, self).__init__(*args, **kwargs)

        self.setStyleSheet('''
            QComboBox {
                border: 1px solid white;
                /*border-radius: 3px;*/
                /*padding: 1px 18px 1px 3px;*/
                min-width: 6em;
                min-height: 1.2em;
                font: 10pt;
                background: rgb(40, 40, 40);
                color: rgb(242, 242, 242);
                }

            QComboBox:disabled {
                color: silver;
                background: rgb(120, 120, 120);
                border: 1px solid rgb(242, 242, 242);
                }

            QComboBox::drop-down {
                /*subcontrol-origin: padding;*/
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: white;
                border-left-style: solid;
                }

            QComboBox::drop-down:disabled {
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: silver;
                border-left-style: solid;
                }
            

            QComboBox::down-arrow {
                image: url(app-resources/arrow-down-w.png);
                }

            QComboBox::down-arrow:disabled {
                image: url(app-resources/arrow-down-s.png);
                }

            QComboBox::down-arrow:on {
                top: 1px;
                left: 1px;
                }

            QComboBox QAbstractItemView {
                border: 2px solid white;
                selection-background-color: rgb(40, 40, 40);
                selection-color: rgb(242, 242, 242);
                }

            QScrollBar:vertical {
                border: none;
                background: white;
                width: 14px;
                /*margin: 0px 2px 0px 0px;*/
                }
                 
            QScrollBar::handle:vertical {
                background: rgba(40, 40, 40, 0.3);
                border-radius: 7px;
                min-height: 40px;
                }

            QScrollBar::handle:vertical:pressed {
                background: rgba(40, 40, 40, 0.8);
                min-height: 40px;
                }

            QScrollBar::up-arrow:vertical {
                height: 0px;
                width: 0px;
                }

            QScrollBar::down-arrow:vertical {
                height: 0px;
                width: 0px;
                }
                 
            QScrollBar::add-line:vertical {
                border: none;
                background: white;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                }

            QScrollBar::sub-line:vertical {
                border: none;
                background: white;
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                }
            ''')

# Create a subclass of QDateEdit to use in options frame
class DateEdit(QDateEdit):
    def __init__(self, *args, **kwargs):
        super(DateEdit, self).__init__(*args, **kwargs)

        self.setStyleSheet('''
            QDateEdit {
                border: 1px solid white;
                min-width: 6em;
                min-height: 1.2em;
                font: 10pt;
                background: rgb(40, 40, 40);
                color: rgb(242, 242, 242);
                }

            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: white;
                border-left-style: solid;
                }
            
            QDateEdit::down-arrow {
                image: url(app-resources/arrow-down-w.png);
                }

            QDateEdit::down-arrow:on {
                top: 1px;
                left: 1px;
                }

            QDateEdit QAbstractItemView {
                font: 8pt;
                border: 2px solid white;
                selection-background-color: rgb(40, 40, 40);
                selection-color: rgb(242, 242, 242);
                }

            QCalendarWidget QToolButton {
                height: 1.3em;
                color: rgb(242, 242, 242);
                font-size: 10pt;
                icon-size: 18px, 18px;
                background-color: rgb(40, 40, 40);
                margin: 0px;
                }
                
            QCalendarWidget QMenu {
                color: rgb(242, 242, 242);
                font-size: 10pt;
                background-color: rgb(40, 40, 40);
                }

            QCalendarWidget QSpinBox {
                padding-right: 12px; /* make room for the arrows */
                border: 1px solid white;
                font-size: 10pt;
                color: rgb(242, 242, 242);
                background-color: rgb(40, 40, 40);
                selection-background-color: rgb(242, 242, 242);
                selection-color: black;
                padding: 2px 8px 2px 0px;
                }
            
            QCalendarWidget QSpinBox::up-button {
                /*subcontrol-origin: border;*/
                subcontrol-position: top right;
                /*width: 12px;*/
                border-left: 1px solid white;
                }
            
            QCalendarWidget QSpinBox::down-button {
                /*subcontrol-origin: padding;*/
                subcontrol-position: bottom right;
                /*width: 12px;*/
                border-left: 1px solid white;
                }
                
            QCalendarWidget QSpinBox::up-arrow {
                image: url(app-resources/arrow-up-w12.png);
                /*width: 8px;
                height: 8px;*/
                }
                
            QCalendarWidget QSpinBox::down-arrow {
                image: url(app-resources/arrow-down-w12.png);
                /*width: 8px;
                height: 8px;*/
                }

            QCalendarWidget QSpinBox::down-button:pressed {
                top: 1px;
                left: 1px;
                }

            QCalendarWidget QSpinBox::up-button:pressed {
                bottom: 1px;
                left: 1px;
                }

            QCalendarWidget QWidget#qt_calendar_navigationbar {
                max-height: 1.2em;
                background-color: rgb(40, 40, 40);
                }

            QCalendarWidget QToolButton#qt_calendar_prevmonth {
                qproperty-icon: url(app-resources/arrow-left-w24.png);
                }
                
            QCalendarWidget QToolButton#qt_calendar_nextmonth {
                qproperty-icon: url(app-resources/arrow-right-w24.png);
                }
            ''')

# Create a subclass of QTableWidget to display data in tabular form
class TableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):

        QTableWidget.__init__(self, *args, **kwargs)

        self.horizontalHeader().setSortIndicatorShown(True)

        self.setStyleSheet('''
            QWidget {
                background-color: white;
                color: black;
                border: none;
                }

            QTableWidget {
                margin: 15px 0px 20px 0px;
                }

            QHeaderView::section {
                background-color: rgb(40, 40, 40);
                color: rgb(242, 242, 242);
                padding: 5px;
                font-size: 12pt;
                border-style: none;
                border-bottom: 1px solid white;
                border-right: 1px solid white;
                }

            QHeaderView::section:horizontal {
                border-top: 1px solid white;
                }

            QHeaderView::section:horizontal:pressed {
                border-top: 1px solid white;
                background-color: white;
                color: black;
                }

            QHeaderView::section:vertical {
                border-left: 1px solid white;
                }

            QHeaderView::down-arrow {
                subcontrol-origin: content;
                subcontrol-position: bottom right;
                image: url(app-resources/arrow-down-w16.png);
                margin: 0px 3px 3px 0px;
                height: 8px;
                width: 8px;
                }

            QHeaderView::up-arrow {
                subcontrol-origin: content;
                subcontrol-position: bottom right;
                image: url(app-resources/arrow-up-w16.png);
                margin: 0px 3px 3px 0px;
                height: 8px;
                width: 8px;
                }

            QTableWidget {
                gridline-color: silver;
                font-size: 10pt;
                }

            QTableWidget QTableCornerButton::section {
                background-color: rgb(40, 40, 40);
                border: 1px solid white;
                }

            QScrollBar:vertical {
                border: none;
                background: white;
                width: 16px;
                /*margin: 0px 2px 0px 0px;*/
                }
                 
            QScrollBar::handle:vertical {
                background: rgba(40, 40, 40, 0.3);
                border-radius: 7px;
                min-height: 60px;
                }

            QScrollBar::handle:vertical:pressed {
                background: rgba(40, 40, 40, 0.8);
                min-height: 60px;
                }

            QScrollBar::up-arrow:vertical {
                height: 0px;
                width: 0px;
                }

            QScrollBar::down-arrow:vertical {
                height: 0px;
                width: 0px;
                }
                 
            QScrollBar::add-line:vertical {
                border: none;
                background: white;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                }

            QScrollBar::sub-line:vertical {
                border: none;
                background: white;
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            ''')

    def setData(self, dataFrame, columns):

        self.setRowCount(len(dataFrame))
        self.setColumnCount(len(columns))

        data = dataFrame.values

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                if isinstance(item, pd._libs.tslibs.timestamps.Timestamp):
                    date = item.to_pydatetime()
                    cellData = QTableWidgetItem()
                    cellData.setData(Qt.DisplayRole, QtCore.QDate(date.year, date.month, date.day))
                else:
                    cellData = QTableWidgetItem()
                    cellData.setData(Qt.EditRole, QtCore.QVariant(item))
                cellData.setFlags(cellData.flags() &  ~Qt.ItemIsEditable)
                self.setItem(i, j, cellData)

        self.sortItems(0, Qt.AscendingOrder)

        def formatColumnName(name):
            l = name.split('_')
            l = list(map(lambda x: x.title(), l))
            return ' '.join(l)

        self.setHorizontalHeaderLabels(list(map(formatColumnName, columns)))
        self.resizeColumnsToContents()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setMaximumSize(self.getQTableWidgetSize())
        self.setMinimumSize(self.getQTableWidgetSize())

    def getQTableWidgetSize(self):
        w = self.verticalHeader().width() + 4  # +4 seems to be needed
        for i in range(self.columnCount()):
            w += self.columnWidth(i)  # seems to include gridline (on my machine)
        h = self.horizontalHeader().height() + 4
        for i in range(self.rowCount()):
            h += self.rowHeight(i)
        return QtCore.QSize(w+16, 677)

# Create a subclass of QScrollArea to make tabs scrollable
class ScrollArea(QScrollArea):
    def __init__(self, *args, **kwargs):
        QScrollArea.__init__(self, *args, **kwargs)

        self.setStyleSheet('''
            QScrollArea {
                border: none;
                background: white;
                }

            QScrollBar:vertical {
                border: none;
                background: white;
                width: 18px;
                margin: 10px 2px 10px 0px;
                }
                 
            QScrollBar::handle:vertical {
                background: rgba(40, 40, 40, 0.3);
                border-radius: 8px;
                min-height: 80px;
                }

            QScrollBar::handle:vertical:pressed {
                background: rgba(40, 40, 40, 0.8);
                min-height: 80px;
                }

            QScrollBar::up-arrow:vertical {
                height: 0px;
                width: 0px;
                }

            QScrollBar::down-arrow:vertical {
                height: 0px;
                width: 0px;
                }
                 
            QScrollBar::add-line:vertical {
                border: none;
                background: white;
                height: 0px;
                subcontrol-position: bottom;
                subcontrol-origin: margin;
                }

            QScrollBar::sub-line:vertical {
                border: none;
                background: white;
                height: 0px;
                subcontrol-position: top;
                subcontrol-origin: margin;
                }

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                }
            
            QScrollBar:horizontal {
                border: none;
                background: white;
                height: 18px;
                margin: 0px 10px 2px 10px;
                }
                 
            QScrollBar::handle:horizontal {
                background: rgba(40, 40, 40, 0.3);
                border-radius: 8px;
                min-width: 80px;
                }

            QScrollBar::handle:horizontal:pressed {
                background: rgba(40, 40, 40, 0.8);
                min-width: 80px;
                }

            QScrollBar::left-arrow:horizontal {
                height: 0px;
                width: 0px;
                }

            QScrollBar::right-arrow:horizontal {
                height: 0px;
                width: 0px;
                }
                 
            QScrollBar::add-line:horizontal {
                border: none;
                background: white;
                height: 0px;
                subcontrol-position: left;
                subcontrol-origin: margin;
                }

            QScrollBar::sub-line:horizontal {
                border: none;
                background: white;
                height: 0px;
                subcontrol-position: right;
                subcontrol-origin: margin;
                }

            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
                }
            ''')

    def wheelEvent(self, event):
##        print('hello')
##        print(event.pixelDelta())
##        print(event.angleDelta().y())
        val = self.verticalScrollBar().value()
        #print(event.buttons())
##        scrollbarHor = self.horizontalScrollBar()
##        scrollbarVer = self.verticalScrollBar()

        if event.angleDelta().y() < 0:
            self.verticalScrollBar().setValue(val+926)
        else:
            self.verticalScrollBar().setValue(val-926)

class horizontalLine(QFrame):
    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)

        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Plain)
        #self.setFixedHeight(10)
        self.setLineWidth(3)

class verticalLine(QFrame):
    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)

        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Plain)
        #self.setFixedHeight(10)
        self.setLineWidth(3)

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = pyqtSignal()
    #error = pyqtSignal(tuple)
    #result = pyqtSignal(object)

# Create a subclass of QRunnable to make worker objects to be used in multi threading
class Worker(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        

    @pyqtSlot()
    def run(self):
        self.function(*self.args, **self.kwargs)
        self.signals.finished.emit()


# Create a subclass of QMainWindow to setup the application's GUI
class CovidAppUi(QMainWindow):
    """CovidApp's View (GUI)."""
    def __init__(self, covid_app):
        """View initializer."""
        super().__init__()

        self.covid_app = covid_app
     
        # Connect to MySQL DB
        self.connectToDb()

        # Create neccessary Data Frames
        self.indiaTotalDataFrame = pd.read_sql('india_total', con=self.engine, index_col='ID')
        self.indiaTotalDataFrame.index.name = None

        self.indiaDailyDataFrame = pd.read_sql('india_daily', con=self.engine, index_col='ID')
        self.indiaDailyDataFrame.index.name = None

        self.globalDataFrame = pd.read_sql('global', con=self.engine, index_col='ID')
        self.globalDataFrame.index.name = None

        # Dispose all connections in connection pool
        self.engine.dispose()
        
        # Create thread pool to execute various "workers" simultaneuosly
        self.threadPool = QThreadPool()

        # Set timer to update database
        self.databaseUpdateTimer = QtCore.QTimer()
        self.updateDatabaseWorker = Worker(self.updateDatabase)
        self.databaseUpdateTimer.singleShot(30000, lambda: self.threadPool.start(self.updateDatabaseWorker))
        
        # Set main window's properties
        self.setWindowTitle('COVID19 Data Visualisation')
        self.setWindowIcon(QtGui.QIcon(r'.\app-resources\logo.png'))
        self.setStyleSheet('''
            QMainWindow {
                background: rgb(40, 40, 40);
                }

            QToolTip {
                border: 1px solid black;
                padding: 4px;
                border-radius: 3px;
                background: rgb(255, 255, 255);
                color: black;
                font-size: 10pt;
                }
            ''')
        
        # Set the central widget
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        # Set the layout of main window
        self.generalLayout = QGridLayout()
        self.generalLayout.setAlignment(Qt.AlignTop)
        self.generalLayout.setVerticalSpacing(0)
        self.centralWidget.setLayout(self.generalLayout)

        # Set tab widget and tabs for main window
        self.tabWidget = TabWidget()

        self.graphTab = QWidget(objectName='graphTab')
        self.tableTab = QWidget(objectName='tableTab')
        self.newsTab = QWidget(objectName='newsTab')

        self.graphTabScrollArea = ScrollArea()
        self.graphTabScrollArea.setWidgetResizable(True)
        
        self.tableTabScrollArea = ScrollArea()
        self.tableTabScrollArea.setWidgetResizable(True)
        
        self.newsTabScrollArea = ScrollArea()
        self.newsTabScrollArea.setWidgetResizable(True)

        self.graphTabScrollArea.setWidget(self.graphTab)
        self.tableTabScrollArea.setWidget(self.tableTab)
        self.newsTabScrollArea.setWidget(self.newsTab)

        # Set all three tabs(instantiate the widget objects)
        self.setTableTab()

        self.setGraphTab()

        self.setNewsTab()

        self.tabWidget.addTab(self.graphTabScrollArea, "Graphs")
        self.tabWidget.addTab(self.tableTabScrollArea, "Data Tables")
        self.tabWidget.addTab(self.newsTabScrollArea, "News")
        
        self.tabWidget.setStyleSheet('''
            QTabWidget::pane {
                background: white;
                /*border: 2px solid rgb(94, 189, 247);*/
                /*left: 12px;*/
                }

            /*QTabWidget::tab-bar {
                top: 2px;
                }*/

            #graphTab, #tableTab, #newsTab {
                background: white;
                }

            /*QTabWidget {
                background: rgb(246, 246, 246);
                }*/
            ''')

        # Set options heading label and frame
        self.optionsHeadFrame = QFrame(objectName='optionsHeadFrame')
        self.optionsHeadLabel = QLabel('Options', objectName='optionsHeadLabel')
        self.optionsHeadFrameLayout = QVBoxLayout()

        self.optionsHeadLabel.setStyleSheet('''
            QLabel#optionsHeadLabel {
                color: rgb(242, 242, 242);
                /*text-shadow: -1px 0 black, 0 1px black, 1px 0 black, 0 -1px black;*/
                font: 16pt;
                font-weight: 500;
                min-width: 4em;
                min-height: 2em;
                }
            ''')
        self.optionsHeadLabel.setAlignment(Qt.AlignCenter)

        self.optionsHeadFrameLayout.addWidget(self.optionsHeadLabel)

        self.optionsHeadFrame.setStyleSheet('''
            #optionsHeadFrame {
                border-top: 2px solid white;
                border-left: 2px solid white;
                border-right: 2px solid white;
                }
            ''')
        
        self.optionsHeadFrame.setLayout(self.optionsHeadFrameLayout)

        # Set options body frame and layout
        self.optionsBodyFrame = QFrame(objectName='optionsBodyFrame')
        self.optionsBodyFrameLayout = QGridLayout()
        self.optionsBodyFrameLayout.setAlignment(Qt.AlignTop)
        self.optionsBodyFrameLayout.setVerticalSpacing(15)
        self.optionsBodyFrameLayout.setHorizontalSpacing(0)

        self.optionsBodyFrame.setStyleSheet('''
            #optionsBodyFrame {
                border-top: 0px;
                border-left: 2px solid white;
                border-right: 2px solid white;
                border-bottom: 2px solid white;
                }
            ''')

        self.optionsBodyFrame.setLayout(self.optionsBodyFrameLayout)

        # Set option-location label
        self.locationLabel = QLabel('Select Location', objectName='locationLabel')
        self.locationLabel.setStyleSheet('''
            #locationLabel {
                font: 14pt;
                color: rgb(242, 242, 242);
                }
            ''')       
        
        # Set option-state combobox and label
        self.stateComboBox = ComboBox(objectName='stateComboBox')
        self.stateList = np.sort(self.indiaTotalDataFrame['state'].unique()).tolist()
        self.stateList.remove('Total')
        self.stateList = ['<-- Select State -->'] + self.stateList
        self.stateComboBox.setEditable(False)
        self.stateComboBox.addItems(self.stateList)
        self.stateComboBox.setCurrentIndex(0)
        self.stateComboBox.model().item(0).setEnabled(False)
        self.stateComboBox.setEnabled(False)
        self.stateComboBox.setToolTip('Sates available for <b>India</b> only.')

        self.stateComboBox.currentTextChanged.connect(self.stateComboBoxTextChange)

        self.stateLabel = QLabel('State : ', objectName='stateLabel')

        self.stateLabel.setStyleSheet('''
            #stateLabel {
                font: 12pt;
                color: rgb(242, 242, 242);
                }
            ''')

        # Set option-country combobox and label
        self.countryComboBox = ComboBox(objectName='countryComboBox')
        self.countryList = np.sort(self.globalDataFrame['country'].unique()).tolist()
        for loc in ['Europe', 'Asia', 'North America', 'European Union', 'South America', 'Africa', 'World']:
            self.countryList.remove(loc)
        #self.countryList.remove('World')
        self.countryList = ['<-- Select Country -->', 'World'] + self.countryList
        self.countryComboBox.setEditable(False)
        self.countryComboBox.addItems(self.countryList)
        self.countryComboBox.setCurrentIndex(0)
        self.countryComboBox.model().item(0).setEnabled(False)
        #self.countryComboBox.addItem(QIcon(r'.\app-resources\arrow-down-s.png'), 'f')

        self.countryComboBox.currentTextChanged.connect(self.countryComboBoxTextChange)

        self.countryLabel = QLabel('Country : ', objectName='countryLabel')

        self.countryLabel.setStyleSheet('''
            #countryLabel{
                font: 12pt;
                color: rgb(242, 242, 242);
                }
            ''')

        # Set option-period label
        self.periodLabel = QLabel('Select Time Period', objectName='periodLabel')
        self.periodLabel.setStyleSheet('''
            #periodLabel {
                font: 14pt;
                /*background: rgb(94, 189, 247);*/
                color: rgb(242, 242, 242);
                margin-top: 20px;
                }
            ''')

        # Set option-to-from label
        self.fromLabel = QLabel('From:', objectName='fromLabel')
        self.fromLabel.setStyleSheet('''
            #fromLabel {
                font: 12pt;
                /*background: rgb(94, 189, 247);*/
                color: rgb(242, 242, 242);
                margin-top: 6px;
                }
            ''')

        self.toLabel = QLabel('To:', objectName='toLabel')
        self.toLabel.setStyleSheet('''
            #toLabel {
                font: 12pt;
                /*background: rgb(94, 189, 247);*/
                color: rgb(242, 242, 242);
                margin-top: 3px;
                }
            ''')
        
        # Set option-date edit and label
        self.fromDateEdit = DateEdit(calendarPopup=True)
        self.fromDateEdit.setDate(QtCore.QDate.currentDate())
        self.fromDateEdit.dateChanged.connect(self.commonDateChanged)
        
        self.toDateEdit = DateEdit(calendarPopup=True)
        self.toDateEdit.setDate(QtCore.QDate.currentDate())
        self.toDateEdit.dateChanged.connect(self.commonDateChanged)
        
        # Set option-India, World chloropleth plot combobox and label
        self.indiaChloroplethLabel = QLabel('Select India Chloropleth Plot', objectName='indiaChloroplethLabel')
        self.indiaChloroplethLabel.setStyleSheet('''
            #indiaChloroplethLabel {
                font: 14pt;
                /*background: rgb(94, 189, 247);*/
                color: rgb(242, 242, 242);
                margin-top: 20px;
                }
            ''')

        self.indiaChloroplethComboBox = ComboBox(objectName='indiaChloroplethComboBox')
        self.indiaChloroplethComboBoxList = ['Total Confirmed Cases', 'Total Recovered', 'Total Deaths']
        self.indiaChloroplethComboBox.setEditable(False)
        self.indiaChloroplethComboBox.addItems(self.indiaChloroplethComboBoxList)
        self.indiaChloroplethComboBox.setCurrentIndex(0)

        self.indiaChloroplethComboBox.currentTextChanged.connect(self.updateIndiaChloropleth)

        self.worldChloroplethLabel = QLabel('Select World Chloropleth Plot', objectName='worldChloroplethLabel')
        self.worldChloroplethLabel.setStyleSheet('''
            #worldChloroplethLabel {
                font: 14pt;
                /*background: rgb(94, 189, 247);*/
                color: rgb(242, 242, 242);
                margin-top: 20px;
                }
            ''')
        
        self.worldChloroplethComboBox = ComboBox(objectName='worldChloroplethComboBox')
        self.worldChloroplethComboBoxList = ['Total Confirmed Cases', 'Total Deaths']
        self.worldChloroplethComboBox.setEditable(False)
        self.worldChloroplethComboBox.addItems(self.worldChloroplethComboBoxList)
        self.worldChloroplethComboBox.setCurrentIndex(0)

        self.worldChloroplethComboBox.currentTextChanged.connect(self.updateWorldChloropleth)

        self.databaseStatusLabel = QLabel()
        self.databaseStatusLabel.setVisible(False)
        self.databaseStatusLabel.setMaximumWidth(400)
        self.databaseStatusLabel.setWordWrap(True)
        self.databaseStatusLabel.setStyleSheet('''
                QLabel {
                font-size: 9pt;
                color: rgb(242, 242, 242);
                font-style: italic;
                }
            ''')
        
        # Add option widgets(comboboxes, labels, etc.) to option body frame layout
        self.optionsBodyFrameLayout.addWidget(self.locationLabel, 0, 1)
        self.optionsBodyFrameLayout.addWidget(self.countryComboBox, 1, 1)
        self.optionsBodyFrameLayout.addWidget(self.stateComboBox, 2, 1)
        self.optionsBodyFrameLayout.addWidget(self.periodLabel, 3, 1)
        self.optionsBodyFrameLayout.addWidget(self.fromLabel, 4, 1)
        self.optionsBodyFrameLayout.addWidget(self.fromDateEdit, 5, 1)
        self.optionsBodyFrameLayout.addWidget(self.toLabel, 6, 1)
        self.optionsBodyFrameLayout.addWidget(self.toDateEdit, 7, 1)
        self.optionsBodyFrameLayout.addWidget(self.worldChloroplethLabel, 8, 1)
        self.optionsBodyFrameLayout.addWidget(self.worldChloroplethComboBox, 9, 1)
        self.optionsBodyFrameLayout.addWidget(self.indiaChloroplethLabel, 10, 1)
        self.optionsBodyFrameLayout.addWidget(self.indiaChloroplethComboBox, 11, 1)

        #Set space below options body
        self.optionsSpace = QSpacerItem(400, 510, QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)

        # Add widgets to general layout
        self.generalLayout.addWidget(self.tabWidget, 0, 0, 4, 1)
        self.generalLayout.addWidget(self.optionsHeadFrame, 0, 1)
        self.generalLayout.addWidget(self.optionsBodyFrame, 1, 1)
        self.generalLayout.addItem(self.optionsSpace, 2, 1)
        self.generalLayout.addWidget(self.databaseStatusLabel, 3, 1)

##        self.updateCountryDataFrameWorker = Worker(self.updateCountryDataFrame)
##        self.updateCountryDataFrameWorker.setAutoDelete(False)
##        #self.updateCountryTableWorker = Worker(self.updateCountryTable)
##        self.updateCountryGraphWorker = Worker(self.updateCountryGraph)
##        self.updateCountryGraphWorker.setAutoDelete(False)
##        self.updateCountryCRGraphWorker = Worker(self.updateCountryCRGraph)
##        self.updateCountryCRGraphWorker.setAutoDelete(False)
##        self.updateNewsTabWorker = Worker(self.updateNewsTab)
##        self.updateNewsTabWorker.setAutoDelete(False)

        self.showMaximized()

    def updateDatabase(self):
        status, lastUpdate = update_covid19_database()
        
        if status == 'Success':
            password = os.environ.get('MYSQL_PASS')
            self.engine = create_engine(fr"mysql+mysqlconnector://root:{password}@localhost/covid19")
        
            self.databaseStatusLabel.setText(f'Database updated succesfully on {lastUpdate}.')
            self.indiaTotalDataFrame = pd.read_sql('india_total', con=self.engine, index_col='ID')
            self.indiaTotalDataFrame.index.name = None

            self.indiaDailyDataFrame = pd.read_sql('india_daily', con=self.engine, index_col='ID')
            self.indiaDailyDataFrame.index.name = None

            self.globalDataFrame = pd.read_sql('global', con=self.engine, index_col='ID')
            self.globalDataFrame.index.name = None

            self.engine.dispose()
            
        elif status == 'No download':
            self.databaseStatusLabel.setText(f'Database up-to-date, last updated on {lastUpdate}.')
        else:
            self.databaseStatusLabel.setText(f'Unable to update database, {status}, last updated on {lastUpdate}.')

        self.databaseStatusLabel.setVisible(True)
        
    def countryComboBoxTextChange(self, text):
        self.covid_app.setOverrideCursor(Qt.WaitCursor)
        
        state = self.stateComboBox.currentText()

        self.fromDateEdit.clearMinimumDate()
        self.fromDateEdit.clearMaximumDate()
        self.toDateEdit.clearMinimumDate()
        self.toDateEdit.clearMaximumDate()

        self.worldChloroplethCanvas.setVisible(True)
        self.hLineGraphTab2.setVisible(True)
        if text == 'India':
            self.stateComboBox.setEnabled(True)
            self.indiaChloroplethCanvas.setVisible(True)
            self.hLineGraphTab1.setVisible(True)
        else:
            self.stateComboBox.setCurrentIndex(0)
            self.stateComboBox.setEnabled(False)
            self.indiaChloroplethCanvas.setVisible(False)
            self.hLineGraphTab1.setVisible(False)

            self.hLineGraphTab5.setVisible(True)

        minDate = self.globalDataFrame[self.globalDataFrame['country']==f'{text}']['date'].min().to_pydatetime().date()
        maxDate = self.globalDataFrame[self.globalDataFrame['country']==f'{text}']['date'].max().to_pydatetime().date()

        self.fromDateEdit.blockSignals(True)
        self.toDateEdit.blockSignals(True)
        self.fromDateEdit.setDate(QtCore.QDate(minDate.year, minDate.month, minDate.day))
        self.toDateEdit.setDate(QtCore.QDate(maxDate.year, maxDate.month, maxDate.day))
        self.fromDateEdit.blockSignals(False)
        self.toDateEdit.blockSignals(False)
        #print(text, self.fromDateEdit.date().toPyDate().strftime('%Y-%m-%d'), self.fromDateEdit.date().toPyDate().strftime('%Y-%m-%d'))

        self.fromDateEdit.setMaximumDate(QtCore.QDate(maxDate.year, maxDate.month, maxDate.day-1))
        self.fromDateEdit.setMinimumDate(QtCore.QDate(minDate.year, minDate.month, minDate.day))
        
        self.toDateEdit.setMaximumDate(QtCore.QDate(maxDate.year, maxDate.month, maxDate.day))
        self.toDateEdit.setMinimumDate(QtCore.QDate(minDate.year, minDate.month, minDate.day+1))

##        self.updateCountryDataFrame()
##        self.updateCountryTable()
##        self.updateCountryGraph()
##        self.updateCountryCRGraph()
##        self.updateNewsTab()
        
        self.updateCountryGraphWorker = Worker(self.updateCountryGraph)
        self.updateCountryCRGraphWorker = Worker(self.updateCountryCRGraph)
        self.updateNewsTabWorker = Worker(self.updateNewsTab)

        self.updateCountryDataFrameWorker = Worker(self.updateCountryDataFrame)
        self.updateCountryDataFrameWorker.signals.finished.connect(self.updateCountryWidgets)
        
        self.threadPool.start(self.updateCountryDataFrameWorker)       

    def updateCountryWidgets(self):
        self.updateCountryTable()
        self.threadPool.start(self.updateCountryGraphWorker)
        self.threadPool.start(self.updateCountryCRGraphWorker)
        self.updateNewsTab()
        self.covid_app.restoreOverrideCursor()


    def stateComboBoxTextChange(self, text):
        self.covid_app.setOverrideCursor(Qt.WaitCursor)
        
        if text != '<-- Select State -->':
            self.hLineGraphTab3.setVisible(True)
            self.hLineGraphTab4.setVisible(True)
        else:
            self.hLineGraphTab3.setVisible(False)
            self.hLineGraphTab4.setVisible(False)
        
        self.updateStateGraphWorker = Worker(self.updateStateGraph)
        self.updateStateCRGraphWorker = Worker(self.updateStateCRGraph)

        self.updateStateDataFrameWorker = Worker(self.updateStateDataFrame)
        self.updateStateDataFrameWorker.signals.finished.connect(self.updateStateWidgets)

        self.threadPool.start(self.updateStateDataFrameWorker)
            
##        self.updateStateDataFrame()
##        self.updateStateTable()
##        self.updateStateGraph()
##        self.updateStateCRGraph()
##        self.updateNewsTab()

    def updateStateWidgets(self):
        self.updateStateTable()
        self.threadPool.start(self.updateStateGraphWorker)
        self.threadPool.start(self.updateStateCRGraphWorker)
        self.updateNewsTab()
        
        self.covid_app.restoreOverrideCursor()
        
    def commonDateChanged(self, date):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()

        if state != '<-- Select State -->':
            self.updateStateDataFrame()
            self.updateStateTable()
            self.updateStateGraph()
            self.updateStateCRGraph()
        self.updateCountryDataFrame()
        self.updateCountryTable()
        self.updateCountryGraph()
        self.updateCountryCRGraph()

    def connectToDb(self):
        password = os.environ.get('MYSQL_PASS')
        self.engine = create_engine(fr"mysql+mysqlconnector://root:{password}@localhost/covid19")

    def executeQuery(self, query):
        self.connection = self.engine.connect()
        cursor = self.connection.execute(query)
        result = cursor.fetchall()
        self.connection.close()
        return result

    def updateCountryDataFrame(self):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()
        fromDate = [self.fromDateEdit.date().toPyDate().strftime('%Y%m%d'), self.fromDateEdit.date().toPyDate().strftime('%d-%b-%Y')]
        toDate = [self.toDateEdit.date().toPyDate().strftime('%Y%m%d'), self.toDateEdit.date().toPyDate().strftime('%d-%b-%Y')]

        countryColumnNames = ['date', 'total_cases', 'new_cases', 'new_deaths', 'total_deaths']
        
        self.countryDataFrame = self.globalDataFrame[(self.globalDataFrame['country'] == f'{country}') &
                                    (self.globalDataFrame['date'].between(f'{fromDate[0]}', f'{toDate[0]}'))][countryColumnNames+['population', 'population_density']]
        
    def updateStateDataFrame(self):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()
        fromDate = [self.fromDateEdit.date().toPyDate().strftime('%Y%m%d'), self.fromDateEdit.date().toPyDate().strftime('%d-%b-%Y')]
        toDate = [self.toDateEdit.date().toPyDate().strftime('%Y%m%d'), self.toDateEdit.date().toPyDate().strftime('%d-%b-%Y')]
        
        if state != '<-- Select State -->':
            stateColumnNames = ['date', 'confirmed', 'deceased', 'recovered', 'total_confirmed', 'total_deceased']

            self.stateDataFrame = self.indiaDailyDataFrame[(self.indiaDailyDataFrame['state'] == f'{state}') &
                                                 (self.indiaDailyDataFrame['date'].between(f'{fromDate[0]}', f'{toDate[0]}'))][stateColumnNames]
        else:
            self.stateDataFrame = None
            
    def setTableTab(self):
        self.tableTabLayout = QVBoxLayout()
        self.tableTabLayout.setSpacing(0)
        self.tableTab.setLayout(self.tableTabLayout)

        self.countryNameLabel = QLabel()
        self.countryNameLabel.setVisible(False)
        self.countryNameLabel.setStyleSheet('''
            QLabel {
                margin: 20px 0px 10px 0px;
                font: 16pt;
                font-weight: 300;
                }
            ''')

        self.countryTypeLabel = QLabel('Total & Daily Cases')
        self.countryTypeLabel.setVisible(False)
        self.countryTypeLabel.setStyleSheet('''
            QLabel {
                margin: 5px 0px 10px 0px;
                font: 14pt;
                font-weight: 300;
                }
            ''')

        self.countryInfoLabels = [QLabel(), QLabel(), QLabel()]
        for label in self.countryInfoLabels:
            label.setVisible(False)
        for label in self.countryInfoLabels:
            label.setStyleSheet('''
                QLabel {
                    font: 13pt;
                    font-weight: 300;
                    margin: 10px 0px 0px 25px;
                    }
                ''')

        self.countryTable = TableWidget()
        self.countryTable.setRowCount(0)
        self.countryTable.setColumnCount(0)
        self.countryTable.setVisible(False)
        self.countryTable.setSortingEnabled(True)

        self.stateNameLabel = QLabel()
        self.stateNameLabel.setVisible(False)
        self.stateNameLabel.setStyleSheet('''
            QLabel {
                margin: 20px 0px 10px 0px;
                font: 16pt;
                font-weight: 300;
                }
            ''')

        self.stateTypeLabel = QLabel('Total & Daily Cases')
        self.stateTypeLabel.setVisible(False)
        self.stateTypeLabel.setStyleSheet('''
            QLabel {
                margin: 5px 0px 10px 0px;
                font: 14pt;
                font-weight: 300;
                }
            ''')

        self.stateInfoLabels = [QLabel(), QLabel(), QLabel()]
        for label in self.stateInfoLabels:
            label.setVisible(False)
        for label in self.stateInfoLabels:
            label.setStyleSheet('''
                QLabel {
                    font: 13pt;
                    font-weight: 300;
                    margin: 10px 0px 0px 25px;
                    }
                ''')

        self.stateTable = TableWidget()
        self.stateTable.setRowCount(0)
        self.stateTable.setColumnCount(0)
        self.stateTable.setVisible(False)
        self.stateTable.setSortingEnabled(True)

        self.stateTotalLabel = QLabel('States/UTs of India')
        self.stateTotalLabel.setVisible(False)
        self.stateTotalLabel.setStyleSheet('''
            QLabel {
                margin: 60px 0px 10px 0px;
                font: 16pt;
                font-weight: 300;
                }
            ''')

        self.stateTotalTypeLabel = QLabel('Total Cases on Last Update')
        self.stateTotalTypeLabel.setVisible(False)
        self.stateTotalTypeLabel.setStyleSheet('''
            QLabel {
                margin: 5px 0px 10px 0px;
                font: 14pt;
                font-weight: 300;
                }
            ''')

        self.stateTotalTable = TableWidget()
        self.stateTotalTable.setVisible(False)
        stateTotalColumnNames = ['state', 'confirmed', 'active', 'recovered', 'deaths', 'population', 'density']
        dataFrameTotal = self.indiaTotalDataFrame[(self.indiaTotalDataFrame['state'] != 'Total')][stateTotalColumnNames]
        self.stateTotalTable.setData(dataFrameTotal, stateTotalColumnNames)
        self.stateTotalTable.setSortingEnabled(True)
        self.stateTotalTable.sortItems(1, Qt.DescendingOrder)

        self.hLineTableTab1 = horizontalLine()
        self.hLineTableTab1.setVisible(False)
        self.hLineTableTab2 = horizontalLine()
        self.hLineTableTab2.setVisible(False)
        
        self.tableTabLayout.addWidget(self.stateNameLabel)
        self.tableTabLayout.addWidget(self.stateTypeLabel)
        for label in self.stateInfoLabels:
            self.tableTabLayout.addWidget(label)
        self.tableTabLayout.addWidget(self.stateTable)
        self.tableTabLayout.addWidget(self.hLineTableTab1)
        self.tableTabLayout.addWidget(self.stateTotalLabel)
        self.tableTabLayout.addWidget(self.stateTotalTypeLabel)
        self.tableTabLayout.addWidget(self.stateTotalTable)
        self.tableTabLayout.addWidget(self.hLineTableTab2)
        self.tableTabLayout.addWidget(self.countryNameLabel)
        self.tableTabLayout.addWidget(self.countryTypeLabel)
        for label in self.countryInfoLabels:
            self.tableTabLayout.addWidget(label)
        self.tableTabLayout.addWidget(self.countryTable)

        self.tableTabLayout.setAlignment(self.stateNameLabel, Qt.AlignHCenter)
        self.tableTabLayout.setAlignment(self.stateTypeLabel, Qt.AlignHCenter)
        self.tableTabLayout.setAlignment(self.stateTable, Qt.AlignHCenter)
        self.tableTabLayout.setAlignment(self.stateTotalLabel, Qt.AlignHCenter)
        self.tableTabLayout.setAlignment(self.stateTotalTypeLabel, Qt.AlignHCenter)
        self.tableTabLayout.setAlignment(self.stateTotalTable, Qt.AlignHCenter)
        self.tableTabLayout.setAlignment(self.countryNameLabel, Qt.AlignHCenter)
        self.tableTabLayout.setAlignment(self.countryTypeLabel, Qt.AlignHCenter)
        self.tableTabLayout.setAlignment(self.countryTable, Qt.AlignHCenter)

    def updateCountryTable(self):
        self.countryTable.setRowCount(0)
        self.countryTable.setColumnCount(0)
        
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()
        fromDate = [self.fromDateEdit.date().toPyDate().strftime('%Y%m%d'), self.fromDateEdit.date().toPyDate().strftime('%d-%b-%Y')]
        toDate = [self.toDateEdit.date().toPyDate().strftime('%Y%m%d'), self.toDateEdit.date().toPyDate().strftime('%d-%b-%Y')]
        
        if country == '<-- Select Country -->':
            return

        countryColumnNames = ['date', 'total_cases', 'new_cases', 'total_deaths', 'new_deaths']
        
        population = self.countryDataFrame['population'].iat[0]
        population_density = math.ceil(self.countryDataFrame['population_density'].iat[0])
        
        self.countryTable.setData(self.countryDataFrame[countryColumnNames], countryColumnNames)

        self.countryNameLabel.setText(f'{country}')
        self.countryInfoLabels[0].setText(f'Data populated from {fromDate[1]} to {toDate[1]}')
        self.countryInfoLabels[1].setText(f'Popualtion: {int(population):n}')
        self.countryInfoLabels[2].setText(f'Population Density: {int(population_density):n}/Km\u00b2')

        self.countryNameLabel.setVisible(True)
        self.countryTypeLabel.setVisible(True)
        for label in self.countryInfoLabels:
            label.setVisible(True)
        self.countryTable.setVisible(True)

    def updateStateTable(self):
        self.stateTable.setRowCount(0)
        self.stateTable.setColumnCount(0)
        
        state = self.stateComboBox.currentText()

        if state == '<-- Select State -->':
            self.stateNameLabel.setVisible(False)
            self.stateTypeLabel.setVisible(False)
            for label in self.stateInfoLabels:
                label.setVisible(False)
            self.stateTable.setVisible(False)
            self.hLineTableTab1.setVisible(False)
            self.stateTotalLabel.setVisible(False)
            self.stateTotalTypeLabel.setVisible(False)
            self.stateTotalTable.setVisible(False)
            self.hLineTableTab2.setVisible(False)

            self.countryNameLabel.setStyleSheet('')
            self.countryNameLabel.setStyleSheet('''
            QLabel {
                margin: 20px 0px 10px 0px;
                font: 16pt;
                font-weight: 300;
                }
            ''')

        else:
            fromDate = [self.fromDateEdit.date().toPyDate().strftime('%Y%m%d'),
                        self.stateDataFrame['date'].min().to_pydatetime().strftime('%d-%b-%Y')]
            toDate = [self.toDateEdit.date().toPyDate().strftime('%Y%m%d'),
                      self.stateDataFrame['date'].max().to_pydatetime().strftime('%d-%b-%Y')]

            stateColumnNames = ['date', 'confirmed', 'deceased', 'recovered', 'total_confirmed', 'total_deceased']

            population = self.indiaTotalDataFrame[self.indiaTotalDataFrame['state'] == f'{state}']['population'].iat[0]
            population_density = self.indiaTotalDataFrame[self.indiaTotalDataFrame['state'] == f'{state}']['density'].iat[0]

            self.stateTable.setData(self.stateDataFrame, stateColumnNames)
            
            self.stateNameLabel.setText(f'{state}, India')
            self.stateInfoLabels[0].setText(f'Data populated from {fromDate[1]} to {toDate[1]}')
            self.stateInfoLabels[1].setText(f'Popualtion: {int(population):n}')
            self.stateInfoLabels[2].setText(f'Population Density: {int(population_density):n}/Km\u00b2')

            self.stateNameLabel.setVisible(True)
            self.stateTypeLabel.setVisible(True)
            for label in self.stateInfoLabels:
                label.setVisible(True)
            self.stateTable.setVisible(True)
            self.hLineTableTab1.setVisible(True)
            self.stateTotalLabel.setVisible(True)
            self.stateTotalTypeLabel.setVisible(True)
            self.stateTotalTable.setVisible(True)
            self.hLineTableTab2.setVisible(True)

            self.countryNameLabel.setStyleSheet("")
            self.countryNameLabel.setStyleSheet('''
            QLabel {
                margin: 60px 0px 10px 0px;
                font: 16pt;
                font-weight: 300;
                }
            ''')

    # Method to round a int number to nearest power of ten
    def roundupToNearestPowerTen(self, x, n):
        return x if x % 10**n == 0 else x + 10**n - x % 10**n
    
    def setGraphTab(self):
        self.graphTabLayout = QVBoxLayout()
        self.graphTabLayout.setSpacing(0)
        self.graphTab.setLayout(self.graphTabLayout)

        self.dateFormatter = DateFormatter("%b, %y")
        self.dateLocator3m = MonthLocator(interval=3)
        self.dateLocator2m = MonthLocator(interval=2)
        self.dateLocator1m = MonthLocator(interval=1)

##        self.graphLoadingLabel = QLabel()
##        self.graphLoadingLabel.setVisible(False)
##        self.graphLoadingMovie = QtGui.QMovie(r'.\app-resources\30.gif')
##        self.graphLoadingLabel.setMovie(self.graphLoadingMovie)

        self.intFormatter = FuncFormatter(lambda x, pos: f'{int(x):n}')

        self.countryFigure = Figure() #linewidth=5, edgecolor='k'
        self.countryCanvas = FigureCanvasQTAgg(self.countryFigure)
        self.countryCanvas.setMinimumHeight(900)
        self.countryCanvas.setMinimumWidth(1000)
        self.countryCanvas.setVisible(False)
        self.countryCanvasCID = None

        self.indiaChloroplethFigure = mpl.figure.Figure() #linewidth=5, edgecolor='k'
        self.indiaChloroplethCanvas = FigureCanvasQTAgg(self.indiaChloroplethFigure)

        self.indiaShapeFilePath = r'F:\PYTHON\covid19_v2\project\app-resources\india_states.geojson'
        self.indiaGeoDataFrame = gpd.read_file(self.indiaShapeFilePath)
        self.indiaGeoDataFrame['ST_NM'] = self.indiaGeoDataFrame['ST_NM'].replace(['Andaman & Nicobar', 'Jammu & Kashmir'],
                                                                                  ['Andaman and Nicobar Islands', 'Jammu and Kashmir'])
        self.indiaChloroplethCanvasCID = None

        self.updateIndiaChloropleth('Total Confirmed Cases')
        
        self.indiaChloroplethCanvas.setMinimumHeight(900)
        self.indiaChloroplethCanvas.setMinimumWidth(1000)
        self.indiaChloroplethCanvas.setVisible(False)


        self.worldChloroplethFigure = mpl.figure.Figure()
        self.worldChloroplethCanvas = FigureCanvasQTAgg(self.worldChloroplethFigure)

        self.worldShapeFilePath = r'F:\PYTHON\covid19_v2\project\app-resources\world-shape-files\ne_110m_admin_0_countries.shp'
        self.worldGeoDataFrame = gpd.read_file(self.worldShapeFilePath)
        self.worldGeoDataFrame['NAME_LONG'] = self.worldGeoDataFrame['NAME_LONG'].replace(['Democratic Republic of the Congo', 'Timor-Leste',
                                                                                           "Côte d'Ivoire", 'Republic of the Congo', 'eSwatini',
                                                                                           'The Gambia', 'Lao PDR', 'Republic of Korea',
                                                                                           'Brunei Darussalam', 'Czech Republic', 'Somaliland',
                                                                                           'Macedonia', 'Russian Federation'],
                                                                                          ['Democratic Republic of Congo', 'Timor',
                                                                                           "Cote d'Ivoire", 'Congo', 'Eswatini', 'Gambia',
                                                                                           'Laos', 'South Korea', 'Brunei', 'Czechia',
                                                                                           'Somalia', 'North Macedonia', 'Russia'])
        #worldColorMap = mpl.cm.Blues
        self.worldTotalDataFrame = self.globalDataFrame[['country', 'total_cases', 'total_deaths']].groupby(['country']).max()
        self.worldTotalDataFrame = self.worldTotalDataFrame[~self.worldTotalDataFrame.index.isin(['Europe', 'Asia', 'North America',
                                                                                                  'European Union', 'South America', 'Africa'])]
        self.worldChloroplethCanvasCID = None

        self.updateWorldChloropleth('Total Confirmed Cases')
        
        self.worldChloroplethCanvas.setMinimumHeight(900)
        self.worldChloroplethCanvas.setMinimumWidth(1000)
        self.worldChloroplethCanvas.setVisible(False)

        
        
        self.stateFigure = Figure()
        self.stateAxes = self.stateFigure.add_subplot(111)

        self.stateCanvas = FigureCanvasQTAgg(self.stateFigure)
        self.stateCanvas.setMinimumHeight(900)
        self.stateCanvas.setMinimumWidth(1000)
        self.stateCanvas.setVisible(False)
        self.stateCanvasCID = None

        self.countryCRFigure = Figure()
        self.countryCRCanvas = FigureCanvasQTAgg(self.countryCRFigure)
        self.countryCRCanvas.setMinimumHeight(900)
        self.countryCRCanvas.setMinimumWidth(1000)
        #self.countryCRCanvas.setVisible(False)

        self.stateCRFigure = Figure()
        self.stateCRCanvas = FigureCanvasQTAgg(self.stateCRFigure)
        self.stateCRCanvas.setMinimumHeight(900)
        self.stateCRCanvas.setMinimumWidth(1000)
        self.stateCRCanvas.setVisible(False)

        self.hLineGraphTab1 = horizontalLine()
        self.hLineGraphTab1.setVisible(False)
        self.hLineGraphTab2 = horizontalLine()
        self.hLineGraphTab2.setVisible(False)
        self.hLineGraphTab3 = horizontalLine()
        self.hLineGraphTab3.setVisible(False)
        self.hLineGraphTab4 = horizontalLine()
        self.hLineGraphTab4.setVisible(False)
        self.hLineGraphTab5 = horizontalLine()
        self.hLineGraphTab5.setVisible(False)

        #self.graphTabLayout.addWidget(self.graphLoadingLabel)
        self.graphTabLayout.addWidget(self.indiaChloroplethCanvas)
        self.graphTabLayout.addWidget(self.hLineGraphTab1)
        self.graphTabLayout.addWidget(self.worldChloroplethCanvas)
        self.graphTabLayout.addWidget(self.hLineGraphTab2)
        self.graphTabLayout.addWidget(self.stateCanvas)
        self.graphTabLayout.addWidget(self.hLineGraphTab3)
        self.graphTabLayout.addWidget(self.stateCRCanvas)
        self.graphTabLayout.addWidget(self.hLineGraphTab4)
        self.graphTabLayout.addWidget(self.countryCanvas)
        self.graphTabLayout.addWidget(self.hLineGraphTab5)
        self.graphTabLayout.addWidget(self.countryCRCanvas)

    def updateIndiaChloropleth(self, plot):
        self.indiaChloroplethFigure.clear()
        self.indiaChloroplethCanvas.mpl_disconnect(self.indiaChloroplethCanvasCID)
        
        self.indiaChloroplethStateName = None

        plot_dict = {'Total Confirmed Cases':{'col': 'confirmed', 'cm':mpl.cm.Blues},
                     'Total Recovered': {'col': 'recovered', 'cm':mpl.cm.Greens},
                     'Total Deaths': {'col': 'deaths', 'cm':mpl.cm.Reds}
                     }

        self.indiaStateMaxCases = self.indiaTotalDataFrame[plot_dict[plot]['col']].nlargest(2).iloc[-1]
        self.indiaStateMinCases = self.indiaTotalDataFrame[plot_dict[plot]['col']].min()

        self.indiaChloroplethAxes = self.indiaChloroplethFigure.add_subplot(111, projection=ccrs.PlateCarree())
        self.indiaChloroplethAxes.axis('off')
        lastUpdate = self.indiaTotalDataFrame.at[1, 'lastupdatedtime'].to_pydatetime().strftime('%d-%b-%Y')

        self.indiaChloroplethFigure.suptitle(f'India Chloropleth\n{plot} as of {lastUpdate}', fontsize=16, linespacing=2)
        #self.indiaChloroplethFigure.text(x=0.5, y=0.9, s='hello')
        
        for state, geometry in self.indiaGeoDataFrame[['ST_NM', 'geometry']].values:
            stateName = state
            cases = self.indiaTotalDataFrame.loc[self.indiaTotalDataFrame.state == stateName, plot_dict[plot]['col']].values[0]
            self.indiaChloroplethAxes.add_geometries([geometry], ccrs.PlateCarree(),
                                                     facecolor=plot_dict[plot]['cm'](cases/self.indiaStateMaxCases, 1),
                                                     edgecolor='k', linewidth=0.2)

        self.indiaChloroplethAxes.set_extent([67, 98, 7, 39], ccrs.PlateCarree())

        sm = plt.cm.ScalarMappable(cmap=plot_dict[plot]['cm'],norm=plt.Normalize(self.indiaStateMinCases, self.indiaStateMaxCases))
        sm._A = []
        self.indiaChloroplethColorBar = plt.colorbar(sm, ax=self.indiaChloroplethAxes, orientation='vertical',  shrink=0.85)
        self.indiaChloroplethColorBar.outline.set_visible(False)
        self.indiaChloroplethColorBar.ax.tick_params(length=0)
        self.indiaChloroplethColorBar.ax.zorder = -1

        self.indiaChloroplethColorBar.ax.yaxis.set_major_formatter(self.intFormatter)

        self.indiaChloroplethAnnotation = self.indiaChloroplethAxes.annotate("", xy=(0,0), xytext=(-20,10),textcoords="offset points",
                                                                             bbox=dict(boxstyle="round", fc="w"))
        self.indiaChloroplethAnnotation.get_bbox_patch().set_alpha(0.9)
        self.indiaChloroplethAnnotation.get_bbox_patch().set_edgecolor('k')
        
        self.indiaChloroplethAnnotation.set_visible(False)

        def updateIndiaChloroplethAnnotation(x, y, state):
            self.indiaChloroplethAnnotation.xy = (x, y)
            cases = self.indiaTotalDataFrame.loc[self.indiaTotalDataFrame.state == state, plot_dict[plot]['col']].values[0]
            text = f'{state}\n{plot}: {int(cases):n}'
            self.indiaChloroplethAnnotation.set_text(text)

        def hoverIndiaChloropleth(event):
            xdata = event.xdata
            ydata = event.ydata
            vis = self.indiaChloroplethAnnotation.get_visible()

            if xdata and ydata:
                point = Point(xdata, ydata)
                boolSeries = self.indiaGeoDataFrame.contains(point)
                if boolSeries.any():
                    state = self.indiaGeoDataFrame[boolSeries]['ST_NM'].iat[0]
                    if state == self.indiaChloroplethStateName:
                        return
                    else:
                        self.indiaChloroplethStateName = state
                        updateIndiaChloroplethAnnotation(xdata, ydata, state)
                        self.indiaChloroplethAnnotation.set_visible(True)
                        self.indiaChloroplethCanvas.draw_idle()
                else:
                    if vis:
                        self.indiaChloroplethStateName = None
                        self.indiaChloroplethAnnotation.set_visible(False)
                        self.indiaChloroplethCanvas.draw_idle()
            else:
                if vis:
                    self.indiaChloroplethStateName = None
                    self.indiaChloroplethAnnotation.set_visible(False)
                    self.indiaChloroplethCanvas.draw_idle()

        self.indiaChloroplethCanvasCID = self.indiaChloroplethCanvas.mpl_connect("motion_notify_event", hoverIndiaChloropleth)

        posIndiaChloroplethAxes = self.indiaChloroplethAxes.get_position() #Bbox(x0=0.1675000000000001, y0=0.10999999999999999, x1=0.7450000000000001, y1=0.88)
        posIndiaChloroplethAxes.y1 = 0.910
        posIndiaChloroplethAxes.x1 = 0.75
        posIndiaChloroplethAxes.x0 = 0
        posIndiaChloroplethAxes.y0 = 0.05
        self.indiaChloroplethAxes.set_position(posIndiaChloroplethAxes)
        
        self.indiaChloroplethCanvas.draw()

    def updateWorldChloropleth(self, plot):
        self.worldChloroplethFigure.clear()
        self.worldChloroplethCanvas.mpl_disconnect(self.worldChloroplethCanvasCID)
        
        self.worldChloroplethCountryName = None

        plot_dict = {'Total Confirmed Cases':{'col': 'total_cases', 'cm':mpl.cm.Blues},
                     'Total Deaths': {'col': 'total_deaths', 'cm':mpl.cm.Reds}
                     }
        
        self.worldCountryMaxCases = self.worldTotalDataFrame[plot_dict[plot]['col']].nlargest(2).iloc[-1]
        self.worldCountryMinCases = self.worldTotalDataFrame[plot_dict[plot]['col']].min()

        self.worldChloroplethAxes = self.worldChloroplethFigure.add_subplot(111, projection=ccrs.PlateCarree())
        self.worldChloroplethAxes.axis('off')
        lastUpdateDate = self.globalDataFrame['date'].max().to_pydatetime().strftime('%d-%b-%Y')
        self.worldChloroplethFigure.suptitle(f'World Chloropleth\n{plot} as of {lastUpdateDate}', fontsize=16, linespacing=2)
        
        for country, geometry in self.worldGeoDataFrame[['NAME_LONG', 'geometry']].values:
            countryName = country
            try:
                confirmedCases = self.worldTotalDataFrame.at[country, plot_dict[plot]['col']]
            except KeyError:
                confirmedCases = 0
                
            self.worldChloroplethAxes.add_geometries([geometry], ccrs.PlateCarree(),
                                                     facecolor=plot_dict[plot]['cm'](confirmedCases/self.worldCountryMaxCases, 1),
                                                     edgecolor='k', linewidth=0.2)

        worldScalarMappable = plt.cm.ScalarMappable(cmap=plot_dict[plot]['cm'],
                                                    norm=plt.Normalize(self.worldCountryMinCases, self.worldCountryMaxCases))
        worldScalarMappable._A = []

        cbaxes = self.worldChloroplethFigure.add_axes([0.91, 0.21, 0.02, 0.55])
        worldChloroplethColorBar = plt.colorbar(worldScalarMappable, ax=self.worldChloroplethAxes, cax=cbaxes, orientation='vertical',  shrink=0.85)
        worldChloroplethColorBar.outline.set_visible(False)
        worldChloroplethColorBar.ax.tick_params(length=0)
        worldChloroplethColorBar.ax.zorder = -1

        worldChloroplethColorBar.ax.yaxis.set_major_formatter(self.intFormatter)

        self.worldChloroplethAnnotation = self.worldChloroplethAxes.annotate("", xy=(0,0), xytext=(-40,10),textcoords="offset points",
                                                                             bbox=dict(boxstyle="round", fc="w"), zorder=5)
        self.worldChloroplethAnnotation.get_bbox_patch().set_alpha(0.9)
        self.worldChloroplethAnnotation.get_bbox_patch().set_edgecolor('k')
        
        self.worldChloroplethAnnotation.set_visible(False)

        def updateWorldChloroplethAnnotation(x, y, country):
            self.worldChloroplethAnnotation.xy = (x, y)
            try:
                cases = self.worldTotalDataFrame.at[country, plot_dict[plot]['col']]
            except KeyError:
                cases = 0
            text = f'{country}\n{plot}: {int(cases):n}'
            self.worldChloroplethAnnotation.set_text(text)

        def hoverWorldChloropleth(event):
            xdata = event.xdata
            ydata = event.ydata
            vis = self.worldChloroplethAnnotation.get_visible()

            if xdata and ydata:
                point = Point(xdata, ydata)
                boolSeries = self.worldGeoDataFrame.contains(point)
                if boolSeries.any():
                    country = self.worldGeoDataFrame[boolSeries]['NAME_LONG'].iat[0]
                    if country == self.worldChloroplethCountryName:
                        return
                    else:
                        self.worldChloroplethCountryName = country
                        updateWorldChloroplethAnnotation(xdata, ydata, country)
                        self.worldChloroplethAnnotation.set_visible(True)
                        self.worldChloroplethCanvas.draw_idle()
                else:
                    if vis:
                        self.worldChloroplethCountryName = None
                        self.worldChloroplethAnnotation.set_visible(False)
                        self.worldChloroplethCanvas.draw_idle()
            else:
                if vis:
                    self.worldChloroplethCountryName = None
                    self.worldChloroplethAnnotation.set_visible(False)
                    self.worldChloroplethCanvas.draw_idle()

        #print(self.worldChloroplethAxes.get_position()) #Bbox(x0=0.1675000000000001, y0=0.10999999999999999, x1=0.7450000000000001, y1=0.88)
        posWorldChloroplethAxes = self.worldChloroplethAxes.get_position() #Bbox(x0=0.1675000000000001, y0=0.10999999999999999, x1=0.7450000000000001, y1=0.88)
        posWorldChloroplethAxes.y1 = 0.925
        posWorldChloroplethAxes.x1 = 0.8775
        posWorldChloroplethAxes.x0 = 0.015
        posWorldChloroplethAxes.y0 = 0.02
        self.worldChloroplethAxes.set_position(posWorldChloroplethAxes)
        
        self.worldChloroplethCanvasCID = self.worldChloroplethCanvas.mpl_connect("motion_notify_event", hoverWorldChloropleth)

        self.worldChloroplethCanvas.draw()
    
    def updateCountryGraph(self):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()
        snsColorPalette = sns.color_palette()

        self.countryCanvas.mpl_disconnect(self.countryCanvasCID)
        
        self.countryCanvas.setVisible(True)

        self.countryFigure.clear()
        countryGridSpec = GridSpec(2, 2, hspace=0.3, wspace=0.3)
        self.countryAxes1 = self.countryFigure.add_subplot(countryGridSpec[0, 0], label='Axes1')
        self.countryAxes2 = self.countryFigure.add_subplot(countryGridSpec[0, 1], label='Axes2')
        self.countryAxes3 = self.countryFigure.add_subplot(countryGridSpec[1, 1], label='Axes3')
        self.countryAxes4 = self.countryFigure.add_subplot(countryGridSpec[1, 0], label='Axes4')
        self.countryAxesList = [self.countryAxes1, self.countryAxes2, self.countryAxes3, self.countryAxes4]
        colorList = [snsColorPalette[0], snsColorPalette[0], snsColorPalette[3], snsColorPalette[3]]

        timeDelta = self.countryDataFrame['date'].max().to_pydatetime() - self.countryDataFrame['date'].min().to_pydatetime()
        if timeDelta.days/30 >= 15:
            dl = self.dateLocator3m
        elif timeDelta.days/30 >= 8:
            dl = self.dateLocator2m
        else:
            dl = self.dateLocator1m
        
        for axes, yattr, c in zip(self.countryAxesList,
                               ['total_cases', 'new_cases', 'new_deaths', 'total_deaths'],
                               colorList):
            sns.lineplot(data=self.countryDataFrame, x='date', y=yattr, ax=axes, color=c)
            axes.fill_between(self.countryDataFrame['date'].values, self.countryDataFrame[yattr].values,
                              color=c, alpha=0.3)

            axes.set_ylabel('Daily '+yattr.replace('_', ' ').title() if 'new' in yattr else yattr.replace('_', ' ').title(),
                            fontsize=12.5)
            axes.set_xlabel('Date', fontsize=12.5)

            axes.xaxis.set_major_locator(dl)
            axes.xaxis.set_major_formatter(self.dateFormatter)

            axes.yaxis.set_major_formatter(self.intFormatter)

        self.countryGraphAnnotations = {}
        for axes in self.countryAxesList:
            label = axes.get_label()
            self.countryGraphAnnotations[label] = axes.annotate("", xy=(0,0), xytext=(-20,10),textcoords="offset points",
                                                                bbox=dict(boxstyle="round", fc="w"), zorder=5)
            self.countryGraphAnnotations[label].get_bbox_patch().set_alpha(0.9)
            self.countryGraphAnnotations[label].get_bbox_patch().set_edgecolor('k')
            self.countryGraphAnnotations[label].set_visible(False)
            
        def updateCountryGraphAnnotation(xdata, ydata, axes, annotation, ind):
            x,y = axes.get_lines()[0].get_data()
            annotation.xy = (xdata, ydata)
            cases = y[ind["ind"][0]]
            date = num2date(x[ind["ind"][0]]).strftime('%d-%b-%y')
            text = f'{int(cases):n} | {date}'
            annotation.set_text(text)

            
        def hoverCountryGraph(event):
            axes = event.inaxes
            if axes:
                vis = self.countryGraphAnnotations[axes.get_label()].get_visible()
                contain, ind = axes.get_lines()[0].contains(event)
                if contain:
                    xdata = event.xdata
                    ydata = event.ydata
                    updateCountryGraphAnnotation(xdata, ydata, axes, self.countryGraphAnnotations[axes.get_label()], ind)
                    self.countryGraphAnnotations[axes.get_label()].set_visible(True)
                    self.countryCanvas.draw_idle()
                else:
                    if vis:
                        self.countryGraphAnnotations[axes.get_label()].set_visible(False)
                    self.countryCanvas.draw_idle()
            else:
                for annot in self.countryGraphAnnotations.values():
                    annot.set_visible(False)
                self.countryCanvas.draw_idle()

        self.countryCanvasCID = self.countryCanvas.mpl_connect("motion_notify_event", hoverCountryGraph)

        self.countryFigure.suptitle(f'{country} Line Graph\nCase - Time Series', fontsize=16, linespacing=1.5)
        
        self.countryCanvas.draw()
        

    def updateStateGraph(self):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()
        snsColorPalette = sns.color_palette()

        if state == '<-- Select State -->':
            self.stateCanvas.setVisible(False)
        else:
            self.stateCanvas.setVisible(True)

            self.stateCanvas.mpl_disconnect(self.stateCanvasCID)

            self.stateFigure.clear()
            stateGridSpec = GridSpec(2, 2, hspace=0.3, wspace=0.3)
            self.stateAxes1 = self.stateFigure.add_subplot(stateGridSpec[0, 0], label='Axes1')
            self.stateAxes2 = self.stateFigure.add_subplot(stateGridSpec[0, 1], label='Axes2')
            self.stateAxes3 = self.stateFigure.add_subplot(stateGridSpec[1, 0], label='Axes3')
            self.stateAxes4 = self.stateFigure.add_subplot(stateGridSpec[1, 1], label='Axes4')
            self.stateAxesList = [self.stateAxes1, self.stateAxes2, self.stateAxes3, self.stateAxes4]
            colorList = [snsColorPalette[0], snsColorPalette[0], snsColorPalette[3], snsColorPalette[2]]
            yLabelList = ['Total Cases', 'Daily New Cases', 'Daily New Deaths', 'Daily New Recoveries']

            timeDelta = self.stateDataFrame['date'].max().to_pydatetime() - self.stateDataFrame['date'].min().to_pydatetime()
            if timeDelta.days/30 >= 15:
                dl = self.dateLocator3m
            elif timeDelta.days/30 >= 8:
                dl = self.dateLocator2m
            else:
                dl = self.dateLocator1m
            
            for axes, yattr, c, ylabel in zip(self.stateAxesList,
                                              ['total_confirmed', 'confirmed', 'deceased', 'recovered'],
                                              colorList,
                                              yLabelList):
                sns.lineplot(data=self.stateDataFrame, x='date', y=yattr, ax=axes, color=c)
                axes.fill_between(self.stateDataFrame['date'].values, self.stateDataFrame[yattr].values,
                                  color=c, alpha=0.3)
                axes.set_ylabel(ylabel, fontsize=12.5)
                axes.set_xlabel('Date', fontsize=12.5)

                axes.xaxis.set_major_locator(dl)
                axes.xaxis.set_major_formatter(self.dateFormatter)

                axes.yaxis.set_major_formatter(self.intFormatter)

            self.stateGraphAnnotations = {}
            for axes in self.stateAxesList:
                label = axes.get_label()
                self.stateGraphAnnotations[label] = axes.annotate("", xy=(0,0), xytext=(-30,10),textcoords="offset points",
                                                                    bbox=dict(boxstyle="round", fc="w"), zorder=5)
                self.stateGraphAnnotations[label].get_bbox_patch().set_alpha(0.9)
                self.stateGraphAnnotations[label].get_bbox_patch().set_edgecolor('k')
                self.stateGraphAnnotations[label].set_visible(False)
                
            def updateStateGraphAnnotation(xdata, ydata, axes, annotation, ind):
                x,y = axes.get_lines()[0].get_data()
                annotation.xy = (xdata, ydata)
                cases = y[ind["ind"][0]]
                date = num2date(x[ind["ind"][0]]).strftime('%d-%b-%y')
                text = f'{int(cases):n} | {date}'
                annotation.set_text(text)
                
            def hoverStateGraph(event):
                axes = event.inaxes
                if axes:
                    vis = self.stateGraphAnnotations[axes.get_label()].get_visible()
                    contain, ind = axes.get_lines()[0].contains(event)
                    if contain:
                        xdata = event.xdata
                        ydata = event.ydata
                        updateStateGraphAnnotation(xdata, ydata, axes, self.stateGraphAnnotations[axes.get_label()], ind)
                        self.stateGraphAnnotations[axes.get_label()].set_visible(True)
                        self.stateCanvas.draw_idle()
                    else:
                        if vis:
                            self.stateGraphAnnotations[axes.get_label()].set_visible(False)
                        self.stateCanvas.draw_idle()
                else:
                    for annot in self.stateGraphAnnotations.values():
                        annot.set_visible(False)
                    self.stateCanvas.draw_idle()

            self.stateCanvasCID = self.stateCanvas.mpl_connect("motion_notify_event", hoverStateGraph)

            self.stateFigure.suptitle(f'{state} Line Graph\nCase - Time Series', fontsize=16, linespacing=1.5)

            self.stateCanvas.draw()

    def updateCountryCRGraph(self):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()
        snsColorPalette = sns.color_palette()
        self.countryCRCanvas.setVisible(True)

        self.countryCRFigure.clear()
        countryCRGridSpec = GridSpec(2, 1, hspace=0.1)
        self.countryCRAxes1 = self.countryCRFigure.add_subplot(countryCRGridSpec[0, 0])
        self.countryCRAxes2 = self.countryCRFigure.add_subplot(countryCRGridSpec[1, 0])
        self.countryCRTwinAxes1 = self.countryCRAxes1.twinx()
        self.countryCRTwinAxes2 = self.countryCRAxes2.twinx()
        self.countryCRAxesList = [self.countryCRAxes1, self.countryCRTwinAxes1, self.countryCRAxes2, self.countryCRTwinAxes2]
        colorList = [snsColorPalette[0], snsColorPalette[3], snsColorPalette[0], snsColorPalette[3]]

        for axes, yattr, c in zip(self.countryCRAxesList,
                                  ['total_cases', 'total_deaths', 'new_cases', 'new_deaths'],
                                  colorList):
            sns.lineplot(data=self.countryDataFrame, x='date', y=yattr, color=c, ax=axes)
            axes.fill_between(self.countryDataFrame['date'].values, self.countryDataFrame[yattr].values,
                              color=c, alpha=0.3)
            
            axes.set_ylabel('Daily '+yattr.replace('_', ' ').title() if 'new' in yattr else yattr.replace('_', ' ').title(),
                            fontsize=13)

##            axes.xaxis.set_major_locator(self.dateLocator)
            axes.xaxis.set_major_formatter(self.dateFormatter)

            maxData = self.countryDataFrame[yattr].values.max()
            nPower = len(str(maxData)) - 1 if len(str(maxData)) > 1 else 0
            axes.set_yticks(np.linspace(0, self.roundupToNearestPowerTen(maxData, nPower), 5))

            axes.tick_params(axis='both', which='both', length=0, pad=8, labelsize=12)

            axes.yaxis.set_major_formatter(self.intFormatter)

        self.countryCRAxes1.set_xlabel('')
        self.countryCRAxes2.set_xlabel('Date', fontsize=13)
        
        self.countryCRTwinAxes1.grid(False)
        self.countryCRTwinAxes2.grid(False)

        for label in self.countryCRAxes1.get_xticklabels():
            label.set_visible(False)
        
        for axes in self.countryCRAxesList:
            pos = axes.get_position()
            pos.x0 += 0.1
            pos.x1 -= 0.1
            #pos.y1 = pos.x1 - pos.x0 + pos.y0
            axes.set_position(pos)

        self.countryCRFigure.suptitle(f'{country} Correlation Line Graph\nCase - Time Series', fontsize=16, linespacing=1.5)
        self.countryCRCanvas.draw()

    def updateStateCRGraph(self):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()
        snsColorPalette = sns.color_palette()

        if state == '<-- Select State -->':
            self.stateCRCanvas.setVisible(False)
        else:
            self.stateCRCanvas.setVisible(True)

            self.stateCRFigure.clear()
            stateCRGridSpec = GridSpec(2, 1, hspace=0.1)
            self.stateCRAxes1 = self.stateCRFigure.add_subplot(stateCRGridSpec[0, 0])
            self.stateCRAxes2 = self.stateCRFigure.add_subplot(stateCRGridSpec[1, 0])
            self.stateCRTwinAxes1 = self.stateCRAxes1.twinx()
            self.stateCRTwinAxes2 = self.stateCRAxes2.twinx()
            self.stateCRAxesList = [self.stateCRAxes1, self.stateCRTwinAxes1, self.stateCRAxes2, self.stateCRTwinAxes2]
            colorList = [snsColorPalette[0], snsColorPalette[3], snsColorPalette[0], snsColorPalette[3]]
            yLabelList = ['Total Cases', 'Total Deaths', 'Daily New cases', 'Daily New Deaths']

            for axes, yattr, c, ylabel in zip(self.stateCRAxesList,
                                              ['total_confirmed', 'total_deceased', 'confirmed', 'deceased'],
                                              colorList,
                                              yLabelList):
                sns.lineplot(data=self.stateDataFrame, x='date', y=yattr, color=c, ax=axes)
                axes.fill_between(self.stateDataFrame['date'].values, self.stateDataFrame[yattr].values,
                                  color=c, alpha=0.3)

                axes.xaxis.set_major_formatter(self.dateFormatter)
                
                maxData = self.stateDataFrame[yattr].values.max()
                nPower = len(str(maxData)) - 1 if len(str(maxData)) > 1 else 0 
                axes.set_yticks(np.linspace(0, self.roundupToNearestPowerTen(maxData, nPower), 5))

                axes.set_ylabel(ylabel, fontsize=13)

                axes.tick_params(axis='both', which='both', length=0, pad=8, labelsize=12)

                axes.yaxis.set_major_formatter(self.intFormatter)

            self.stateCRAxes1.set_xlabel('')
            self.stateCRAxes2.set_xlabel('Date', fontsize=13)
        
            self.stateCRTwinAxes1.grid(False)
            self.stateCRTwinAxes2.grid(False)

            for label in self.stateCRAxes1.get_xticklabels():
                label.set_visible(False)

            for axes in self.stateCRAxesList:
                pos = axes.get_position()
                pos.x0 += 0.1
                pos.x1 -= 0.1
                axes.set_position(pos)

            self.stateCRFigure.suptitle(f'{state} Correlation Line Graph\nCase - Time Series', fontsize=16, linespacing=1.5)
            self.stateCRCanvas.draw()


    def setNewsTab(self):
        self.newsTabLayout = QVBoxLayout()
        self.newsTabLayout.setSpacing(20)
        self.newsTabLayout.setAlignment(Qt.AlignTop)
        self.newsTab.setLayout(self.newsTabLayout)

        self.newsHeadLayout = QHBoxLayout()
        self.newsHeadLayout.setAlignment(Qt.AlignCenter)

        self.newsHeadLoadLabel = QLabel()
        self.newsHeadLoadLabel.setVisible(False)
        self.graphLoadingMovie = QtGui.QMovie(r'.\app-resources\1494.gif')
        self.graphLoadingMovie.start()
        self.newsHeadLoadLabel.setMovie(self.graphLoadingMovie)
        
        self.newsHeadLabel = QLabel()
        self.newsHeadLabel.setAlignment(Qt.AlignCenter)
        self.newsHeadLabel.setStyleSheet('''
            QLabel {
                font-size: 16pt;
                margin: 10px 0px 15px 0px;
                }
            ''')
        
        self.numberOfNewsItem = 20
        
        self.newsItemFrames = []
        
        for i in range(self.numberOfNewsItem):
            self.newsItemFrames.append({'frame': QFrame(objectName=f'newsFrame{i}')})
            self.newsItemFrames[i]['frame'].setVisible(False)
            self.newsItemFrames[i]['frame'].setStyleSheet(f'''#newsFrame{i} {{
                                                                border: 2px solid black;
                                                                }}
                                                          ''')
            self.newsItemFrames[i]['layout'] = QGridLayout()
            self.newsItemFrames[i]['layout'].setAlignment(Qt.AlignLeft)
            self.newsItemFrames[i]['layout'].setVerticalSpacing(0)
            self.newsItemFrames[i]['layout'].setHorizontalSpacing(10)
            self.newsItemFrames[i]['frame'].setLayout(self.newsItemFrames[i]['layout'])

            self.newsItemFrames[i]['title'] = QLabel()
            self.newsItemFrames[i]['title'].setMinimumWidth(1000)
            self.newsItemFrames[i]['title'].setWordWrap(True)
            self.newsItemFrames[i]['title'].setStyleSheet('''QLabel {font-weight: 700;
                                                                     font-size: 12pt;}''')
            self.newsItemFrames[i]['description'] = QLabel()
            self.newsItemFrames[i]['description'].setMinimumWidth(1000)
            self.newsItemFrames[i]['description'].setStyleSheet('QLabel {font-size: 11pt;}')
            self.newsItemFrames[i]['description'].setWordWrap(True)

            self.newsItemFrames[i]['image'] = QLabel()
            #self.newsItemFrames[i]['image'].setStyleSheet('QLabel {border: 2px solid black;}')

            self.newsItemFrames[i]['url'] = QPushButton('Source', objectName=f'{i}')
            self.newsItemFrames[i]['url'].setFlat(True)
            self.newsItemFrames[i]['url'].setStyleSheet('''
                                                        QPushButton:flat {
                                                            color: Blue;
                                                            font-size: 11pt;
                                                            text-align: left;
                                                        }''')
            self.newsItemFrames[i]['url'].clicked.connect(self.linkButtonPressed)
            
            self.newsItemFrames[i]['vline'] = verticalLine()
            
            self.newsItemFrames[i]['layout'].addWidget(self.newsItemFrames[i]['image'], 0, 0, 3, 1, Qt.AlignLeft)
            self.newsItemFrames[i]['layout'].addWidget(self.newsItemFrames[i]['vline'], 0, 1, 3, 1)
            self.newsItemFrames[i]['layout'].addWidget(self.newsItemFrames[i]['title'], 0, 2, Qt.AlignLeft)
            self.newsItemFrames[i]['layout'].addWidget(self.newsItemFrames[i]['description'], 1, 2, Qt.AlignLeft)
            self.newsItemFrames[i]['layout'].addWidget(self.newsItemFrames[i]['url'], 2, 2, Qt.AlignLeft)

        self.newsHeadLayout.addWidget(self.newsHeadLoadLabel)
        self.newsHeadLayout.addWidget(self.newsHeadLabel)
        #self.newsTabLayout.addWidget(self.newsHeadLabel)
        self.newsTabLayout.addLayout(self.newsHeadLayout)
        for i in range(self.numberOfNewsItem):
            self.newsTabLayout.addWidget(self.newsItemFrames[i]['frame'])
            

    def updateNewsTab(self):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()

        location = state if state != '<-- Select State -->' else country

        self.newsHeadLoadLabel.setVisible(True)

        self.newsHeadLabel.setText(location + ' Latest News')

        self.downloadNewsItemsWorker = Worker(self.downloadNewsItems)
        self.downloadNewsItemsWorker.signals.finished.connect(self.updateNewsWidgets)

        self.threadPool.start(self.downloadNewsItemsWorker)

    def downloadNewsItems(self):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()

        location = state if state != '<-- Select State -->' else country
        
        url = ('https://newsapi.org/v2/everything?'
               f'qInTitle=(+corona OR +covid OR +coronavirus) AND {location}&'
               'sortBy=popularity&'
               'pageSize=20&'
               #'sources=google-news-in,the-hindu,the-times-of-india&'
               'apiKey=0324ca0fe426490680ceb5b3e5b6de42')

        response = requests.get(url)
        self.newsDict = response.json()
        self.newsImages = []
        
        for i, itemDict in enumerate(self.newsDict['articles'][:self.numberOfNewsItem]):
            if itemDict['urlToImage']:
                image = QtGui.QPixmap()
                image.loadFromData(requests.get(itemDict['urlToImage']).content)
                image = image.scaled(QtCore.QSize(300, 300),  Qt.KeepAspectRatio)
                self.newsImages.append(image)

    def updateNewsWidgets(self):
        images = iter(self.newsImages)
        
        for i, itemDict in enumerate(self.newsDict['articles'][:self.numberOfNewsItem]):
            self.newsItemFrames[i]['title'].setText(itemDict['title'])
            
            self.newsItemFrames[i]['string_url'] = itemDict['url']

            self.newsItemFrames[i]['description'].setText(itemDict['description'])
            
            #self.newsItemFrames[i]['url'].setText('Source') #itemDict['url']
            self.newsItemFrames[i]['url'].setToolTip(itemDict['url'])
            
            if itemDict['urlToImage']:
                self.newsItemFrames[i]['image'].setPixmap(next(images))

            self.newsItemFrames[i]['frame'].setVisible(True)

        self.newsHeadLoadLabel.setVisible(False)

##        url = ('https://newsapi.org/v2/everything?'
##               f'qInTitle=(+corona OR +covid OR +coronavirus) AND {location}&'
##               'sortBy=popularity&'
##               'pageSize=20&'
##               #'sources=google-news-in,the-hindu,the-times-of-india&'
##               'apiKey=0324ca0fe426490680ceb5b3e5b6de42')
##
##        response = requests.get(url)
##        newsDict = response.json()
##
##        for i, itemDict in enumerate(newsDict['articles'][:self.numberOfNewsItem]):
##            self.newsItemFrames[i]['title'].setText(itemDict['title'])
##            
##            self.newsItemFrames[i]['string_url'] = itemDict['url']
##
##            self.newsItemFrames[i]['description'].setText(itemDict['description'])
##            
##            #self.newsItemFrames[i]['url'].setText('Source') #itemDict['url']
##            self.newsItemFrames[i]['url'].setToolTip(itemDict['url'])
##            
##            if itemDict['urlToImage']:
##                image = QtGui.QPixmap()
##                image.loadFromData(requests.get(itemDict['urlToImage']).content)
##                image = image.scaled(QtCore.QSize(300, 300),  Qt.KeepAspectRatio)
##                self.newsItemFrames[i]['image'].setPixmap(image)
##
##            self.newsItemFrames[i]['frame'].setVisible(True)
            
    def linkButtonPressed(self):
        country = self.countryComboBox.currentText()
        state = self.stateComboBox.currentText()
        loc = state if state != '<-- Select State -->' else country
        
        button = self.sender()
        i = int(button.objectName())

        item = self.newsItemFrames[i]

        self.newsWebPageView = QWebEngineView()
        self.newsWebPageView.setWindowTitle(f'{loc} News')
        self.newsWebPageView.setWindowIcon(QtGui.QIcon(r'.\app-resources\news.png'))
        #self.newsWebPageView.setWindowFlag(Qt.FramelessWindowHint)
        self.newsWebPageView.setFixedSize(750, 900)
        
        self.newsWebPageView.load(QtCore.QUrl(item['string_url']))
        self.newsWebPageView.show()
  

def main():
    """Main function."""
    locale.setlocale(locale.LC_ALL, 'English_India')
    
    # Create an instance of QApplication
    covid_app = QApplication(sys.argv)
    
    # Adding custom Font
    _id = QtGui.QFontDatabase.addApplicationFont(r'.\app-resources\Ubuntu-Regular.ttf')
    covid_app.setFont(QtGui.QFont("Ubuntu"))
    
    # Show the app's GUI
    view = CovidAppUi(covid_app)
    view.show()
    
    # Execute the app's main loop
    sys.exit(covid_app.exec())

if __name__ == '__main__':
    main()
