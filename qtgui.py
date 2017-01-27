
'''GUI class using PyQt5. Provides a graphical interface for users to search 
with. Benefits offered by the GUI is an intuitive means of searching and a means 
of interacting with each result by clicking it. Application results are launched 
while file and directory results are opened in Windows Explorer.'''

import search, time, sys, os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui
from enum import Enum
from threading import *

class ResultType(Enum):
    App   = 1
    Dir   = 2
    File  = 3
    Other = 4

class ResultLabel(QLabel):
	def __init__(self, text, resultType, parent=None):
		super(ResultLabel, self).__init__(parent)
		self.text = text
		self.resultType = resultType
		self.setText(text)
		self.setWordWrap(False)
		
	def mouseReleaseEvent(self, event):
		try:
			path = self.text
			if self.resultType == ResultType.App:
				cmd = self.quotify(path)
				ct = CommandThread(cmd)
				ct.start()
			elif self.resultType == ResultType.Dir:
				cmd = r"Explorer /open,%s" % (self.quotify(path))
				os.system(cmd)
			elif self.resultType == ResultType.File:
				cmd = r"Explorer /select,%s" % (self.quotify(path))
				os.system(cmd)
			elif self.resultType == ResultType.Other:
				pass # No action required.
		except Exception as ex:
			QMessageBox.information(self, "Error", ex)
		
	# It is necessary to quotify a windows command path when it has spaces.
	def quotify(self, command):
		return '"' + command + '"'
			
class SearchBox(QLineEdit):
	def __init__(self, button, parent=None):
		super(SearchBox, self).__init__(parent)
		self.button = button
	
	def keyReleaseEvent(self, event):
		if event.key() == Qt.Key_Escape:
			self.clear()

