#!/usr/bin/env python
"""display.py: Builds a GUI. Python 2.7."""

import Tkinter as tk
from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog, tkMessageBox
import math
import random
import numpy as np
import view
import data
from data import ClusterData
import analysis
import copy

__author__ = "Raj Kane"
__version__ = "Project 7"
__date__ = "Spring 2018"


# create a class to build and manage the display
class DisplayApp:
    def __init__(self, width, height):

        #create View object
        self.view = view.View()
        self.viewClone = None
        self.dataObj = data.Data()

        #point colors and sizes
        self.clist = []
        self.slist = []

        #variables associated with linear regression
        self.dialogWindow = None
        self.endpoint1 = None
        self.endpoint2 = None
        self.endpoints = None
        self.line = None
        self.reg_objects = []

        #variables associated with PCA
        self.pcaBoxA = None #the Listbox for PCA
        self.PCANum = 0 #used for labeling principal components
        self.PCAObjects = [] #list that houses PCAData objects

        #variables associated with clustering
        self.ClusterBoxA = None
        self.ClusterObjects = []
        self.codes = None #don't use codes, codebook, or errors
        self.codebook = None
        self.errors = None
        self.ClusterNum = 0
        # self.ClusterColors = [(131,139,139), (156,102,31), (152,245,255), (118,238,0),
        #                       (220,20,60), (154,50,205), (238,18,137), (3,3,3),
        #                       (0,0,128), (255,69,0)]
        #'azure4', 'brick', 'cadetblue1', 'chartreuse2', 'crimson',
        #'darkorchid3', 'deeppink2', 'gray1', 'navy', 'orangered1'

        #building data points
        self.data2plot = None
        self.endpts = np.matrix([[0.0,0.0,0.0,1.0],
                            [1.0,0.0,0.0,1.0],
                            [0.0,0.0,0.0,1.0],
                            [0.0,1.0,0.0,1.0],
                            [0.0,0.0,0.0,1.0],
                            [0.0,0.0,1.0,1.0]])

        # list that contains the actual graphics line objects
        #that instantiate them on the screen
        self.lines = [None, None, None]

        # create a tk object, which is the root window
        self.root = tk.Tk()

        # width and height of the window
        self.initDx = width
        self.initDy = height

        # set up the geometry for the window
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

        # set the title of the window
        self.root.title("Pretty Good Analysis")

        # set the maximum size of the window for resizing
        self.root.maxsize( 1024, 768 )

        # bring the window to the front
        self.root.lift()

        # setup the menus
        self.buildMenus()

        # build the controls
        self.buildControls()

        # build the objects on the Canvas
        self.buildCanvas()

        # set up the key bindings
        self.setBindings()

        # Create the axes fields and build the axes
        # set up the application state
        self.Ax = None
        self.Ay = None
        self.Az = None

        self.objects = []
        self.data = None
        self.buildAxes()
        self.updateAxes()

        #axes lables
        self.labelX = tk.Label(self.canvas,text = 'X')
        self.labelY = tk.Label(self.canvas, text = 'Y')
        self.labelZ = tk.Label(self.canvas, text = 'Z')

        #initialize ui
        self.baseClick1 = None
        self.baseClick2 = None
        self.baseClick3 = None


    def buildMenus(self):

        # create a new menu
        self.menu = tk.Menu(self.root)

        # set the root menu to our new menu
        self.root.config(menu = self.menu)

        # create a variable to hold the individual menus
        self.menulist = []

        # create a file menu
        filemenu = tk.Menu( self.menu )
        self.menu.add_cascade( label = "File", menu = filemenu )
        self.menulist.append(filemenu)

        #create an analysis menu
        analysismenu = tk.Menu(self.menu)
        self.menu.add_cascade(label='Analysis', menu=analysismenu)
        self.menulist.append(analysismenu)

        # menu text for the elements
        menutext = [[ 'Open...  \xE2\x8C\x98-O', '-', 'Quit  \xE2\x8C\x98-Q'],
                    ['Principal Component Analysis', 'Clustering Analysis']]

        # menu callback functions
        menucmd = [[self.handleOpen, None, self.handleQuit],
                    [self.handlePCA, self.handleCluster]]

        # build the menu elements and callbacks
        for i in range(len(self.menulist)):
            for j in range(len(menutext[i])):
                if menutext[i][j] != '-':
                    self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
                else:
                    self.menulist[i].add_separator()

    # create the canvas object
    def buildCanvas(self):
        self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
        self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
        return

    # build a frame and put controls in it
    def buildControls(self):
        # make a control frame
        self.cntlframe = tk.Frame(self.root)
        self.cntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

        sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)

        self.cntlframe2 = tk.Frame(self.cntlframe)
        self.cntlframe2.pack(side=tk.BOTTOM, padx=2, pady=2, fill=tk.Y)

        # make a cmd 1 button in the frame
        self.buttons = []
        self.buttons.append( ( 'reset', tk.Button( self.cntlframe, text="Reset", command=self.handleResetButton, width=5 ) ) )
        self.buttons[-1][1].pack(side=tk.TOP)  # default side is top

        self.buttons.append(('plot', tk.Button(self.cntlframe, text='Plot', command=self.handlePlotData, width = 5)))
        self.buttons[-1][1].pack(side=tk.TOP)

        self.buttons.append(('regression', tk.Button(self.cntlframe, text='Regression', command=self.handleLinearRegression, width=5)))
        self.buttons[-1][1].pack(side=tk.TOP)

        self.pcaBoxA = tk.Listbox(self.cntlframe, selectmode=tk.SINGLE, exportselection=0)
        self.pcaBoxA.pack(side=tk.TOP, padx=0)

        self.buttons.append(('pca', tk.Button(self.cntlframe, text='Plot PCA', command=self.handlePlotPCA, width=5)))
        self.buttons[-1][1].pack(side=tk.TOP)

        self.buttons.append(('delete', tk.Button(self.cntlframe, text='Delete PCA', command=self.handleDeletePCA, width=10)))
        self.buttons[-1][1].pack(side=tk.TOP)

        self.buttons.append(('eigen', tk.Button(self.cntlframe, text='View Eigen', command=self.handleViewPCA, width=10)))
        self.buttons[-1][1].pack(side=tk.TOP)

        self.ClusterBoxA = tk.Listbox(self.cntlframe2, selectmode=tk.SINGLE, exportselection=0)
        self.ClusterBoxA.pack(side=tk.TOP, padx=0)

        self.buttons.append(('plot cluster', tk.Button(self.cntlframe2, text='Plot Cluster', command=self.handlePlotCluster, width=10)))
        self.buttons[-1][1].pack(side=tk.TOP)

        self.buttons.append(('delete cluster', tk.Button(self.cntlframe2, text='Delete Cluster', command=self.handleDeleteCluster, width=10)))
        self.buttons[-1][1].pack(side=tk.TOP)

        self.ClusterText = tk.Text(self.root, height=1, width=60)
        self.ClusterText.pack(side=tk.TOP)

        return

    def buildPoints(self, inputHeaders):
        '''Takes list of headers, deletes existing objects representing data, builds new 
        set of data points.'''
        if len(self.PCAObjects) > 0:
            active = self.pcaBoxA.index(tk.ACTIVE)
            self.dataObj = self.PCAObjects[active]

        if len(self.ClusterObjects) > 0:
            active = self.pcaBoxA.index(tk.ACTIVE)
            self.dataObj = self.ClusterObjects[active]

        # clear the canvas
        for obj in self.objects:
            self.canvas.delete(obj)
        self.objects = []

        # first two variables are given. consider whether z header has been selected
        if (inputHeaders[2] != None):
            self.data2plot = analysis.normalize_columns_separately(inputHeaders[0:3], self.dataObj)
        else:
            self.data2plot = analysis.normalize_columns_separately(inputHeaders[0:2], self.dataObj)

        # consider whether color header has been selected
        if (inputHeaders[3] == None):
            for row in range(self.data2plot.shape[0]):
                self.clist.append((0,0,0))
        else:
            cmatrix = analysis.normalize_columns_separately([inputHeaders[3]], self.dataObj)
            for i in range(cmatrix.shape[0]):
                self.clist.append((int(float(cmatrix[i,0]) * 255), 0, int(255 * (1 - float(cmatrix[i, 0])))))

        # case: size selected, but color not selected

        # consider whether size header has been selected
        if (inputHeaders[4] == None):
            for row in range(self.data2plot.shape[0]):
                self.slist.append(3.0)
        else:
            smatrix = analysis.normalize_columns_separately([inputHeaders[4]], self.dataObj)
            for i in range(smatrix.shape[0]):
                self.slist.append(smatrix[i, 0] * 5)

        zeros = np.zeros((self.data2plot.shape[0], 1))
        ones = np.ones((self.data2plot.shape[0], 1))

        if (inputHeaders[2] == None):
            self.data2plot = np.hstack((self.data2plot, zeros, ones))
        else:
            self.data2plot = np.hstack((self.data2plot, ones))

        self.data2plot = self.data2plot.astype(np.float) 

        #build vtm and use it to transform the data
        vtm = self.view.build()
        pts = (vtm * self.data2plot.T).T 

        #create the canvas graphics objects
        for i in range(pts.shape[0]):
            self.objects.append(self.canvas.create_oval(pts[i, 0] - self.slist[i],
                                                        pts[i, 1] - self.slist[i],
                                                        pts[i, 0] + self.slist[i],
                                                        pts[i, 1] + self.slist[i],
                                                        fill='#%02x%02x%02x'%self.clist[i]))

        self.updatePoints()

    def updatePoints(self):
        '''Builds a new VTM, uses the VTM to transform the matrix of data points, then updates 
        the coordinates of each data point.'''
        if (len(self.objects))==0:
            return
        else:
            vtm = self.view.build()
            pts = (vtm * self.data2plot.T).T
            for i in range(len(self.objects)):
                dist = self.slist[i]
                self.canvas.coords(self.objects[i], pts[i,0] - dist, pts[i, 1] - dist,
                pts[i,0] + dist, pts[i, 1] + dist)
            return

    def buildAxes(self):
        '''Creates the axis line objects in their default location.'''
        vtm = self.view.build()
        pts = (vtm * self.endpts.T).T

        self.Ax = self.canvas.create_line(pts[0, 0], pts[0, 1], pts[1, 0], pts[1, 1], fill="red")
        self.Ay = self.canvas.create_line(pts[2, 0], pts[2, 1], pts[3, 0], pts[3, 1], fill="blue")
        self.Az = self.canvas.create_line(pts[4, 0], pts[4, 1], pts[5, 0], pts[5, 1], fill="green")
        self.A = [self.Ax, self.Ay, self.Az]

        #add axis labels
        self.labelX = tk.Label(self.canvas, text='X')
        self.labelY = tk.Label(self.canvas, text='Y')
        self.labelZ = tk.Label(self.canvas, text='Z')

        self.labelX.place(x=pts[1, 0], y=pts[1, 1])
        self.labelY.place(x=pts[3, 0], y=pts[3, 1])
        self.labelZ.place(x=pts[5, 0], y=pts[5, 1])

    def updateAxes(self):
        '''Modifies the endpoints of the axes to their new location.'''
        vtm = self.view.build()
        pts = (vtm * self.endpts.T).T
        self.canvas.coords(self.Ax, pts[0, 0], pts[0, 1], pts[1, 0], pts[1, 1])
        self.canvas.coords(self.Ay, pts[2, 0], pts[2, 1], pts[3, 0], pts[3, 1])
        self.canvas.coords(self.Az,pts[4, 0], pts[4, 1], pts[5, 0], pts[5, 1])

        self.labelX.place(x=pts[1, 0], y=pts[1, 1])
        self.labelY.place(x=pts[3, 0], y=pts[3, 1])
        self.labelZ.place(x=pts[5, 0],y=pts[5, 1])

    def setBindings(self):
        self.root.bind( '<Button-1>', self.handleButton1 )
        self.root.bind( '<Control-Button-1>', self.handleButton2 )
        self.root.bind( '<Shift-Button-1>', self.handleButton3 )
        self.root.bind( '<B1-Motion>', self.handleButton1Motion )
        self.root.bind( '<Control-B1-Motion>', self.handleButton2Motion )
        self.root.bind( '<Shift-B1-Motion>', self.handleButton3Motion )
        self.root.bind( '<Control-q>', self.handleQuit )
        self.root.bind( '<Control-o>', self.handleModO )
        self.canvas.bind( '<Configure>', self.handleResize )
        return

