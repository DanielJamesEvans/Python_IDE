WARNING: This software was primarily written for Mac computers.  While it should run on 
Windows and Linux computers, a Mac is needed to access all of the software’s features.

This is a simple IDE for the Python programming language.  It is written in Python; the
GUI was written using TkInter.  It is licensed under the MIT license; read LICENSE.txt for
more information.

Installation: To run the IDE, it is necessary to have Python (and its standard libraries)
installed on your computer.  However, it is not necessary to install additional libraries.

Use: There are two ways to use this software.

     WAY 1 (for all computers): To begin using this IDE, run ide.py like a normal Python 
                                file.  Note that some features (ex. using the Mac OS
                                “Open With” feature) are not available when directly 
                                running ide.py.  To access these features, see “WAY 2”
                                below.

     WAY 2 (Mac only): In order to access all of the features of the software, use
                       py2app to create a Mac app.
                       STEP 1: In the directory containing the code, run the following command in Terminal:
                       py2applet --make-setup ide.py -includes syntax_highlighter.py preferences.ini --argv-emulation
                       STEP 2: In the directory containing the code, run the following command in Terminal:
                       python setup.py py2app -A
                       STEP 3: Find the app in the dist directory in the directory where the source code is.