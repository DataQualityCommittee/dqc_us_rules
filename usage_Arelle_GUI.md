# Using DQC Rules with Arelle - from the GUI 
[return to README](README.md#using)

## Initial setup for the DQC Rules xule plugin

* Open the Arelle program.
* Choose the "Help" menu and select "Manage plug-ins" to verify the "DQC Rules Validator" is listed.
* ***If DQC Rules Validator is not listed:***
    * Use the "Select" button to bring up teh "Select Plug-in Module" dialog. 
    * Select the the "DQC.py" file (under "Validate"). Next to the file, the name will appear as "DQC Rules Validator". Click on "Ok". 
    * The "Select Plug-in Module" will close. On the "Plug-in Manager" dialog click on "Close".
	* When the dialogue box appears requesting a program restart, choose "Yes".
* Choose the "Tools" menu and "Validation" and confirm there is a check mark for "DQC Rules". If not, select this item from the menu.

## Checking a filing with DQC Rules

* Choose the "File" menu and either "Open file" or "Open Web" to select an XBRL .zip file from local computer or SEC EDGAR system.
* Select the .xml file (instance document) from the view of the contents of the .zip.
* After the instance has rendered in Arelle, choose the "Tools" >> "Validation" menu and select "Validate".
* Monitor the "messages" window at the bottom of Arelle, to see _[DQC] Starting DQC validation - xxx.xml_ appears.
* After the message _[DQC] Finished DQC validation - xxx.xml_ appears, review any error messages. The results can be saved by selecting the messages window (right-click on a Windows PC) and choosing "Save to file".

See also [from a command prompt](usage_command_prompt.md) for advanced configuration options. 

### [return to README](README.md#using)
 
© Copyright 2015 - 2019 XBRL US, Inc. All rights reserved.   
See [License](https://xbrl.us/dqc-license) for license information.  
See [Patent Notice](https://xbrl.us/dqc-patent) for patent infringement notice.