##### CLUSTERING #####

    def handleCluster(self, event=None):
        '''Creates ClusterDialog object.'''
        print('handleCluster')
        self.ClusterWindow = ClusterDialog(self.root, self.dataObj)

        if self.ClusterWindow.headers == None:
            tkMessageBox.showerror('No File Opened!', 'Please open a file first')
            return

        if self.ClusterWindow.result == None:
            return

        self.ClusterObjects = []

        A = self.dataObj.columns_data(self.ClusterWindow.result[0])
        A = A.astype(float)
        m = np.mean(A, axis=0)
        D = A - m
        U, S, V = np.linalg.svd(D, full_matrices=False)
        projectedData = (V * D.T).T

        means, codebook, self.errors = analysis.kmeans(self.dataObj, self.ClusterWindow.result[0], self.ClusterWindow.result[1])
        c_object = ClusterData(projectedData, self.ClusterWindow.result[0], self.ClusterWindow.result[1], codebook, means, self.errors)
        self.ClusterObjects.append(c_object)
        codebook = codebook.T.tolist()[0]
        self.dataObj.addColumn(codebook, 'cluster', 'numeric')
        if self.ClusterWindow.result[1] == None:
            name = 'Cluster' + str(self.ClusterNum)
            self.ClusterNum += 1
        else:
            name = self.ClusterWindow.result[1]

        self.ClusterBoxA.insert(tk.END, name)

    def handlePlotCluster(self, event=None):
        print('handlePlotCluster')
        if len(self.ClusterObjects) > 0:
            quality = analysis.kmeans_quality(self.errors, int(self.ClusterWindow.result[1]))
            self.ClusterText.delete('1.0', tk.END)
            self.ClusterText.insert(tk.END, 'Quality: ')
            self.ClusterText.insert(tk.END, quality[0,0])
            active = self.ClusterBoxA.index(tk.ACTIVE)
            dat = self.ClusterObjects[active]
            c = ClusterDisplayDialog(self.root, dat)
            self.buildPoints(c.result)
        return

    def buildClusterColors(self, K):
        self.ClusterColors = []
        additionalColors = [(0,0,128), (220,20,60), (131,139,139), (156,102,31), (152,245,255), (118,238,0),
                            (154,50,205), (238,18,137), (3,3,3), (255,69,0)]
        #'azure4', 'brick', 'cadetblue1', 'chartreuse2', 'crimson',
        #'darkorchid3', 'deeppink2', 'gray1', 'navy', 'orangered1'
        if K <= 10:
            for i in range(K):
                c = additionalColors[i]
                self.ClusterColors.append(c)
        else:
            for i in range(10):
                c = additionalColors[i]
                self.ClusterColors.append(c)
            for i in range(K-10):
                c = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
                if c in self.ClusterColors:
                    tkMessageBox.showerror('Color used twice!', 'Sorry, please run again.')
                    #Ideally, instead of this message box, I can implement a while loop
                    #such that c keeps getting a random RGB value until it isn't in self.ClusterColors
                self.ClusterColors.append(c)

    def handleDeleteCluster(self):
        if len(self.ClusterObjects) > 0:
            active = self.ClusterBoxA.index(tk.ACTIVE)
            self.ClusterBoxA.delete(active)
            del self.ClusterObjects[active]
            return

