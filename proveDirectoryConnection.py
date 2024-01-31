# This script can be used to prove accessible featureclass content from a directory structure from ArcGIS Server
# The script can be run from the Python included with ArcGIS Server
# Note that directories and files that are not visible to the executing user will not show update
# The executing user should be the ArcGIS Server service account
# And, the list of featureclasses should be checked against a list of expected featureclasses
# A top-level share or directory that is not accessible to the user will simply return no featureclasses or directories
# Usage Example: "C:\Program Files\ArcGIS\Server\framework\runtime\ArcGIS\bin\Python\Scripts\propy.bat" c:\path\proveDirectoryConnection.py "c:\temp"

import arcpy
from arcpy import env
from pathlib import Path
import argparse
import logging
import sys 
import os

def main(argv=None):

	logging.basicConfig(filename="proveDirectoryConnection.log",encoding="utf-8",level=logging.INFO, format="%(asctime)s %(levelname)-8s %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
	logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
	
	parser = argparse.ArgumentParser()
	parser.add_argument('targetDirectory', help=('A directory to analyze as the current user'))
	args = parser.parse_args()
	location = args.targetDirectory

	
	currentUser = os.getlogin()
	domain = os.environ['userdomain']
	
	#location = r"\\esri.com\toybox\public\dkrouk" 
	
	logging.info("START OF EXPLORATION\n")
	logging.info("Location: " + location + " Traversed by Domain: " + domain + " User: " + currentUser + "\n")
	
	allFeatureClasses = []
	unReadableDirectories = []
	unWritableDirectories = []
	unExecutableDirectories = []
	totalFeatureClasses = 0
	totalDirectories = 0
	for root, dirs, files in os.walk(location):
		# only process directories
		for dirname in dirs:
			targetDirName = os.path.join(root,dirname)
			logging.info("Examining: " + targetDirName)
			totalDirectories = totalDirectories + 1
			if hasRead(targetDirName) == False:
				unReadableDirectories.append(targetDirName)
			else:
				featureclasses = reportEsriContent(targetDirName)
				for fc in featureclasses:
					allFeatureClasses.append(os.path.join(targetDirName,fc))			

			if hasWrite(targetDirName) == False:
				unWritableDirectories.append(targetDirName)				
			if hasExecute(targetDirName) == False:
				unExecutableDirectories.append(targetDirName)				
	
	logging.info("\n")
	logging.info("CONTENT SUMMARY\n")
	
	logging.info("Total directories examined: " + str(totalDirectories) + "\n")
	if (totalDirectories == 0):
		logging.warning("*No directories were examined*.  Please check file and/or share permissions.\n")
	logging.info("Directory permissions limits (on write and execute; unreadable directories are not detectable): \n")

	for unreadable in unReadableDirectories:
		logging.warning ("Unreadable directory: " + unreadable + "\n") # we would not be aware of a directory we cannot read.  So, this should never occur.
	for unwritable in unWritableDirectories:
		logging.info ("Unwritable directory: " + unwritable + "\n")
	for unexecutable in unExecutableDirectories:
		logging.info ("Unexecutable directory: " + unexecutable + "\n")
	
	logging.info("Featureclasses found: " + str(len(allFeatureClasses)) + " \n")
	if (len(allFeatureClasses) == 0):
		logging.warning("*No featureclasses were found*.  Please check file and/or share permissions.\n")
	for fc in allFeatureClasses:
		logging.info(fc)
	#reportDirectoryPrivileges(location)
	#totalFeatureClasses = reportEsriContent(location)
	
	#if (totalFeatureClasses > 0):
	#	totalWorkspaces = 1
	#else:
	#	totalWorkspaces = 0

	#contents = [ f for f in os.listdir(location) if os.path.isfile(f) == False]
	#logging.info("\n")
	#logging.info(" Directories in location: " + str(len(contents)) + "\n")
	
	#cumulativeDirectories = 0
	#for c in contents:
	#	cumulativeDirectories = cumulativeDirectories + 1

	#	target_c = os.path.join(location,c)
	#	logging.info(str(cumulativeDirectories) +  ": Directory target: " + target_c)
		
	#	reportDirectoryPrivileges(target_c)
	#	featureclassCount = 0		
	#	featureclassCount = reportEsriContent(target_c)
		
	#	totalFeatureClasses = totalFeatureClasses + featureclassCount
	#	if (featureclassCount > 0):
	#		totalWorkspaces = totalWorkspaces + 1
			
	#logging.info ("Total workspaces: " + str(totalWorkspaces) + " in location " + location)
	#logging.info ("Total featureclasses: " + str(totalFeatureClasses) + " in location " + location)
	
	logging.info("\n")
	logging.info("EXECUTION COMPLETE")
	

def reportEsriContent(location):
	try:
		i = 0
		
		desc = arcpy.Describe(location)
		if hasattr(desc, "catalogPath"):
			logging.debug (" - Catalog Path: " + desc.catalogPath)
		if hasattr(desc, "dataElementType"):
			logging.debug (" - Data Element Type: "  + desc.dataElementType)		
		
		arcpy.env.workspace = location
		featureclasses = arcpy.ListFeatureClasses()	
		i = 0
		for fc in featureclasses:
			logging.debug(fc)
			i = i + 1
		logging.debug(str(i) + " featureclasses found")
		return featureclasses
		#for fc in featureclasses:
		#	i = i + 1
			
		#logging.info (" - " + str(i) + " featureclasses found in workspace " + location + "\n")
		
		#return i # number of featureclasses (!= 0 means it is a workspace)
		
	except:
		logging.info("WARNING: Unable to understand target directory: " + location + "\n")

def hasRead(location):
	permissions = os.stat(location).st_mode
	if (permissions & 0o400):
		return True
	else:
		return False

def hasWrite(location):
	permissions = os.stat(location).st_mode
	if (permissions & 0o200):
		return True
	else:
		return False

def hasExecute(location):
	permissions = os.stat(location).st_mode
	if (permissions & 0o100):
		return True
	else:
		return False



def reportDirectoryPrivileges(location):
	permissions = os.stat(location).st_mode
	if (permissions & 0o400):
		logging.info(" Directory read confirmed")
	else:
		logging.info(" WARNING: No directory read permission")
	if (permissions & 0o200):
		logging.info(" Directory write confirmed")
	if (permissions & 0o100):
		logging.info(" Directory execute confirmed")

if __name__ == "__main__":
	sys.exit(main(sys.argv))