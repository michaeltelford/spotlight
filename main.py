
'''Search script which offers a command line alternative to the GUI search 
capability. Receives the user arguments and uses them to search the system.'''

import search, time, sys

def main():
	
	# Init default search params.
	searchText 			= ""
	rootFolder 			= search.getRootDirPath()
	caseSensitive 		= False
	searchDirs 			= True
	searchFiles 		= True
	searchFileContent 	= True
	searchApps 			= True
	removeDuplicates	= True
	
	paramLen = len(sys.argv)
	if paramLen < 2:
		print("\nMust include at least one argument containing search text")
		sys.exit(0)
	
	# Set user search params.
	# sys.argv[0] is the script name.
	for x in range(paramLen):
		if x is 1:
			searchText = str(sys.argv[x])
		elif x is 2:
			param = str(sys.argv[x])
			if param == "home":
				rootFolder = search.getHomeDirPath()
			elif param == "root":
				rootFolder = search.getRootDirPath()
			else:
				rootFolder = param
		elif x is 3:
			caseSensitive = getBool(sys.argv[x])
		elif x is 4:
			searchDirs = getBool(sys.argv[x])
		elif x is 5:
			searchFiles = getBool(sys.argv[x])
		elif x is 6:
			searchFileContent = getBool(sys.argv[x])
		elif x is 7:
			searchApps = getBool(sys.argv[x])
		elif x is 8:
			removeDuplicates = getBool(sys.argv[x])
			
	# Ensure there is something to search for.
	if not searchDirs and not searchFiles and not searchApps:
		print("\nMust have something to search through e.g. files, folders")
		sys.exit(0)
	
	# Calculate if the searchText is a math expression.
	try:
		ans = eval(searchText)
		print("\nResult:", ans)
		# Continue with search using expression.
	except:
		pass
	
	# Perform the search and time it.
	print("Searching...")
	start = time.time()
	if searchApps: # Display app results first to save time.
		apps = search.searchApplications(searchText)
		if len(apps) is not 0:
			print("\nApplication result(s):")
			for x in apps:
				print(x)
	else:
		apps = []

	results = search.searchRecursively(searchText, rootFolder, caseSensitive, searchDirs, searchFiles, searchFileContent)
	end = time.time()
	length = end - start

	dirs   = results[0]
	files  = results[1]
	denied = results[2]
	
	# Remove apps from the file results (duplicates).
	if removeDuplicates:
		for x in apps:
			if x in files:
				files.remove(x)
	
	# Update the CLI with the results.
	numResults = len(apps) + len(files) + len(dirs)
	if numResults is 0:
		print("\nThere are no search results (%f seconds)" % (length))
	else:
		if len(dirs) is not 0:
			print("\nDirectory result(s):")
			for x in dirs:
				print(x)
		if len(files) is not 0:
			print("\nFile result(s):")
			for x in files:
				print(x)
		if len(denied) is not 0:
			print("\nFile access denied:")
			for x in denied:
				print(x)
		print("\nThere is/are %d result(s) (%f seconds)" % (numResults, length))
		
def getBool(boolStr):
	if boolStr.lower() == "true":
		return True
	elif boolStr.lower() == "false":
		return False
	else:
		raise IOError("Must be true or false")
		
# Start execution.
if __name__ == "__main__":
	main()