##### PRINCIPAL COMPONENT ANALYSIS ######

    #create PCADialog object
    def handlePCA(self, event=None):
        print('handlePCA')
        self.PCAWindow = PCADialog(self.root, self.dataObj)

        if self.PCAWindow.headers == None:
            tkMessageBox.showerror('No File Opened!', 'Please open a file first')
            return

        if self.PCAWindow.result == None:
            return

        self.PCAObjects = []
        #check whether normalization is required
        if self.PCAWindow.result[0] == 1:
            self.PCAObjects.append(analysis.pca(self.dataObj, self.PCAWindow.result[1]))
        else:
            self.PCAObjects.append(analysis.pca(self.dataObj, self.PCAWindow.result[1], False))

        #analysis name
        if self.PCAWindow.result[2] == None:
            PCAName = "PCA" + str(self.PCANum)
            self.PCANum += 1
        else:
            PCAName = self.PCAWindow.result[2]

        self.pcaBoxA.insert(tk.END, PCAName)

    def handleDeletePCA(self):
        if len(self.PCAObjects) > 0:
            active = self.pcaBoxA.index(tk.ACTIVE)
            self.pcaBoxA.delete(active)
            del self.PCAObjects[active]
            return

    def handleViewPCA(self):
        if len(self.PCAObjects) > 0:
            active = self.pcaBoxA.index(tk.ACTIVE)
            dat = self.PCAObjects[active] #this is a PCAData object
            e = EigenDialog(self.root, dat)

    def handlePlotPCA(self, event=None):
        if len(self.PCAObjects) > 0:
            active = self.pcaBoxA.index(tk.ACTIVE)
            dat = self.PCAObjects[active] #this is a PCAData object
            e = EigenDisplayDialog(self.root, dat)
            self.labelX = tk.Label(self.canvas, text = 'PCA0') #might want to use stringvar instead
            self.labelY = tk.Label(self.canvas, text = 'PCA1')
            self.labelZ = tk.Label(self.canvas, text = 'PCA2')
            self.buildPoints(e.result)
        return

