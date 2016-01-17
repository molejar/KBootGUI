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
- [wxPython](https://github.com/wxWidgets/wxPython) - In Windows use following instalers: [wxPython3.0-win32-py27](http://downloads.sourceforge.net/wxpython/wxPython3.0-win32-3.0.2.0-py27.exe), [wxPython3.0-win64-py27](http://downloads.sourceforge.net/wxpython/wxPython3.0-win64-3.0.2.0-py27.exe)

Usage
-----

Go into `KBootGUI` directory and execute `kboot-gui.py`. 

TODO
----

- Add UART interface support
- Add KBOOT configuration area parser and editor
- Add USB hotplug detection
