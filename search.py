
# TODO:
# Update the get methods below to be portable.

'''Search module used to search for a given piece of text within folders and 
files. Performs a contains and does not search for whole words. scandir.walk() 
is used to recursively search faster than os.walk(). scandir is a third party 
module.'''

import os, scandir, mimetypes
from itertools import islice
from os.path import expanduser

def searchRecursively(searchPattern, rootFolder, caseSensitive=False, searchDirs=True, searchFiles=True, searchFileContent=True):
	
	dirResults   = []
	fileResults  = []
	accessDenied = []
	
	# Return empty file and dir lists if there is no desired search.
	if not searchDirs and not searchFiles:
		return (dirResults, fileResults, accessDenied)
	if str(type(searchPattern)) != "<class 'str'>":
		return (dirResults, fileResults, accessDenied)
	
	if not caseSensitive:
		searchPattern = searchPattern.lower()
	
	# Search through dirs and files: scandir.walk is recursive.
	for root, dirs, files in scandir.walk(rootFolder):
		if searchFiles:
			for f in files:
				filePath = root + os.sep + f
				
				if not caseSensitive:
					f = f.lower()
				
				if searchPattern in f:
					fileResults.append(filePath)
						
				# If filename doesn't match then search the file content.
				elif searchFileContent:
					try:
						if searchFile(searchPattern, filePath, caseSensitive):
							fileResults.append(filePath)
					except PermissionError:
						accessDenied.append(filePath)
				
		if searchDirs:	
			for d in dirs:
				dirPath = root + os.sep + d
				
				if not caseSensitive:
					d = d.lower()
				
				if searchPattern in d:
					dirResults.append(dirPath)
	
	return (dirResults, fileResults, accessDenied)

def searchFile(searchPattern, filePath, caseSensitive=True):
	# Ensure searchPattern is a text string.
	if str(type(searchPattern)) != "<class 'str'>":
		return False
	
	# If file is binary then don't search it. Improves speed.
	t = mimetypes.guess_type(filePath, strict=False)
	if not str(t[0]).startswith("text"):
		return False
		
	if not caseSensitive:
		searchPattern = searchPattern.lower()
	searchPattern = str.encode(searchPattern) # Convert to bytes for a faster search.
	
	# n lines must be large enough for speed but small enough for memory usage.
	n = 250
	
	# The file is opened in read binary mode to avoid decode errors and improve speed.
	with open(filePath, mode="rb") as f:
		while True:
			lines = list(islice(f, n))
			if not lines:
				return False
			for x in lines:
				if not caseSensitive:
					x = x.lower()
				if searchPattern in x:
					return True
	
def searchApplications(searchPattern):
	results = []
	if str(type(searchPattern)) != "<class 'str'>":
		return results
	
	# App searches are always case insensitive.
	searchPattern = searchPattern.lower()
	path = getAppDirPath()
	ext = getAppExt()
	
	for root, dirs, files in scandir.walk(path):
		for f in files:
			filePath = root + os.sep + f
			f = f.lower()
			
			if searchPattern in f and f.endswith(ext):
				results.append(filePath)
		
	return results
	
def getRootDirPath():
	root = "C:\\"
	return root
	
def getHomeDirPath():
	home = expanduser("~")
	return home
	
def getAppDirPath():
	path = r"C:\Program Files (x86)"
	return path
	
def getAppExt():
	# Should always return lower case and contain a '.' before the ext.
	ext = ".exe"
	if not ext.startswith("."):
		raise IOError("Extension must have a '.' e.g. '.exe'")
	return ext.lower()