##### LINEAR REGRESSION #####

    def handleLinearRegression(self, event=None): #added event
        '''Creates the linear regression dialog window.'''
        print('handleLinearRegression')
        self.dialogWindow = RegressionDialog(self.root, self.dataObj)
        self.updateRegression()
        self.buildLinearRegression()
        self.updateRegression()

    def buildLinearRegression(self):
        if self.dialogWindow.getIV2() == None:
            headers = [self.dialogWindow.getIV(), self.dialogWindow.getDV()]
            normalized = analysis.normalize_columns_separately(headers, self.dataObj)
            zeros = np.zeros((normalized.shape[0], 1))
            normalized = np.hstack((normalized, zeros))
            ones = np.ones((normalized.shape[0], 1))
            normalized = np.hstack((normalized, ones))

            vtm = self.view.build()
            pts = (vtm*self.data2plot.T).T

            (m, b, rVal, pVal, stdErr, indRange, depRange) = analysis.single_linear_regression(
            self.dataObj, [self.dialogWindow.getIV()], [self.dialogWindow.getDV()])

            self.endpoint1 = ((indRange[0][0] * m + b) - depRange[0][0]) / (depRange[0][1] - depRange[0][0])
            self.endpoint2 = ((indRange[0][1] * m + b) - depRange[0][0]) / (depRange[0][1] - depRange[0][0])
            self.endpoints = np.matrix([[0., self.endpoint1, 0., 1.],
                                        [1., self.endpoint2, 0., 1.]])
            self.endpoints = (vtm * self.endpoints.T)
            self.line = self.canvas.create_line(self.endpoints[0, 0], self.endpoints[1, 0],
            self.endpoints[0, 1],self.endpoints[1, 1], fill="orange")
            self.reg_objects.append(self.line)

            self.buildRegressionLegend(m, b, rVal)
            return

        else:
            indHeaders = [self.dialogWindow.getIV(), self.dialogWindow.getIV2()]
            (b, sse, r2, t, p) = analysis.linear_regression(self.dataObj, indHeaders, self.dialogWindow.getDV())
            self.buildMultipleRegressionLegend(b, sse, r2, t, p)
            return

    def updateRegression(self):
        vtm = self.view.build()
        (m, b, rVal, pVal, stdErr, indRange, depRange) = analysis.single_linear_regression(
        self.dataObj, [self.dialogWindow.getIV()], [self.dialogWindow.getDV()])

        self.endpoint1 = ((indRange[0][0] * m + b) - depRange[0][0]) / (depRange[0][1] - depRange[0][0])
        self.endpoint2 = ((indRange[0][1] * m + b) - depRange[0][0]) / (depRange[0][1] - depRange[0][0])
        self.endpoints = np.matrix([[0., self.endpoint1, 0., 1.],
                                    [1., self.endpoint2, 0., 1.]])
        self.endpoints = (vtm * self.endpoints.T)

        for i in range(len(self.reg_objects)):
            self.canvas.coords(self.reg_objects[i], self.endpoints[0, 0], self.endpoints[1, 0],
            self.endpoints[0,1],self.endpoints[1, 1])

    def buildRegressionLegend(self, slope, intercept, r):
        t = 'Slope: {0} \nIntercept: {1} \nR2: {2}'.format(round(slope, 3),round(intercept, 3),round(r * r, 3))
        self.legendText = tk.Label(self.cntlframe, text=t, width=20, justify=tk.LEFT)
        self.legendText.pack(side=tk.BOTTOM)

    def buildMultipleRegressionLegend(self, slope, sse, r, t, p):
        slopes = 'm0: {0} \nm1: {1} \nm2: {2}'.format(round(slope[0], 3), round(slope[1], 3), round(slope[2], 3))
        tVals = '\nt0: {0} \nt1: {1} \nt2: {2}'.format(round(t[0], 3), round(t[1], 3), round(t[2], 2))
        pVals = '\np0: {0} \np1: {1} \np2: {2}'.format(round(p[0],3), round(p[1], 3), round(p[2], 3))
        string = slopes + tVals + pVals + '\nSSE: {0} \nR2: {1}'.format(round(sse,3), round(r * r, 3))
        self.legendText = tk.Label(self.cntlframe, text = string, width = 15, justify = tk.LEFT)
        self.legendText.pack(side=tk.BOTTOM)