class Form(QMainWindow):
	def __init__(self, parent=None):
		super(Form, self).__init__(parent)
		self.progressThread = ProgressThread(None, None, None)
        
        #************** Search Params ***************
		self.rootFolder			= search.getHomeDirPath()
		self.caseSensitive		= False
		self.searchDirs			= True
		self.searchFiles		= True
		self.searchFileContent	= False
		self.searchApps			= True
		self.removeDuplicates	= True
		#********************************************
        
		self.name 			= "Spotlamp"
		self.guiWidth   	= 300
		self.guiHeight  	= 42
		self.searchHeight	= 70
		self.resultsWidth	= 700
		self.resultsHeight	= 500
		self.emptyHeight	= 125
        
		self.scrollArea 	= QScrollArea()	
		self.searchButton 	= QPushButton("&Search")
		self.searchField  	= SearchBox(self.searchButton)
		self.progressBar  	= QProgressBar(self)

		baseWidget 			= QWidget(self.scrollArea)
		baseLayout 			= QGridLayout()
		searchLayout 		= QHBoxLayout()
		progressBarLayout 	= QHBoxLayout()
		self.resultsLayout 	= QVBoxLayout()
		
		self.setWindowTitle(self.name)
		self.searchButton.clicked.connect(self.searchClicked) # Search button event handler link.
		
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		
		searchLayout.addWidget(self.searchField)
		searchLayout.addWidget(self.searchButton)
		
		progressBarLayout.addWidget(self.progressBar)
		self.progressBar.hide()
		
		baseWidget.setLayout(baseLayout)
		self.scrollArea.setWidget(baseWidget)
		self.setCentralWidget(self.scrollArea);
		
		baseLayout.addLayout(searchLayout, 0, 0)
		baseLayout.addLayout(progressBarLayout, 1, 0)
		baseLayout.addLayout(self.resultsLayout, 2, 0)
		
		baseLayout.setAlignment(Qt.AlignTop)
		baseLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
		
	def show(self):
		super(Form, self).show()
		self.setMinimumSize(self.guiWidth, self.guiHeight)
		self.resize(self.guiWidth, self.guiHeight)
		self.searchField.setFocus()
		
	def addResult(self, text, resultType):
		r = ResultLabel(text, resultType)
		self.resultsLayout.addWidget(r)
		
	def clearResults(self):
		for i in reversed(range(self.resultsLayout.count())): 
			self.resultsLayout.itemAt(i).widget().deleteLater()
		
	def addLabel(self, text):
		self.addResult("", ResultType.Other) # Line break.
		self.addResult(text, ResultType.Other)
		
	def addSummaryLabel(self):
		summaryLabel = ResultLabel("", ResultType.Other)
		self.resultsLayout.addWidget(summaryLabel)
		return summaryLabel
			
	def showProgressBar(self):
		if self.progressBar.isVisible():
			return
		self.progressBar.show()
		if self.height() < self.searchHeight:
			self.resize(self.width(), self.searchHeight)
		
	def setProgressValue(self, value, delay=False, duration=10):
		self.progressThread.stop()
		if self.progressThread.isAlive():
			self.progressThread.join()
		if not delay:
			self.progressBar.setValue(value)
		else:
			self.progressThread = ProgressThread(self.progressBar, value, duration)
			self.progressThread.start()
			
	def getSearchDuration(self):
		total = 0
		if self.searchDirs:
			total += 1
		if self.searchFiles:
			total += 1
		if self.searchFileContent:
			total += 2
		
		if self.rootFolder == search.getRootDirPath():
			return total * 16
		elif self.rootFolder == search.getHomeDirPath():
			return total * 3.5
		else: # Custom (user chosen) root directory.
			return total * 14

	def searchClicked(self):
		searchText = self.searchField.text() # Deliberately not trimmed (stripped).
		
		if searchText.strip() == "":
			QMessageBox.information(self, self.name, "You've not entered any text to search with.")
			return
		if not self.searchDirs and not self.searchFiles and not self.searchApps:
			QMessageBox.information(self, self.name, "You've not chosen anything to search through, check the search preferences.")
			return
		if self.rootFolder == search.getRootDirPath() and self.searchFileContent:
			QMessageBox.information(self, self.name, "You've chosen to search through every file (root directory) and its content, this may take some time. Please be patient.")

		self.showProgressBar()
		self.setProgressValue(0)
		self.setProgressValue(30, True, 3)

		# Start the search and time it.
		start = time.time()
		apps = []
		if self.searchApps:
			apps = search.searchApplications(searchText)
			
		self.setProgressValue(85, True, self.getSearchDuration())
				
		results = search.searchRecursively(searchText, self.rootFolder, self.caseSensitive, self.searchDirs, self.searchFiles, self.searchFileContent)
		end = time.time()
		length = end - start
		
		self.setProgressValue(100, True, 0.1)
	
		dirs   = results[0]
		files  = results[1]
		denied = results[2]
		
		# Remove apps from the file results (duplicates).
		if self.removeDuplicates:
			for x in apps:
				if x in files:
					files.remove(x)
					
		self.clearResults()
		summary = self.addSummaryLabel()
		
		# Calculate if the searchText is a math expression.
		try:
			ans = eval(searchText)
			# Prevent a single number from being printed as a sum result e.g. 45 = 45.
			if str(ans) != searchText:
				self.addLabel("%s = %d" % (searchText, ans))
		except:
			pass
		
		# Update the GUI with the results.
		numResults = len(apps) + len(files) + len(dirs)
		if numResults is 0:
			h = self.emptyHeight
			w = self.width()
			summary.setText("0 results (%f seconds)" % (length))
		else:
			h = self.resultsHeight
			w = self.resultsWidth
			summary.setText("%d result(s) (%f seconds)" % (numResults, length))
			if len(apps) is not 0:
				self.addLabel("Applications:")
				for x in apps:
					self.addResult(str(x), ResultType.App)
			if len(dirs) is not 0:
				self.addLabel("Directory result(s):")
				for x in dirs:
					self.addResult(str(x), ResultType.Dir)
			if len(files) is not 0:
				self.addLabel("File result(s):")
				for x in files:
					self.addResult(str(x), ResultType.File)
			if len(denied) is not 0:
				self.addLabel("File access denied (try running as administrator):")
				for x in denied:
					self.addResult(str(x), ResultType.Other)
		
		# Resize the GUI if necessary.
		if self.height() < h:
			self.resize(self.width(), h)
		if self.width() < w:
			self.resize(w, self.height())
		self.setProgressValue(100)
				
class ProgressThread(Thread):
	def __init__(self, progressBar, value, duration):
		Thread.__init__(self)
		self.daemon = True
		self.progressBar = progressBar
		self.value = value
		self.duration = duration
		self.kill = False

	def run(self):
		progress = self.progressBar.value()
		diff = self.value - progress
		self.duration = self.duration / diff
		
		while progress < self.value and not self.kill:
			progress += 1
			self.progressBar.setValue(progress)
			time.sleep(self.duration)
			
		self.progressBar.setValue(self.value)
			
	def stop(self):
		if self.isAlive():
			self.kill = True
			
class CommandThread(Thread):
	def __init__(self, command):
		Thread.__init__(self)
		self.daemon = False
		self.command = command

	def run(self):
		os.system(self.command)
            
# Start of execution, inits GUI and displays it.
if __name__ == '__main__':
	app = QApplication(sys.argv)
	app.setStyle("fusion")
	screen = Form()
	screen.show()
	sys.exit(app.exec_())
