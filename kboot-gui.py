#!/usr/bin/env python

# Copyright 2015 Martin Olejar
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import os
import sys
import time
import struct
import logging
import threading

import wx
import wx.propgrid as pg
import wx.dataview as dw

from gui import AppMain
from kboot import KBoot, Property, Status, SRecFile

try:
    from intelhex import IntelHex
except ImportError:
    pass

mylogger = logging.getLogger()


# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""
    def __init__(self, **data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


# Thread class that executes processing
class WorkerThread(threading.Thread):
    """Worker Thread Class."""
    def __init__(self, *args, **kwargs):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self._notify_window = args[0]
        self._want_abort = 0
        self._cmd_type = args[1]
        self._func = args[2]
        self._args = kwargs

    def run(self):
        """Run Worker Thread."""
        if self._cmd_type == 'read':
            status, data = self._func(self._args['saddr'], self._args['len'])
            wx.PostEvent(self._notify_window, ResultEvent(cmd=self._cmd_type, status=status, data=data))
        else:
            status = self._func(self._args['saddr'], self._args['data'])
            wx.PostEvent(self._notify_window, ResultEvent(cmd=self._cmd_type, status=status))

    def abort(self):
        """abort worker thread."""
        self._want_abort = 1


class WxTextCtrlHandler(logging.Handler):
    def __init__(self, ctrl):
        logging.Handler.__init__(self)
        self.ctrl = ctrl

    def emit(self, record):
        s = self.format(record) + '\n'
        wx.CallAfter(self.ctrl.WriteText, s)


class Timer:
    def __init__(self):
        self.__start = 0
        self.__interval_ms = int(0)
        self.__is_runing = False

    def start(self):
        self.__start = time.time()
        self.__is_runing = True

    def stop(self):
        self.interval = time.time() - self.__start
        self.__interval_ms = int(round(self.interval * 1000))
        self.__is_runing = False

    def is_runing(self):
        return self.__is_runing

    def get_interval_ms(self):
        return self.__interval_ms

    def get_interval_str(self):
        ms = (self.__interval_ms % 1000)
        s  = (self.__interval_ms / 1000) % 60
        m  = (self.__interval_ms / (1000 * 60)) % 60
        return "{0:02d}:{1:02d}.{2:03d}".format(m, s, ms)


class KBootAppMain(AppMain):
    FlashStartAddress = 0
    FlashSize = 0
    Offset = 0

    def __init__(self, parent):
        AppMain.__init__(self, parent)
        #self.SetIcon(wx.Icon('mcu.png', wx.PNG_TYPE_COLOUR, 16, 16))
        handler = WxTextCtrlHandler(self.m_tcLogger)
        mylogger.addHandler(handler)
        FORMAT = "[%(asctime)s %(levelname)-5s]  %(message)s"
        handler.setFormatter(logging.Formatter(FORMAT, datefmt='%M:%S'))
        mylogger.setLevel(logging.DEBUG)
        # -------
        self.m_pg_min_update_wait = 50
        self.m_pg_last_update_time = None
        self.start_addr = 0
        self.data_buffer = []
        self.operation = None
        self.worker = None
        # -------
        self.timer = Timer()
        self.kboot = KBoot()
        self.scan_for_dev()
        # -------
        self.m_dvlcMcuInfo.AppendTextColumn('Parameter', width=150, flags=dw.DATAVIEW_COL_SORTABLE)
        self.m_dvlcMcuInfo.AppendTextColumn('Value', width=350)
        # -------
        self.m_dvlcDataBuff.AppendTextColumn("Address", width=95, align=wx.ALIGN_CENTER, flags=16)
        for i in range(16):
            #self.m_dvlcDataBuff.AppendTextColumn("{:01X}".format(i), width=26, align=wx.ALIGN_CENTER,
            #                                     mode=dw.DATAVIEW_CELL_EDITABLE, flags=16)
            self.m_dvlcDataBuff.AppendTextColumn("{:01X}".format(i), width=26, align=wx.ALIGN_CENTER, flags=16)
        self.m_dvlcDataBuff.AppendTextColumn("0123456789ABCDEF", width=140, align=wx.ALIGN_CENTER)
        # -------
        self.m_pErase = self.m_pGridOptions.Append( pg.PropertyCategory( u"Erase CMD", u"EraseCMD" ) )
        self.m_pEDef = self.m_pGridOptions.Append( pg.EnumProperty( u"Mode", u"Mode",
                                                                    ['Mass Erase', 'Sector Erase'], [0, 1], 0 ) )
        self.m_pESSector = self.m_pGridOptions.Append( pg.UIntProperty( u"Start Sector", u"StartSector" ) )
        self.m_pEESector = self.m_pGridOptions.Append( pg.UIntProperty( u"End Sector", u"EndSector" ) )
        self.m_pWrite = self.m_pGridOptions.Append( pg.PropertyCategory( u"Write CMD", u"WriteCMD" ) )
        self.m_pWOffset = self.m_pGridOptions.Append( pg.StringProperty( u"Offset", u"WROffset", "0x0" ) )
        self.m_pWErase = self.m_pGridOptions.Append( pg.EnumProperty( u"Erase Befor Write ?", u"EraseBeforWrite",
                                                                      ['Yes (Mass Erase)', 'Yes (Sector Erase)', 'No'],
                                                                      [0, 1, 2], 0 ) )
        self.m_pRead = self.m_pGridOptions.Append( pg.PropertyCategory( u"Read CMD", u"ReadCMD" ) )
        self.m_pRSAddr = self.m_pGridOptions.Append( pg.StringProperty( u"Start Address", u"RDStartAddress" ) )
        self.m_pRLen = self.m_pGridOptions.Append( pg.StringProperty( u"Length", u"RDLength" ) )
        # -------
        self.m_dvlcDataBuff.SetForegroundColour( wx.Colour( 10, 145, 40 ) )
        self.m_dvlcDataBuff.SetBackgroundColour( wx.Colour( 32, 32, 32 ) )
        self.m_tcLogger.SetForegroundColour( wx.Colour( 10, 185, 80 ) )
        self.m_tcLogger.SetBackgroundColour( wx.Colour( 32, 32, 32 ) )
        # -------
        if os.name == "posix":
            self.m_dvlcDataBuff.SetFont( wx.Font( 10, 70, 90, 90, False, "Droid Sans Mono" ) )
            self.m_tcLogger.SetFont( wx.Font( 9, 70, 90, 90, False, "Droid Sans Mono" ) )
        else:
            self.m_dvlcDataBuff.SetFont( wx.Font( 10, 75, 90, 90, False, "Lucida Console" ) )
            self.m_tcLogger.SetFont( wx.Font( 9, 75, 90, 90, False, "Lucida Console" ) )
        # -------
        self.m_tcTime.SetValue('Time')
        self.m_tcTime.Disable()
        self.m_tcState.SetValue('Status')
        self.m_tcState.Disable()
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)

        self.m_gProgBar.SetRange(1000)
        self.kboot.set_handler(self.update_progressbar, 0, self.m_gProgBar.GetRange())

    def __del__(self):
        if self.worker:
            self.worker.join()
            self.worker = None
        self.kboot.disconnect()

    def ctrlbt_enable(self):
        self.m_bReset.Enable()
        self.m_bErase.Enable()
        self.m_bUnlock.Enable()
        self.m_bRead.Enable()
        if self.data_buffer:
            self.m_bWrite.Enable()

    def ctrlbt_disable(self):
        self.m_bReset.Disable()
        self.m_bErase.Disable()
        self.m_bUnlock.Disable()
        self.m_bRead.Disable()
        self.m_bWrite.Disable()

    def connect(self):
        self.kboot.connect(self.devs[self.m_chDevice.GetSelection()])
        if self.get_mcu_info():
            self.m_bConnect.LabelText = 'Disconnect'
            self.m_chDevice.Disable()
            self.m_bRefresh.Disable()
            self.m_gProgBar.Enable()
            self.m_tcTime.Enable()
            self.m_tcState.Enable()
            self.m_tcState.SetValue('OK')
            self.ctrlbt_enable()
            if self.data_buffer:
                self.m_bWrite.Enable()
                self.m_bpSave.Enable()
                self.m_mSave.Enable()
            self.m_gProgBar.SetValue(self.m_gProgBar.GetRange())
        else:
            self.disconnect()

    def disconnect(self):
        if self.worker:
            self.kboot.abort()
            self.worker.abort()
            self.worker.join()
            self.worker = None
        self.kboot.disconnect()
        self.scan_for_dev()
        self.ctrlbt_disable()
        self.m_bConnect.LabelText = 'Connect'
        self.m_chDevice.Enable()
        self.m_bRefresh.Enable()
        self.m_dvlcMcuInfo.DeleteAllItems()
        self.m_gProgBar.SetValue(0)
        self.m_tcTime.SetValue('Time')
        self.m_tcTime.Disable()
        self.m_tcState.SetValue('Status')
        self.m_tcState.Disable()
        self.m_tcState.SetToolTipString('')

    def update_progressbar(self, value):
        cur_time = time.time() * 1000
        if self.m_pg_last_update_time is not None:
            if cur_time - self.m_pg_last_update_time < self.m_pg_min_update_wait:
                return
        self.m_pg_last_update_time = cur_time
        wx.CallAfter(self.m_gProgBar.SetValue, value)

    def task_begin(self, status_msg=''):
        self.m_gProgBar.SetValue(0)
        self.m_tcState.SetToolTipString('')
        self.m_tcState.SetForegroundColour(wx.Colour(0, 0, 0))
        self.m_tcState.SetValue(status_msg)
        self.m_tcTime.SetValue('Please Wait')
        self.timer.start()

    def task_end(self, status=True):
        if status:
            self.m_tcState.SetToolTipString('Operation Successful')
            self.m_tcState.SetForegroundColour(wx.Colour( 10, 120, 10 ))
            self.m_tcState.SetValue('OK')
            self.m_gProgBar.SetValue(self.m_gProgBar.GetRange())
        else:
            self.m_tcState.SetToolTipString('For error details read logger')
            self.m_tcState.SetForegroundColour(wx.Colour( 160, 10, 10 ))
            self.m_tcState.SetValue('ERROR')
        if self.timer.is_runing():
            self.timer.stop()
        self.m_tcTime.SetValue(self.timer.get_interval_str())

    def show_buffer(self, start_address=0):
        if self.data_buffer:
            length = len(self.data_buffer)
            address = start_address
            dline = []
            chstr = ''
            self.m_dvlcDataBuff.DeleteAllItems()
            for i in range(0, length):
                if (i % 16) == 0:
                    if i > 0:
                        dline += [chstr]
                        self.m_dvlcDataBuff.AppendItem(dline)
                        chstr = ''
                    dline = ["0x{:08X}".format(address)]
                    address += 16
                c = self.data_buffer[i]
                if not isinstance(c, int):
                    c = ord(c)
                dline += ['{:02X}'.format(c)]
                if 0x20 <= c < 0x7F:
                    chstr += chr(c)
                else:
                    chstr += '.'

    def get_mcu_info(self):
        if self.kboot.is_connected():
            self.task_begin()
            mcuinfo = self.kboot.get_mcu_info()
            if mcuinfo:
                self.task_end()

                for key, value in mcuinfo.items():
                    self.m_dvlcMcuInfo.AppendItem((key, value['string']))

                if mcuinfo.has_key(Property.FlashStartAddress.name):
                    self.FlashStartAddress = mcuinfo[Property.FlashStartAddress.name]['raw_value']
                    self.m_pRSAddr.SetValue('0x{:X}'.format(self.FlashStartAddress))

                if mcuinfo.has_key(Property.FlashSize.name):
                    self.FlashSize = mcuinfo[Property.FlashSize.name]['raw_value']
                    self.m_pRLen.SetValue('0x{:X}'.format(self.FlashSize))
                return True
            else:
                self.task_end(False)
                return False

    def load_image(self, path):
        retst = True
        self.data_buffer = []
        if path.lower().endswith('.bin'):
            with open(path, "rb") as f:
                raw_data = f.read()
                f.close()
            self.data_buffer = struct.unpack("%iB" % len(raw_data), raw_data)
        elif path.lower().endswith('.hex'):
            ihex = IntelHex()
            try:
                ihex.loadfile(path, format='hex')
            except Exception as e:
                wx.MessageBox("Could not read from file: %s\n\n%s" % (path, str(e)), 'ERROR', wx.OK|wx.ICON_ERROR)
                retst = False
            else:
                dhex = ihex.todict()
                self.data_buffer = [0xFF]*(max(dhex.keys()) + 1)
                for i, val in dhex.items():
                    self.data_buffer[i] = val
        elif path.lower().endswith(('.s19', '.srec')):
            srec = SRecFile()
            try:
                srec.open(path)
            except Exception as e:
                wx.MessageBox("Could not read from file: %s\n\n%s" % (path, str(e)), 'ERROR', wx.OK|wx.ICON_ERROR)
                retst = False
            else:
                self.data_buffer = srec.data
        else:
            retst = False
            wx.MessageBox('Not supported file Type !', 'ERROR', wx.OK | wx.ICON_ERROR)
        return retst

    def save_image(self, path):
        if self.data_buffer:
            if path.lower().endswith('.bin'):
                with open(path, "wb") as f:
                    f.write(bytearray(self.data_buffer))
                    f.close()
            elif path.lower().endswith('.hex'):
                ihex = IntelHex()
                ihex.frombytes(self.data_buffer, 0)
                ihex.start_addr = self.FlashStartAddress
                try:
                    ihex.tofile(path, format='hex')
                except Exception as e:
                    wx.MessageBox("Could not write into file: %s\n\n%s" % (path, str(e)), 'ERROR', wx.OK|wx.ICON_ERROR)
            elif path.lower().endswith(('.s19', '.srec')):
                srec = SRecFile()
                srec.header = "KBOOT"
                srec.start_addr = self.FlashStartAddress
                srec.data = self.data_buffer
                try:
                    srec.save(path)
                except Exception as e:
                    wx.MessageBox("Could not write into file: %s\n\n%s" % (path, str(e)), 'ERROR', wx.OK|wx.ICON_ERROR)
            else:
                wx.MessageBox('Not supported file Type !', 'ERROR', wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox('No data to save', 'INFO', wx.OK | wx.ICON_INFORMATION)

    def scan_for_dev(self):
        self.m_chDevice.Clear()
        self.devs = self.kboot.scan_usb_devs()
        if self.devs:
            self.m_chDevice.Enable()
            self.m_bConnect.Enable()
            for dev in self.devs:
                self.m_chDevice.Append(dev.getInfo())
            self.m_chDevice.SetSelection(0)
        else:
            self.m_chDevice.Disable()
            self.m_bConnect.Disable()

    # --- Event Handlers ---

    def OnExit(self, event):
        self.Close(False)

    def OnRefresh(self, event):
        self.scan_for_dev()
        event.Skip()

    def OnConnect(self, event):
        if self.kboot.is_connected():
            self.disconnect()
        else:
            self.connect()
        event.Skip()

    def OnOpen(self, event):
        wildcard = "Binary Image (*.bin)|*.bin;*.Bin;*.BIN|"   \
                   "IntelHEX Image (*.hex)|*.hex;*.Hex;*.HEX|" \
                   "Motorola Image (*.S19,*.srec)|*.s19;*.S19;*.srec"
        dialog = wx.FileDialog(self, "Choose a file", os.getcwd(), "", wildcard, wx.OPEN | wx.FD_FILE_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPaths()[0]
            if self.load_image(path):
                self.m_txtcDataInfo.SetValue(path)
                self.show_buffer()
                self.m_bpSave.Enable()
                self.m_mSave.Enable()
                if self.kboot.is_connected():
                    self.m_bWrite.Enable()
        dialog.Destroy()
        event.Skip()

    def OnSave(self, event):
        file_ext = ('.bin', '.hex', '.s19', '.srec')
        wildcard = "Binary Image (*.bin)|*.bin;*.Bin;*.BIN|"   \
                   "IntelHEX Image (*.hex)|*.hex;*.Hex;*.HEX|" \
                   "Motorola Image (*.S19,*.srec)|*.s19;*.S19;*.srec"
        dialog = wx.FileDialog(self, "Save to file", os.getcwd(), "image", wildcard, wx.SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPaths()[0]
            if not path.lower().endswith(file_ext):
                path += file_ext[dialog.GetFilterIndex()]
            self.save_image(path)
        dialog.Destroy()
        event.Skip()

    def OnSelUsbHid(self, event):
        event.Skip()

    def OnSelUart(self, event):
        event.Skip()

    def OnSettings(self, event):
        event.Skip()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.SetName('KBoot GUI')
        info.SetVersion('0.1 Beta')
        info.SetDescription("KBoot GUI is PC side user interface fo Kinetis bootloader")
        info.SetCopyright('(C) 2014 - 2016 Martin Olejar')
        info.SetWebSite('https://github.com/molejar')
        wx.AboutBox(info)
        event.Skip()

    def OnReset(self, event):
        if self.kboot.is_connected():
            # Call KBoot MCU reset function
            status = self.kboot.reset()
            self.disconnect()
        event.Skip()

    def OnUnlock(self, event):
        if self.kboot.is_connected():
            self.task_begin()
            # Call KBoot flash erase all and unsecure function
            status = self.kboot.flash_erase_all_unsecure()
            self.task_end(status == Status.Success)
        event.Skip()

    def OnErase(self, event):
        if self.kboot.is_connected():
            self.task_begin()
            # Call KBoot flash erase all function
            status = self.kboot.flash_erase_all()
            self.task_end(status == Status.Success)
        event.Skip()

    def OnWrite(self, event):
        if self.kboot.is_connected():
            saddr = self.FlashStartAddress + self.Offset
            #status = kboot.flash_erase_region(saddr, dlen)
            self.ctrlbt_disable()
            self.task_begin('Writing')
            status = self.kboot.flash_erase_all_unsecure()
            if status == Status.Success:
                self.worker = WorkerThread(self, 'write', self.kboot.write_memory, saddr=saddr, data=self.data_buffer)
                self.worker.start()
            else:
                self.task_end(False)
        event.Skip()

    def OnRead(self, event):
        if self.kboot.is_connected():
            self.start_addr = int(self.m_pRSAddr.GetValue(), 0)
            dlen  = int(self.m_pRLen.GetValue(), 0)
            self.ctrlbt_disable()
            self.task_begin('Reading')
            self.worker = WorkerThread(self, 'read', self.kboot.read_memory, saddr=self.start_addr, len=dlen)
            self.worker.start()
            event.Skip()

    def OnResult(self, event):
        """Show Result status."""
        if event.data:
            if event.data['status'] == Status.Success:
                self.task_end()
                if event.data['cmd'] == 'read':
                    self.data_buffer = event.data['data']
                    self.show_buffer(self.start_addr)
                    self.m_bpSave.Enable()
                    self.m_mSave.Enable()
                    self.m_txtcDataInfo.SetValue('MCU Memory')
                self.ctrlbt_enable()
            else:
                self.task_end(False)
                self.ctrlbt_enable()
                if event.data['status'] == -1:
                    self.disconnect()
        self.worker = None

    def OnLeaveLogger(self, event):
        self.m_tcLogger.SetInsertionPoint(self.m_tcLogger.GetLastPosition())
        event.Skip()

    def OnChoiceLogLevel(self, event):
        log_level = [logging.DEBUG, logging.INFO, logging.ERROR]
        mylogger.setLevel(log_level[self.m_chLogLevel.GetSelection()])
        event.Skip()

    def OnClearLog(self, event):
        self.m_tcLogger.Clear()
        event.Skip()

    def OnSaveLog(self, event):
        dialog = wx.FileDialog(self, "Save to file", os.getcwd(), "log.txt", "Text File (*.txt)|*.txt", wx.SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPaths()[0]
            if not path.lower().endswith('.txt'):
                path += '.txt'
            with open(path, "w") as f:
                    f.write(self.m_tcLogger.GetValue())
                    f.close()
        event.Skip()


class MyApp(wx.App):
    def OnInit(self):
        frame = KBootAppMain(None)
        frame.Show(True)
        return True


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()