##### PLOTTING, OPENING, RESETTING #####

    def handleResize(self, event=None):
        # You can handle resize events here
        pass

    def handleChooseAxes(self,event=None):
        print('handleChooseAxes')
        var = data.Data()
        self.headers = var.get_headers()
        return self.headers

    def handlePlotData(self):
        print('handlePlotData')
        self.handleChooseAxes()
        self.dialogWindow = AxesDialog(self.root, self.dataObj)
        self.buildPoints(self.dialogWindow.result)

    def handleOpen(self):
        print('handleOpen')
        fn = tkFileDialog.askopenfilename(parent=self.root,title='Choose a data file', initialdir='.')
        self.dataObj = data.Data(fn)
        self.handlePlotData()

    def handleModO(self, event):
        self.handleOpen()

    def handleQuit(self, event=None):
        print('Terminating')
        self.root.destroy()

    def handleResetButton(self):
        print('handling reset button')
        self.canvas.delete('all')
        self.view.reset()
        print 'reset A is ', self.A

        try:
            self.legendText.destroy()
        except AttributeError:
            pass
        print 'destroy A is ', self.A

        self.buildAxes()
        print 'build A is ', self.A
        self.objects = []
        print 'object A is ', self.A
        self.reg_objects = []
        print 'reg A is ', self.A
        self.updateAxes()
        print 'update A is ', self.A
        self.updatePoints()
        print 'points A is', self.A
        self.updateRegression()

#####
##### BUTTON AND MOTION CAPABILITIES #####

    def handleButton1(self, event):
        print('handle button 1: %d %d' % (event.x, event.y))
        self.baseClick1 = (event.x, event.y)

    def handleButton1Motion(self, event):
        print('handle button 1 motion: %d %d' % (event.x, event.y) )
        dx = (event.x - self.baseClick1[0]) / self.view.screen[0]
        dy = (event.y - self.baseClick1[1]) / self.view.screen[1]
        delta0 = 0.01 * dx * self.view.screen[0]
        delta1 = 0.7 * dy * self.view.extent[1]
        self.view.vrp = delta0 * self.view.u + delta1 * self.view.vup
        self.updateAxes()
        self.updatePoints()
        self.updateRegression()

    def handleButton2(self, event):
        print('handle button 2: %d %d' % (event.x, event.y))
        self.baseClick2 = (event.x, event.y)
        self.viewClone = self.view.clone()

    def handleButton2Motion(self, event):
        print('handle button 2 motion: %d %d' % (event.x, event.y) )
        diff = (event.x - self.baseClick2[0], event.y - self.baseClick2[1])
        self.view = self.viewClone.clone()
        delta0 = (-diff[0]) / (1.0 * self.canvas.winfo_height()) * math.pi
        delta1 = (diff[1]) / (1.0 * self.canvas.winfo_width()) * math.pi
        degx = delta0 * (180 / math.pi)
        degy = -delta1 * (180 / math.pi)

        self.view.rotateVRC(delta1, delta0)
        self.updateAxes()
        self.updatePoints()
        self.updateRegression()

    def handleButton3(self, event):
        print('handle button 3: %d %d' % (event.x, event.y))
        self.baseClick3 = (event.x, event.y)
        self.viewClone = self.view.clone()
        self.baseExtent = self.viewClone.extent[:]

    def handleButton3Motion( self, event):
        print('handle button 3 motion: %d %d' % (event.x, event.y) )
        #convert the distance between the base click and the current mouse position into a scale factor
        #only look at y, not x, because this works as a "vertical lever"
        dist = float(event.y - self.baseClick3[1])
        scale_factor = 1.0 + (dist / self.canvas.winfo_screenheight())
        scale_factor = max(min(scale_factor, 3.0), 0.1)
        self.view.extent = [self.baseExtent[0] * scale_factor, self.baseExtent[1] * scale_factor, self.baseExtent[2] * scale_factor]
        self.updatePoints()
        self.updateAxes()
        self.updateRegression()

    def main(self):
        print('Entering main loop')
        self.root.mainloop()

