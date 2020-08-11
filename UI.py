from PyQt5.QtWidgets import * 
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import * 

import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from pricing import option

class BlackScholesUI(QDialog):
    def __init__(self, parent=None):
        super(BlackScholesUI, self).__init__(parent)

        self.originalPalette = QApplication.palette()
        
        self.outputs = ['Price', 'delta', 'vega', 'theta', 'rho', 'omega',\
                        'gamma', 'vanna', 'charm', 'vomma', 'veta', 'speed', \
                            'zomma', 'color', 'ultima', 'dualDelta', 'dualGamma']
            
        self.optionsList = []
            
        self.addOptionSelector()
        self.addOptionInputs()
        self.greeksView()
        self.sweepInput()
        self.sweepOutput()
        self.optionsDisplay()
        self.plotWindow()
        
        leftLayout = QVBoxLayout()
        leftLayout.addWidget(self.optionsSelection)
        leftLayout.addWidget(self.optionsInput)
        leftLayout.addWidget(self.greeksBox)

        rightLayout = QGridLayout()
        rightLayout.addLayout(self.inputBox, 0, 0, 1, 3)
        rightLayout.addWidget(self.outputSelectList, 1, 0, 5, 3)
        
        bottomLayout = QGridLayout()
        bottomLayout.addWidget(self.optionsBox, 0, 0, 2, 7)
        MATLABButton = QPushButton("Export to MATLAB")
        bottomLayout.addWidget(MATLABButton, 2, 0, 3, 3)
        plotButton = QPushButton("Plot Sweep Outputs")
        bottomLayout.addWidget(plotButton, 2, 3, 3, 4)
        
        mainLayout = QGridLayout()
        mainLayout.addLayout(leftLayout, 0, 0, 3, 4)
        mainLayout.addLayout(rightLayout, 0, 9, 3, -1)
        mainLayout.addLayout(bottomLayout, 3, 4, -1, 5)
        mainLayout.addWidget(self.plotGroupBox, 0, 4, 3, 5)
        
        mainLayout.setColumnStretch(0, 1)
        mainLayout.setColumnStretch(1, 1)
        mainLayout.setColumnStretch(2, 1)
        mainLayout.setColumnStretch(3, 2)
        mainLayout.setColumnStretch(4, 2)
        mainLayout.setColumnStretch(5, 2)
        mainLayout.setColumnStretch(6, 1)
        mainLayout.setColumnStretch(7, 1)
        mainLayout.setColumnStretch(8, 1)
        self.setLayout(mainLayout)
        
        self.setFixedSize(1440, 900) 
        
        self.setWindowTitle("Black-Scholes Calculations")
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        
    def addOptionSelector(self):
        self.optionsSelection = QGroupBox('Select')
        addOptionButton = QPushButton("Add Option")
        addOptionButton.clicked.connect(self.onOptionsAddClicked) 
        self.optionsTypeBox = QComboBox()
        self.optionsTypeBox.addItems(['Long Call', 'Long Put', 'Short Call', 'Short Put'])
        
        layout = QHBoxLayout()
        layout.addWidget(addOptionButton)
        layout.addWidget(self.optionsTypeBox)
        layout.addStretch(1)
        self.optionsSelection.setLayout(layout)
        
    def onOptionsAddClicked(self):
        marketPrice = None
        vol = None
        K = None
        expDay = None
        S0 = None
        q = 0
        r = None
        try:
            K = float(self.kEdit.text())
        except ValueError:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle("Error")
            msgBox.setText("Please Enter a Strike Price")
            msgBox.exec_()
        try:
            expDay = str(self.TEdit.text())
        except ValueError:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle("Error")
            msgBox.setText("Please Enter an Expiration")
            msgBox.exec_()
        try:
            S0 = float(self.S0Edit.text())
        except ValueError:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle("Error")
            msgBox.setText("Please Enter a Stock Price")
            msgBox.exec_()
        try:
            q = float(self.qEdit.text())
        except ValueError:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle("Error")
            msgBox.setText("Please Enter a Dividend Yield")
            msgBox.exec_()
        try:
            r = float(self.rEdit.text())
        except ValueError:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle("Error")
            msgBox.setText("Please Enter a Risk Free Rate")
            msgBox.exec_()
        try:
            vol = float(self.volEdit.text())
        except ValueError:
            try:
                marketPrice = float(self.mpEdit.text())
            except ValueError:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setWindowTitle("Error")
                msgBox.setText("Please Enter a Market Price or Volatility")
                msgBox.exec_()
                
        if 'Long' in self.optionsTypeBox.currentText():
            ls = 'Long'
        elif 'Short' in self.optionsTypeBox.currentText():
            ls = 'Short'
        if 'Call' in self.optionsTypeBox.currentText():
            otype = 'Call'
        elif 'Put' in self.optionsTypeBox.currentText():
            otype = 'Put'
        
        if K and expDay and S0 and (q is not None) and r and (vol or marketPrice):
            if marketPrice is None:
                opt = option(otype=otype, K=K, expDay=expDay, S0=S0, vol=vol, q=q, r=r, ls=ls)
            elif vol is None:
                opt = option(otype=otype, K=K, expDay=expDay, S0=S0, marketPrice=marketPrice, q=q, r=r, ls=ls)
            self.optionsList.append(opt)
            self.updateOptionsDisplay()
            
            
    def updateOptionsDisplay(self):
        for i, opt in enumerate(self.optionsList):
            self.optionsTable.setItem(i+1, 0, QTableWidgetItem(opt.ls + ' ' + opt.otype))
            self.optionsTable.setItem(i+1, 1, QTableWidgetItem(str(opt.K)))
            self.optionsTable.setItem(i+1, 2, QTableWidgetItem(opt.expDayStr))
            self.optionsTable.setItem(i+1, 3, QTableWidgetItem(str(opt.S0)))
            
    def addOptionInputs(self):
        self.optionsInput = QGroupBox('Option Inputs')
        
        kLabel = QLabel("&Strike:")
        self.kEdit = QLineEdit()
        kLabel.setBuddy(self.kEdit)
        
        TLabel = QLabel("&Expiration Date (YYYY-MM-DD):")
        self.TEdit = QLineEdit()
        TLabel.setBuddy(self.TEdit)
        
        S0Label = QLabel("&Underlying Price:")
        self.S0Edit = QLineEdit()
        S0Label.setBuddy(self.S0Edit)
        
        volLabel = QLabel("&Volatility:")
        self.volEdit = QLineEdit()
        volLabel.setBuddy(self.volEdit)
        
        mpLabel = QLabel("&Option Market Price:")
        self.mpEdit = QLineEdit()
        mpLabel.setBuddy(self.mpEdit)
        
        qLabel = QLabel("&Dividend Yield:")
        self.qEdit = QLineEdit()
        qLabel.setBuddy(self.qEdit)
        
        rLabel = QLabel("&Risk Free Rate:")
        self.rEdit = QLineEdit()
        rLabel.setBuddy(self.rEdit)
        
        layout = QFormLayout()
        layout.addRow(kLabel, self.kEdit)
        layout.addRow(TLabel, self.TEdit)
        layout.addRow(S0Label, self.S0Edit)
        layout.addRow(volLabel, self.volEdit)
        layout.addRow(mpLabel, self.mpEdit)
        layout.addRow(qLabel, self.qEdit)
        layout.addRow(rLabel, self.rEdit)
        
        self.optionsInput.setLayout(layout)
    
    def greeksView(self):
        self.greeksBox = QGroupBox("Option Info")
        self.greeksTable = QTableWidget(11, 4)
        self.greeksTable.setItem(0, 0, QTableWidgetItem('Market Price'))
        self.greeksTable.setItem(1, 0, QTableWidgetItem('Volatility'))
        self.greeksTable.setItem(2, 0, QTableWidgetItem('Years To Expiration'))
        self.greeksTable.setItem(3, 0, QTableWidgetItem('Dividend Yield'))
        self.greeksTable.setItem(4, 0, QTableWidgetItem('Risk Free Rate'))
        self.greeksTable.setItem(5, 0, QTableWidgetItem('Delta'))
        self.greeksTable.setItem(6, 0, QTableWidgetItem('Vega'))
        self.greeksTable.setItem(7, 0, QTableWidgetItem('Theta'))
        self.greeksTable.setItem(8, 0, QTableWidgetItem('Rho'))
        self.greeksTable.setItem(9, 0, QTableWidgetItem('Omega'))
        self.greeksTable.setItem(10, 0, QTableWidgetItem('Gamma'))
        self.greeksTable.setItem(0, 2, QTableWidgetItem('Vanna'))
        self.greeksTable.setItem(1, 2, QTableWidgetItem('Charm'))
        self.greeksTable.setItem(2, 2, QTableWidgetItem('Vomma'))
        self.greeksTable.setItem(3, 2, QTableWidgetItem('Veta'))
        self.greeksTable.setItem(4, 2, QTableWidgetItem('Speed'))
        self.greeksTable.setItem(5, 2, QTableWidgetItem('Zomma'))
        self.greeksTable.setItem(6, 2, QTableWidgetItem('Color'))
        self.greeksTable.setItem(7, 2, QTableWidgetItem('Ultima'))
        self.greeksTable.setItem(8, 2, QTableWidgetItem('Dual Delta'))
        self.greeksTable.setItem(9, 2, QTableWidgetItem('Dual Gamma'))
        

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.greeksTable)
        self.greeksBox.setLayout(layout)
    
    def plotWindow(self):
        self.plotGroupBox = QTabWidget()
        self.plotGroupBox.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Ignored)
        
        self.tab1 = FigureCanvas(Figure(figsize=(4, 8)))
        self.timeEvolutionAx = self.tab1.figure.add_subplot(111)

        tab2 = QWidget()
        textEdit = QTextEdit()

        textEdit.setPlainText("Twinkle, twinkle, little star,\n"
                              "How I wonder what you are.\n"
                              "Up above the world so high,\n"
                              "Like a diamond in the sky.\n"
                              "Twinkle, twinkle, little star,\n"
                              "How I wonder what you are!\n")

        tab2hbox = QHBoxLayout()
        tab2hbox.setContentsMargins(5, 5, 5, 5)
        tab2hbox.addWidget(textEdit)
        tab2.setLayout(tab2hbox)
        
        
        self.plotGroupBox.addTab(self.tab1, "&Time Evolution of Value")
        self.plotGroupBox.addTab(tab2, "&Sweep Results")
        #self.plotGroupBox.addTab(tab3, "&Profit Calculator")
        #self.plotGroupBox.addTab(tab4, "&Delta Hedging")
    
    def optionsDisplay(self):
        self.optionsBox = QGroupBox("Options")
        self.optionsTable = QTableWidget(10, 4)
        self.optionsTable.setItem(0, 0, QTableWidgetItem('Option Type'))
        self.optionsTable.setItem(0, 1, QTableWidgetItem('Strike'))
        self.optionsTable.setItem(0, 2, QTableWidgetItem('Expiration'))
        self.optionsTable.setItem(0, 3, QTableWidgetItem('Underlying Price'))
        #self.optionsTable.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.optionsTable.cellClicked.connect(self.onOptionTableClicked)

        layout = QHBoxLayout()
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(self.optionsTable)
        self.optionsBox.setLayout(layout)
    
    def onOptionTableClicked(self, row, column):
        selected = self.optionsTable.selectedItems()
        fulltime = []
        halftime = []
        expiry = []
        for item in selected:
            if item.row() != 0 and item.row()<=len(self.optionsList):
                opt = self.optionsList[item.row()-1]
                self.greeksTable.setItem(0, 1, QTableWidgetItem(str(opt.marketPrice)))
                self.greeksTable.setItem(1, 1, QTableWidgetItem(str(opt.vol)))
                self.greeksTable.setItem(2, 1, QTableWidgetItem(str(opt.T)))
                self.greeksTable.setItem(3, 1, QTableWidgetItem(str(opt.q)))
                self.greeksTable.setItem(4, 1, QTableWidgetItem(str(opt.r)))
                self.greeksTable.setItem(5, 1, QTableWidgetItem(str(opt.delta(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(6, 1, QTableWidgetItem(str(opt.vega(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(7, 1, QTableWidgetItem(str(opt.theta(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(8, 1, QTableWidgetItem(str(opt.rho(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(9, 1, QTableWidgetItem(str(opt.omega(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(10, 1, QTableWidgetItem(str(opt.gamma(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(0, 3, QTableWidgetItem(str(opt.vanna(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(1, 3, QTableWidgetItem(str(opt.charm(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(2, 3, QTableWidgetItem(str(opt.vomma(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(3, 3, QTableWidgetItem(str(opt.veta(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(4, 3, QTableWidgetItem(str(opt.speed(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(5, 3, QTableWidgetItem(str(opt.zomma(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(6, 3, QTableWidgetItem(str(opt.color(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(7, 3, QTableWidgetItem(str(opt.ultima(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(8, 3, QTableWidgetItem(str(opt.dualDelta(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                self.greeksTable.setItem(9, 3, QTableWidgetItem(str(opt.dualGamma(S0=opt.S0, K=opt.K, vol=opt.vol, r=opt.r, T=opt.T, q=opt.q))))
                
                self.timeEvolutionAx.clear()
                toSweep = {'S0' : (opt.S0*0.8, opt.S0*1.2, 50)}
                toGrab = ('price')
                fulltime.append(opt.sweep(toSweep, toGrab))
                self.timeEvolutionAx.plot(fulltime[0]['S0'], self.sumprice(fulltime), label='Now')
                saveT = opt.T
                opt.T /= 2
                halftime.append(opt.sweep(toSweep, toGrab))
                self.timeEvolutionAx.plot(halftime[0]['S0'], self.sumprice(halftime), label='Half Time')
                opt.T = 1e-6
                expiry.append(opt.sweep(toSweep, toGrab))
                opt.T = saveT
                self.timeEvolutionAx.plot(expiry[0]['S0'], self.sumprice(expiry), label='Expiration')
                self.timeEvolutionAx.set_xlabel('Stock Price')
                self.timeEvolutionAx.set_ylabel('Option Price')
                self.timeEvolutionAx.legend()
                self.tab1.draw()
            
    def sumprice(self, outs):
        for i in range(len(outs)):
            outs[i]['price']=np.array(outs[i]['price'])
            if i == 0:
                if outs[0]['ls'] == 'Long':
                    price=outs[0]['price']
                elif outs[0]['ls'] == 'Short':
                    price= -outs[0]['price']
            else:
                if outs[i]['ls'] == 'Long':
                    price+=outs[i]['price']
                elif outs[i]['ls'] == 'Short':
                    price-=outs[i]['price']
        print(price)
        return price
    
    def sweepInput(self):
        self.sweepBox = QGroupBox("Sweep Variables")
        
        toSweepLabel = QLabel("Inputs to Sweep")
        minLabel = QLabel("Min")
        maxLabel = QLabel("Max")
        stepsLabel = QLabel("Steps")
        inputSelect1 = QComboBox()
        inputSelect2 = QComboBox()
        min1 = QLineEdit()
        min2 = QLineEdit()
        max1 = QLineEdit()
        max2 = QLineEdit()
        steps1 = QLineEdit()
        steps2 = QLineEdit()

        self.inputBox = QGridLayout()
        self.inputBox.addWidget(toSweepLabel, 0, 0, 1, 1)
        self.inputBox.addWidget(minLabel, 0, 1, 1, 2)
        self.inputBox.addWidget(maxLabel, 0, 2, 1, 3)
        self.inputBox.addWidget(stepsLabel, 0, 3, 1, 4)
        self.inputBox.addWidget(inputSelect1, 1, 0, 2, 1)
        self.inputBox.addWidget(inputSelect2, 2, 0, 3, 1)
        self.inputBox.addWidget(min1, 1, 1, 2, 2)
        self.inputBox.addWidget(min2, 2, 1, 3, 2)
        self.inputBox.addWidget(max1, 1, 2, 2, 3)
        self.inputBox.addWidget(max2, 2, 2, 3, 3)
        self.inputBox.addWidget(steps1, 1, 3, 2, 4)
        self.inputBox.addWidget(steps2, 2, 3, 3, 4)
        
    def sweepOutput(self):
        self.outputSelectList = QListWidget()
        
        for i, out in enumerate(self.outputs):
            self.outputSelectList.insertItem(i, out)

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    gallery = BlackScholesUI()
    gallery.show()
    sys.exit(app.exec_())