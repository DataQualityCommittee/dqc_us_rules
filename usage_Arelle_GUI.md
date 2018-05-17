# Using DQC Rules with Arelle - from the GUI [return to README](README.md#using)

## Initial setup for the DQC Rules xule plugin

* Open the Arelle program.
* Choose the "Help" menu and select "Manage plug-ins" to verify the DQC XBRL rule processor (xule) is listed.
* ***If DQC XBRL rule processor (xule) is not listed:***
	* Use the "Browse" button to locate the xule plugin folder in Arelle's install directory, which is located on a path similar to C:\Program FIles\Arelle\plugin; on a Mac, the location would be at /Applications/Arelle.app/Contents/MacOS/plugin. 
	* **Choose the __init__.py file** and verify the DQC XBRL rule processor (xule) is listed in the Plug-in Manager, then click "Close". 
	* When the dialogue box appears requesting a program restart, choose "Yes".
* Choose the "Tools" menu and "Validate" to confirm there is a check mark for "DQC Rules". If not, select this item from the menu and confirm the selection is now checked.
* Choose the "Tools" menu and "DQC" >> "Version..." to confirm 3.0.22485 or higher appears.

## Checking a filing with DQC Rules

* Choose the "File" menu and either "Open file" or "Open Web" to select an XBRL .zip file from local computer or SEC EDGAR system.
* Select the .xml file (instance document) from the view of the contents of the .zip.
* After the instance has rendered in Arelle, choose the "Tools" >> "Validation" menu and select "Validate".
* Monitor the "messages" window at the bottom of Arelle, to see _[DQC] Starting DQC validation - xxx.xml_ appears.
* After the message _[DQC] Finished DQC validation - xxx.xml_ appears, review any error messages. The results can be saved by selecting the messages window (right-click on a Windows PC) and choosing "Save to file".

See also [from a command prompt](usage_command_prompt.md) for advanced configuration options. 

### [return to README](README.md#using)
 
© Copyright 2015 - 2018 XBRL US, Inc. All rights reserved.   
See [License](https://xbrl.us/dqc-license) for license information.  
See [Patent Notice](https://xbrl.us/dqc-patent) for patent infringement notice.