class Dialog(tk.Toplevel):

    def __init__(self, parent, title = None):

        tk.Toplevel.__init__(self, parent)
        self.transient(parent)

        if title:
            self.title(title)

        self.parent = parent

        self.result = []

        self.color = 0
        self.size = 0
        self.z = 0

        self.cancelled = False

        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                  parent.winfo_rooty()+50))

        self.initial_focus.focus_set()

        self.wait_window(self)

    # construction hooks

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.  this method should be overridden

        pass

    def buttonbox(self):
       #button box creates ok and cancel buttons which allow user to register or cancel
       # their entries

        box = tk.Frame(self)

        ok = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        ok.pack(side=tk.LEFT, padx=5, pady=5)

        cncl = tk.Button(box, text="Cancel", width=10, command=self.cancel)

        cncl.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    # standard button semantics
    def ok(self, event=None):

        if not self.validate():
            self.initial_focus.focus_set() # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.cancel()

    def cancelled(self):
        return self.cancelled

    def cancel(self, event=None):
        self.cancelled = True
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()

    # command hooks
    def validate(self):
        return 1 # override

    def apply(self):
       pass

class MyDialog(Dialog):

    def __init__(self, parent, data):
        Dialog.__init__(self,parent)
        self.result=[]
        self.size = ["6"]
        self.color=["black"]
        self.headers = data.get_headers()
        self.dep_list = None
        self.ind_list = None

    def body(self, master):

        variable = StringVar(master)
        variable.set("x") # default value

        self.beginVar = tk.StringVar()
        self.beginVar.set("1-10")

        #e1 stores user input for number of points
        self.e1 = tk.Entry(master, textvariable = self.beginVar)
        self.e1.focus_set()
        self.e1.selection_range(0, tk.END)

        self.e1.grid(row=0, column=1)
        return self.e1 # initial focus

## Handles user selection of which data to display.
class AxesDialog(Dialog):

    def __init__(self,parent,data):
        self.headers = data.get_headers()
        Dialog.__init__(self,parent,'Choose Axes')

    def body(self,master):
        self.Label = tk.Label(master, text="X                                   Y                                   Z                                   Color                                   Size")
        self.xbox = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.headers)):
            self.xbox.insert(tk.END, self.headers[i])

        self.ybox = tk.Listbox(master,selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.headers)):
            self.ybox.insert(tk.END, self.headers[i])

        self.zbox = tk.Listbox(master,selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.headers)):
            self.zbox.insert(tk.END, self.headers[i])

        self.colorbox = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.headers)):
            self.colorbox.insert(tk.END, self.headers[i])

        self.sizebox = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.headers)):
            self.sizebox.insert(tk.END, self.headers[i])

        self.Label.pack(side=tk.TOP)
        self.xbox.pack(side=tk.LEFT)
        self.ybox.pack(side=tk.LEFT)
        self.zbox.pack(side=tk.LEFT)
        self.colorbox.pack(side=tk.LEFT)
        self.sizebox.pack(side=tk.LEFT)


    def apply(self):
        self.result.append(self.headers[self.xbox.curselection()[0]])
        self.result.append(self.headers[self.ybox.curselection()[0]])

        if len(self.zbox.curselection()) > 0:
    		self.result.append(self.headers[self.zbox.curselection()[0]])
        else:
    		self.result.append(None)

        if len(self.colorbox.curselection()) > 0:
    		self.result.append(self.headers[self.colorbox.curselection()[0]])
    	else:
    		self.result.append(None)

        if len(self.sizebox.curselection()) > 0:
    		self.result.append(self.headers[self.sizebox.curselection()[0]])
    	else:
    		self.result.append(None)

        pass

    def getVars(self):
        return self.result

    def getZresult(self):
        return self.headers([self.zbox.curselection()[0]])

    def getColorResult(self):
        return self.headers([self.colorbox.curselection()[0]])

    def getSizeResult(self):
        return self.headers([self.sizebox.curselection()[0]])

