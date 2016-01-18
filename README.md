KBoot GUI
===========

The Graphical User Interface for Kinetis Bootloader based on [pyKBoot](https://github.com/molejar/pyKBoot) and [wxPython](https://github.com/wxWidgets/wxPython). It's multiplatform (Windows, Linux and OSX are supported).

<p align="center">
  <img src="https://github.com/molejar/KBootGUI/blob/master/doc/kboot-gui.png?raw=true" alt="KBoot GUI: Main window"/>
</p>

Installation
------------

Clone the project into your local directory

``` bash
    $ git clone https://github.com/molejar/KBootGUI.git
```
Install dependencies:
- [pyKBoot](https://github.com/molejar/pyKBoot)
- [wxPython](https://github.com/wxWidgets/wxPython) (Windows users can use following installers: [wxPython3.0-win32-py27](http://downloads.sourceforge.net/wxpython/wxPython3.0-win32-3.0.2.0-py27.exe) or [wxPython3.0-win64-py27](http://downloads.sourceforge.net/wxpython/wxPython3.0-win64-3.0.2.0-py27.exe))

Usage
-----

Go into `KBootGUI` directory and execute `python kboot-gui.py` in terminal or just `kboot-gui.py` in windows commander. 

Create One Executable File
--------------------------

KBoot GUI is written in Python language, what means that you need have installed Python interpreter on your computer. This condition can be restrictive for somebody and therefore exist option how to build KBoot GUI into one executable file. All what you need is to run following commands in terminal:

``` bash
    $ pip install pyinstaller
    $ cd KBootGUI
    $ python pyinstaller -F -w kboot-gui.py
```
If the build was successful, then in `./dist` folder will locate the executable file of `kboot-gui.py`

TODO
----

- Add support for UART interface
- Add KBOOT configuration area parser and editor
- Add USB hotplug detection

