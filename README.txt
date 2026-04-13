Running InstaSentry

1. Download all InstaSentry files to your system, preferably in a single file.
2. Search: "chrome://extensions/" and make sure developer mode is toggled on.
3. Press "Load unpacked" and choose the file containing ALL InstaSentry files.

4. In VS Code, open the main.py file and start a new terminal (ctrl + ~).
5. For first time installation, copy/paste into the terminal to install the following dependencies:
	* pip install selenium
	* pip install flask
	* pip install flask flask-cors
	* pip install pywin32

5. Then, run: "python app.py" in the terminal. This will start the required local server used for communication between Py and Java.
6. Set up is complete.
7. Navigate back to the Google Chrome Extension page and run the extension.

Anytime you run this extension, repeat steps 5 and 7. Kill the server session in the terminal if needed (ctrl + c) and start a fresh one.

Note: The final product will be much easier and user friendly. This is for testing purposes.