## Handles user selection of regression variables.
class RegressionDialog(Dialog):
    def __init__(self,parent,data):
        self.headers = data.get_headers()
        self.DV_list = None
        self.IV_list = None
        Dialog.__init__(self, parent, 'Choose variables for Regression')

    def body(self,master):
        Variable_label = tk.Label(master,text='Dependent                   Independent                   Independent')
        Variable_label.pack(side=tk.TOP)
        self.DV_list = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        self.IV_list = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        self.IV_list2 = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.headers)):
            self.DV_list.insert(tk.END, self.headers[i])
            self.IV_list.insert(tk.END, self.headers[i])
            self.IV_list2.insert(tk.END, self.headers[i])
        self.DV_list.pack(side=tk.LEFT)
        self.IV_list.pack(side=tk.LEFT)
        self.IV_list2.pack(side=tk.LEFT)

    def apply(self):
        self.variables = []
        if len(self.DV_list.curselection()) > 0:
            self.variables.append(self.headers[self.DV_list.curselection()[0]])
        else:
            self.variables.append(None)

        if len(self.IV_list.curselection()) > 0:
            self.variables.append(self.headers[self.IV_list.curselection()[0]])
        else:
            self.variables.append(None)

        if len(self.IV_list2.curselection()) > 0:
            self.variables.append(self.headers[self.IV_list2.curselection()[0]])
        else:
            self.variables.append(None)

        pass

    def cancelled(self):
        self.cancel()

    def getIV(self):
        return self.variables[1]

    def getIV2(self):
        return self.variables[2]

    def getDV(self):
        return self.variables[0]

## Handles user selection of variables for principal component analysis.
class PCADialog(Dialog):
    def __init__(self, parent, data):
        self.headers = data.get_headers()
        self.check = tk.IntVar(parent, value=0) # whether data should be normalized
        self.name = tk.StringVar(parent, value='')
        self.PCA_box = None
        Dialog.__init__(self, parent, 'PCA')

    def body(self, master):
        Variable_label = tk.Label(master, text='PCA Variables')
        Variable_label.pack(side=tk.TOP)

        self.PCA_box = tk.Listbox(master, selectmode=tk.MULTIPLE, exportselection=0)
        # insert headers into the pca dialog
        for i in range(len(self.headers)):
            self.PCA_box.insert(tk.END, self.headers[i])
        self.PCA_box.pack(side=tk.TOP)

        Name_label = tk.Label(master, text='Name')
        Name_label.pack(side=tk.TOP)

        Analysis_entry = tk.Entry(master, textvariable=self.name)
        Analysis_entry.pack(side=tk.TOP)

        Normalize_button = tk.Checkbutton(master, text='Normalize', variable=self.check)
        Normalize_button.pack(side=tk.TOP)

    def apply(self):
        self.result = [self.check.get()]
        variables = []
        for i in range(len(self.PCA_box.curselection())):
            variables.append(self.headers[self.PCA_box.curselection()[i]])

        if len(variables) < 3:
            tkMessageBox.showerror('Not enough variables', 'At least three variables required')
            return

        self.result.append(variables)
        self.result.append(self.name.get())

    def getVars(self):
        return self.result

## Handles display of eigenvectors and associated values.
class EigenDialog(Dialog):
    def __init__(self, parent, data):
        self.evectors = data.get_eigenvectors()
        self.evalues =  data.get_eigenvalues() #convert from np array to python list
        self.headers = data.get_headers()
        self.eheaders = data.get_original_headers()
        Dialog.__init__(self, parent, 'PCA')

    def body(self, master):
        tk.Label(master, text="Eigenvector").grid(row=0, column=0)
        tk.Label(master, text="Eigenvalue").grid(row=0, column=1)

        for i in range(self.evalues.shape[0]):
            tk.Label(master, text=str(self.eheaders[i])).grid(row=0, column=i+2)

        for j in range(len(self.headers)):
            tk.Label(master, text=str(self.headers[j])).grid(row=j+1, column=0)

        for k in range(self.evalues.shape[0]):
            tk.Label(master, text='%1.5f'%self.evalues[k]).grid(row=k+1, column=1)

        for l in range(self.evectors.shape[0]):
            for m in range(self.evectors.shape[0]):
                tk.Label(master, text='%1.5f'%self.evectors[l,m]).grid(row=l+1, column=m+2)

    def apply(self):
        pass

## Handles dimensions for PCA.
class EigenDisplayDialog(Dialog):
    def __init__(self, parent, data):
        self.eheaders = data.get_headers()
        self.PCA_box = None
        Dialog.__init__(self, parent, 'PCA')

    def body(self, master):
        self.Label = tk.Label(master, text="X                                   Y                                   Z                                   Color                                   Size")

        self.Box_X = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.eheaders)):
            self.Box_X.insert(tk.END, self.eheaders[i])

        self.Box_Y = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.eheaders)):
            self.Box_Y.insert(tk.END, self.eheaders[i])

        self.Box_Z = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.eheaders)):
            self.Box_Z.insert(tk.END, self.eheaders[i])

        self.Box_C = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.eheaders)):
            self.Box_C.insert(tk.END, self.eheaders[i])

        self.Box_S = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.eheaders)):
            self.Box_S.insert(tk.END, self.eheaders[i])


        self.Label.pack(side=tk.TOP)
        self.Box_X.pack(side=tk.LEFT, padx=5)
        self.Box_Y.pack(side=tk.LEFT, padx=5)
        self.Box_Z.pack(side=tk.LEFT, padx=5)
        self.Box_C.pack(side=tk.LEFT, padx=5)
        self.Box_S.pack(side=tk.LEFT, padx=5)

        self.epoints = tk.Entry(self)
        self.epoints.pack()

    def apply(self):
        self.result = []
        if len(self.Box_X.curselection()) > 0:
            self.result.append(self.eheaders[self.Box_X.curselection()[0]])
        else:
            self.result.append(None)

        if len(self.Box_Y.curselection()) > 0:
            self.result.append(self.eheaders[self.Box_Y.curselection()[0]])
        else:
            self.result.append(None)

        if len(self.Box_Z.curselection()) > 0:
            self.result.append(self.eheaders[self.Box_Z.curselection()[0]])
        else:
            self.result.append(None)

        if len(self.Box_C.curselection()) > 0:
            self.result.append(self.eheaders[self.Box_C.curselection()[0]])
        else:
            self.result.append(None)

        if len(self.Box_S.curselection()) > 0:
            self.result.append(self.eheaders[self.Box_S.curselection()[0]])
        else:
            self.result.append(None)

    def getVars(self):
        return self.result

## Handles user selection of variables for clustering.
class ClusterDialog(Dialog):
    def __init__(self, parent, data):
        self.headers = data.get_headers()
        self.name = tk.StringVar(parent, value='') #number of clusters
        self.Cluster_box = None
        Dialog.__init__(self, parent, 'K-Means Clustering')

    def body(self, master):
        Variable_label = tk.Label(master, text='Clustering Variables')
        Variable_label.pack(side=tk.TOP)

        self.Cluster_box = tk.Listbox(master, selectmode=tk.MULTIPLE, exportselection=0)
        # insert headers into the cluster dialog
        for i in range(len(self.headers)):
            self.Cluster_box.insert(tk.END, self.headers[i])
        self.Cluster_box.pack(side=tk.TOP)

        cluster_label = tk.Label(master, text='K value')
        cluster_label.pack(side=tk.TOP)

        cluster_entry = tk.Entry(master, textvariable=self.name) #number of clusters
        cluster_entry.pack(side=tk.TOP)





    def apply(self):
        self.result = []
        variables = []
        for i in range(len(self.Cluster_box.curselection())):
            variables.append(self.headers[self.Cluster_box.curselection()[i]])

        if len(variables) < 3:
            tkMessageBox.showerror('Not enough variables', 'At least three variables required')
            return

        self.result.append(variables)
        self.result.append(self.name.get())
        #self.result.append(int(self.numClusters.get()))

    def getResult(self):
        return self.result

    def getName(self):
        return self.name

#handles dimensions for clustering
class ClusterDisplayDialog(Dialog):
    def __init__(self, parent, data):
        self.cheaders = data.get_headers()
        self.Cluster_box = None
        Dialog.__init__(self, parent, 'Clustering')

    def body(self, master):
        self.Label = tk.Label(master, text="X                                   Y                                   Z                                   Color                                   Size")

        self.Box_X = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.cheaders)):
            self.Box_X.insert(tk.END, self.cheaders[i])

        self.Box_Y = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.cheaders)):
            self.Box_Y.insert(tk.END, self.cheaders[i])

        self.Box_Z = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.cheaders)):
            self.Box_Z.insert(tk.END, self.cheaders[i])

        self.Box_C = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.cheaders)):
            self.Box_C.insert(tk.END, self.cheaders[i])

        self.Box_S = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0)
        for i in range(len(self.cheaders)):
            self.Box_S.insert(tk.END, self.cheaders[i])

        self.Label.pack(side=tk.TOP)
        self.Box_X.pack(side=tk.LEFT, padx=5)
        self.Box_Y.pack(side=tk.LEFT, padx=5)
        self.Box_Z.pack(side=tk.LEFT, padx=5)
        self.Box_C.pack(side=tk.LEFT, padx=5)
        self.Box_S.pack(side=tk.LEFT, padx=5)

    def apply(self):
        self.result = []
        if len(self.Box_X.curselection()) > 0:
            self.result.append(self.cheaders[self.Box_X.curselection()[0]])
        else:
            self.result.append(None)

        if len(self.Box_Y.curselection()) > 0:
            self.result.append(self.cheaders[self.Box_Y.curselection()[0]])
        else:
            self.result.append(None)

        if len(self.Box_Z.curselection()) > 0:
            self.result.append(self.cheaders[self.Box_Z.curselection()[0]])
        else:
            self.result.append(None)

        if len(self.Box_C.curselection()) > 0:
            self.result.append(self.cheaders[self.Box_C.curselection()[0]])
        else:
            self.result.append(None)

        if len(self.Box_S.curselection()) > 0:
            self.result.append(self.cheaders[self.Box_S.curselection()[0]])
        else:
            self.result.append(None)

    def getVars(self):
        return self.result

    def getName(self):
        return self.name


if __name__ == "__main__":
    dapp = DisplayApp(700, 500)
    dapp.main()
