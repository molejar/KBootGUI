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
from kboot import *
from intelhex import IntelHex
from flufl.enum import IntEnum

mylogger = logging.getLogger()


# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(wx.ID_ANY, wx.ID_ANY, EVT_RESULT_ID, func)


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
        self.__notify_window = args[0]
        self.__want_abort = 0
        self.__cmd  = args[1]
        self.__func = args[2]
        self.__args = kwargs

    def run(self):
        """Run Worker Thread."""
        status = 0
        data = []
        try:
            if self.__cmd == CMD.Read:
                data = self.__func(self.__args['saddr'], self.__args['len'])
            else:
                self.__func(self.__args['saddr'], self.__args['data'])
        except (KBootTimeoutError, KBootConnectionError):
            status = -1
        except:
            status = 1
        # Execute CallBack Event
        wx.PostEvent(self.__notify_window, ResultEvent(cmd=self.__cmd, status=status, data=data))

    def abort(self):
        """abort worker thread."""
        self.__want_abort = 1


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


class CMD(IntEnum):
    Read   = 0x01
    Write  = 0x02
    Erase  = 0x03
    Unlock = 0x04
    Reset  = 0x05


class KBootAppMain(AppMain):
    # Connected MCU Params
    FlashStartAddress = 0
    FlashSize = 0
    FlashSectorSize = 0

    # Actual CMD Params
    WR_Offset = 0
    ER_StartAddr = 0
    ER_Len = 0
    RD_StartAddr = 0
    RD_Len = 0
    KEYVALUE = bytearray([0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38]) # 12345678

    # Supported baudrates
    UART_BR = (600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000, 576000, 921600)

    # Supported images
    WILDCARD = "Motorola Image (*.S19,*.srec)|*.s19;*.S19;*.srec|" \
               "IntelHEX Image (*.hex)|*.hex;*.Hex;*.HEX|" \
               "Binary Image (*.bin)|*.bin;*.Bin;*.BIN"

    def __init__(self, parent):
        AppMain.__init__(self, parent)
        #self.SetIcon(wx.Icon('mcu.png', wx.PNG_TYPE_COLOUR, 16, 16))
        handler = WxTextCtrlHandler(self.m_tcLogger)
        mylogger.addHandler(handler)
        FORMAT = "[%(asctime)s.%(msecs)03d %(levelname)-5s] %(message)s"
        handler.setFormatter(logging.Formatter(FORMAT, datefmt='%M:%S'))
        mylogger.setLevel(logging.DEBUG)
        # -------
        self.m_pg_min_update_wait = 50
        self.m_pg_last_update_time = None
        self.start_addr = 0
        self.data_buffer = bytearray()
        self.operation = None
        self.worker = None
        # -------
        self.timer = Timer()
        self.kboot = KBoot()
        self.scan_for_dev()
        # -------
        self.m_dvlcMcuInfo.AppendTextColumn('Parameter', width=150, flags=dw.DATAVIEW_COL_SORTABLE)
        self.m_dvlcMcuInfo.AppendTextColumn('Value', width=500)
        # -------
        self.m_dvlcDataBuff.AppendTextColumn("Address", width=95, align=wx.ALIGN_CENTER, flags=16)
        for i in range(16):
            self.m_dvlcDataBuff.AppendTextColumn("{:01X}".format(i), width=26, align=wx.ALIGN_CENTER, flags=16)
        self.m_dvlcDataBuff.AppendTextColumn("0123456789ABCDEF", width=140, align=wx.ALIGN_CENTER)
        # -------
        self.m_pUnlock = self.m_pGridOptions.Append(pg.PropertyCategory(u"Unlock CMD", u"UnlockCMD"))
        self.m_pUMode = self.m_pGridOptions.Append(pg.EnumProperty(u"Mode", u"UMode",
                                                                  ['Default (Mass Erase)',
                                                                   'Use Backdoor Key in ASCII Format',
                                                                   'Use Backdoor Key in HEX Format'], [0, 1, 2], 0))
        self.m_pUKey = self.m_pGridOptions.Append(pg.StringProperty(u"Key Value", u"UKey", "12345678"))
        self.m_pUKey.Enable(False)
        self.m_pErase = self.m_pGridOptions.Append(pg.PropertyCategory(u"Erase CMD", u"EraseCMD"))
        self.m_pEDef = self.m_pGridOptions.Append(pg.EnumProperty(u"Mode", u"EMode",
                                                                  ['Mass Erase', 'Sector Erase'], [0, 1], 0))
        self.m_pESAddr = self.m_pGridOptions.Append(pg.StringProperty(u"Start Address", u"ESAddr", "0x0"))
        self.m_pELen = self.m_pGridOptions.Append(pg.StringProperty(u"Length", u"ELen", "0x0"))
        self.m_pESAddr.Enable(False)
        self.m_pELen.Enable(False)
        self.m_pWrite = self.m_pGridOptions.Append(pg.PropertyCategory(u"Write CMD", u"WriteCMD"))
        self.m_pWOffset = self.m_pGridOptions.Append(pg.StringProperty(u"Offset", u"WROffset", "0x0"))
        self.m_pWErase = self.m_pGridOptions.Append(pg.EnumProperty(u"Erase Befor Write ?", u"EraseBeforWrite",
                                                                    ['Yes (Mass Erase)', 'Yes (Sector Erase)', 'No'],
                                                                    [0, 1, 2], 0))
        self.m_pRead = self.m_pGridOptions.Append(pg.PropertyCategory(u"Read CMD", u"ReadCMD"))
        self.m_pRSAddr = self.m_pGridOptions.Append(pg.StringProperty(u"Start Address", u"RSAddr", "0x0"))
        self.m_pRLen = self.m_pGridOptions.Append(pg.StringProperty(u"Length", u"RLen", "0x0"))
        self.m_pGridOptions.Disable()
        # ------
        #self.m_panel3.Show(False)
        self.m_pBDKey = self.m_pGridFCA.Append(pg.PropertyCategory(u"BackDoor Key", u"BackDoorKey"))
        self.m_pBKFM = self.m_pGridFCA.Append(pg.EnumProperty(u"Key Format", u"BKFormat",
                                                                  ['In ASCII Value',
                                                                   'In HEX Value'], [0, 1], 0))
        self.m_pBDKeyVal = self.m_pGridFCA.Append(pg.StringProperty(u"Key Value", u"BDKey", "12345678"))

        self.m_pFLProt = self.m_pGridFCA.Append(pg.PropertyCategory(u"FLASH Protection", u"FLProt"))
        # -------
        self.m_panel4.Show(False)
        # -------
        self.m_dvlcDataBuff.SetForegroundColour(wx.Colour(10, 145, 40))
        self.m_dvlcDataBuff.SetBackgroundColour(wx.Colour(32, 32, 32))
        self.m_tcLogger.SetForegroundColour(wx.Colour(10, 185, 80))
        self.m_tcLogger.SetBackgroundColour(wx.Colour(32, 32, 32))
        # -------
        if os.name == "posix":
            self.m_dvlcDataBuff.SetFont(wx.Font(10, 70, 90, 90, False, "Droid Sans Mono"))
            self.m_tcLogger.SetFont(wx.Font(9, 70, 90, 90, False, "Droid Sans Mono"))
        else:
            self.m_dvlcDataBuff.SetFont(wx.Font( 10, 75, 90, 90, False, "Lucida Console"))
            self.m_tcLogger.SetFont(wx.Font(9, 75, 90, 90, False, "Lucida Console"))
        # -------
        self.m_tcTime.SetValue('Time')
        self.m_tcTime.Disable()
        self.m_tcState.SetValue('Status')
        self.m_tcState.Disable()

        self.m_chBaudrate.AppendItems([str(c) for c in self.UART_BR])
        self.m_chBaudrate.SetSelection(9)

        self.m_gProgBar.SetRange(1000)
        self.kboot.set_handler(self.update_progressbar, 0, self.m_gProgBar.GetRange())

        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)

        self.m_pGridOptions.Bind(pg.EVT_PG_CHANGED, self.OnCmdOpsChanger)

    def __del__(self):
        if self.worker:
            self.worker.join()
            self.worker = None
        self.kboot.disconnect()

    def ctrlbt_enable(self):
        self.m_pGridOptions.Enable()
        #self.m_pGridOptions.Show(True)
        self.m_bReset.Enable()
        self.m_bErase.Enable()
        self.m_bUnlock.Enable()
        self.m_bRead.Enable()
        if self.data_buffer:
            self.m_bWrite.Enable()

    def ctrlbt_disable(self):
        self.m_pGridOptions.Disable()
        #self.m_pGridOptions.Show(False)
        self.m_bReset.Disable()
        self.m_bErase.Disable()
        self.m_bUnlock.Disable()
        self.m_bRead.Disable()
        self.m_bWrite.Disable()

    def connect(self):
        if self.m_mUsbHid.IsChecked():
            self.kboot.connect_usb(self.devs[self.m_chDevice.GetSelection()])
        else:
            self.kboot.connect_uart(self.devs[self.m_chDevice.GetSelection()],
                                    self.UART_BR[self.m_chBaudrate.GetSelection()])
        if self.get_mcu_info():
            self.m_mUsbHid.Enable(False)
            self.m_mUart.Enable(False)
            self.m_bConnect.LabelText = 'Disconnect'
            self.m_chBaudrate.Disable()
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
        self.m_mUsbHid.Enable(True)
        self.m_mUart.Enable(True)
        self.m_bConnect.LabelText = 'Connect'
        self.m_chBaudrate.Enable()
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

                if mcuinfo.has_key(Property.FlashSize.name):
                    self.FlashSize = mcuinfo[Property.FlashSize.name]['raw_value']

                if mcuinfo.has_key(Property.FlashSectorSize.name):
                    self.FlashSectorSize = mcuinfo[Property.FlashSectorSize.name]['raw_value']

                self.ER_StartAddr = self.FlashStartAddress
                self.m_pESAddr.SetValue('0x{:X}'.format(self.ER_StartAddr))
                self.ER_Len = self.FlashSize
                self.m_pELen.SetValue('0x{:X}'.format(self.ER_Len))

                self.RD_StartAddr = self.FlashStartAddress
                self.m_pRSAddr.SetValue('0x{:X}'.format(self.RD_StartAddr))
                self.RD_Len = self.FlashSize
                self.m_pRLen.SetValue('0x{:X}'.format(self.RD_Len))
                return True
            else:
                self.task_end(False)
                return False

    def load_image(self, path):
        retst = True
        self.data_buffer = bytearray()
        if path.lower().endswith('.bin'):
            with open(path, "rb") as f:
                self.data_buffer = f.read()
                f.close()
        elif path.lower().endswith('.hex'):
            ihex = IntelHex()
            try:
                ihex.loadfile(path, format='hex')
            except Exception as e:
                wx.MessageBox("Could not read from file: %s\n\n%s" % (path, str(e)), 'ERROR', wx.OK|wx.ICON_ERROR)
                retst = False
            else:
                dhex = ihex.todict()
                self.data_buffer = bytearray([0xFF]*(max(dhex.keys()) + 1))
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
                    f.write(self.data_buffer)
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
        if self.m_mUsbHid.IsChecked():
            self.devs = self.kboot.scan_usb_devs()
        else:
            self.devs = self.kboot.scan_uart_ports()
        if self.devs:
            self.m_chDevice.Enable()
            self.m_chBaudrate.Enable()
            self.m_bConnect.Enable()
            for dev in self.devs:
                if self.m_mUsbHid.IsChecked():
                    self.m_chDevice.Append(dev.getInfo())
                else:
                    self.m_chDevice.Append(dev)
            self.m_chDevice.SetSelection(0)
        else:
            self.m_chBaudrate.Disable()
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

        dialog = wx.FileDialog(self, "Choose a file", os.getcwd(), "", self.WILDCARD, wx.OPEN | wx.FD_FILE_MUST_EXIST)
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
        dialog = wx.FileDialog(self, "Save to file", os.getcwd(), "image", self.WILDCARD, wx.SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPaths()[0]
            if not path.lower().endswith(file_ext):
                path += file_ext[dialog.GetFilterIndex()]
            self.save_image(path)
        dialog.Destroy()
        event.Skip()

    def OnSelUsbHid(self, event):
        self.m_stxDevice.SetLabel('USB Device:')
        self.m_stBaudrate.Hide()
        self.m_chBaudrate.Hide()
        self.Layout()
        self.scan_for_dev()
        event.Skip()

    def OnSelUart(self, event):
        self.m_stxDevice.SetLabel('RS232 Port :')
        self.m_stBaudrate.Show()
        self.m_chBaudrate.Show()
        self.Layout()
        self.scan_for_dev()
        event.Skip()

    def OnSettings(self, event):
        event.Skip()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.SetName('KBoot GUI')
        info.SetVersion('0.1 Beta')
        info.SetDescription("KBoot GUI is PC side user interface fo Kinetis bootloader")
        info.SetCopyright('(C) 2016 Martin Olejar')
        info.SetWebSite('https://github.com/molejar')
        wx.AboutBox(info)
        event.Skip()

    def OnReset(self, event):
        self.kboot.reset()
        self.disconnect()
        event.Skip()

    def OnUnlock(self, event):
        self.task_begin()
        try:
            if self.m_pUMode.GetValue() == 0:
                self.kboot.flash_erase_all_unsecure()
            else:
                self.kboot.flash_security_disable(self.KEYVALUE)
        except:
            self.task_end(False)
        else:
            self.task_end(True)
        event.Skip()

    def OnErase(self, event):
        self.task_begin()
        try:
            if self.m_pErase.GetValue() == 0:
                self.kboot.flash_erase_all_unsecure()
            else:
                self.kboot.flash_erase_region(self.ER_StartAddr, self.ER_Len)
        except:
            self.task_end(False)
        else:
            self.task_end(True)
        event.Skip()

    def OnWrite(self, event):
        if self.kboot.is_connected():
            saddr = self.FlashStartAddress + self.WR_Offset
            self.ctrlbt_disable()
            self.task_begin('Writing')
            try:
                if self.m_pWErase.GetValue() == 0:
                    self.kboot.flash_erase_all_unsecure()
                elif self.m_pWErase.GetValue() == 1:
                    esaddr = (saddr & ~(self.FlashSectorSize - 1))
                    eslen = (len(self.data_buffer) & ~(self.FlashSectorSize - 1))
                    if (len(self.data_buffer) % self.FlashSectorSize) > 0:
                        eslen += self.FlashSectorSize
                    self.kboot.flash_erase_region(esaddr, eslen)
                else:
                    logging.info('Writing without erase')
            except:
                self.task_end(False)
            else:
                self.worker = WorkerThread(self, CMD.Write, self.kboot.write_memory, saddr=saddr, data=self.data_buffer)
                self.worker.start()
        event.Skip()

    def OnRead(self, event):
        self.start_addr = self.RD_StartAddr
        self.ctrlbt_disable()
        self.task_begin('Reading')
        self.worker = WorkerThread(self, CMD.Read, self.kboot.read_memory, saddr=self.start_addr, len=self.RD_Len)
        self.worker.start()
        event.Skip()

    def OnResult(self, event):
        """Show Result status."""
        if event.data:
            if event.data['status'] == 0:
                self.task_end()
                if event.data['cmd'] == CMD.Read:
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

    def OnCmdOpsChanger(self, event):
        prop = event.GetProperty()
        getval = prop.GetValue()
        if prop.GetName() == 'UMode':
            if getval == 1:
                self.m_pUKey.SetValue(array_to_string(self.KEYVALUE, '', 'c'))
            elif getval == 2:
                self.m_pUKey.SetValue(array_to_string(self.KEYVALUE, ' ')[:-1])
        elif prop.GetName() == 'UKey':
            if self.m_pUMode.GetValue() == 1:
                if len(getval) != 8:
                    self.m_pUKey.SetValue(array_to_string(self.KEYVALUE, '', 'c'))
                    wx.MessageBox(" Key Value \"%s\" hasn\'t correct length !\n\n Use 8 ASCII Chars"
                              % getval, 'ERROR', wx.OK|wx.ICON_ERROR)
                self.KEYVALUE = string_to_array(self.m_pUKey.GetValue(), 1, 0)
            if self.m_pUMode.GetValue() == 2:
                getval = getval.replace(' ', '')
                print(getval)
                if len(getval) != 16:
                    self.m_pUKey.SetValue(array_to_string(self.KEYVALUE, ' ')[:-1])
                    wx.MessageBox(" Key Value \"%s\" hasn\'t correct length !\n\n Use 8 HEX Chars"
                          % getval, 'ERROR', wx.OK|wx.ICON_ERROR)
                else:
                    try:
                        tmp = string_to_array(getval, 2, 16)
                    except:
                        self.m_pUKey.SetValue(array_to_string(self.KEYVALUE, ' ')[:-1])
                        wx.MessageBox(" Key Value \"%s\" hasn\'t correct hex chars !\n\n Use Chars in range 0 - F"
                              % getval, 'ERROR', wx.OK|wx.ICON_ERROR)
                    else:
                        self.KEYVALUE = tmp
        elif prop.GetValueType() == 'string':
            try:
                val = int(getval, 0)
            except:
                if prop.GetName() == 'ESAddr':
                    prop.SetValue('0x{:X}'.format(self.ER_StartAddr))
                elif prop.GetName() == 'ELen':
                    prop.SetValue('0x{:X}'.format(self.ER_Len))
                elif prop.GetName() == 'WROffset':
                    prop.SetValue('0x{:X}'.format(self.WR_Offset))
                elif prop.GetName() == 'RSAddr':
                    prop.SetValue('0x{:X}'.format(self.RD_StartAddr))
                elif prop.GetName() == 'RLen':
                    prop.SetValue('0x{:X}'.format(self.RD_Len))
                wx.MessageBox(" Value \"%s\" hasn\'t correct type !\n\n Use decimal (0...) or hex (0x...) chars"
                              % getval, 'ERROR', wx.OK|wx.ICON_ERROR)
            else:
                if prop.GetName() == 'ESAddr':
                    if (val % self.FlashSectorSize) > 0:
                        prop.SetValue('0x{:X}'.format(self.ER_StartAddr))
                        wx.MessageBox(" Start Address Value for Erase CMD must be\n aligned to Flash Sector Size: 0x%X "
                                      % self.FlashSectorSize, 'ERROR', wx.OK|wx.ICON_ERROR)
                    else:
                        self.ER_StartAddr = val
                elif prop.GetName() == 'ELen':
                    if (val % self.FlashSectorSize) > 0:
                        prop.SetValue('0x{:X}'.format(self.ER_Len))
                        wx.MessageBox(" Length Value for Erase CMD must be\n aligned to Flash Sector Size: 0x%X "
                                      % self.FlashSectorSize, 'ERROR', wx.OK|wx.ICON_ERROR)
                    else:
                        self.ER_Len = val
                elif prop.GetName() == 'WROffset':
                    self.WR_Offset = val
                elif prop.GetName() == 'RSAddr':
                    self.RD_StartAddr = val
                elif prop.GetName() == 'RLen':
                    self.RD_Len = val

        if prop.GetName() == 'UMode':
            if prop.GetValue() == 0:
                self.m_pUKey.Enable(False)
            else:
                self.m_pUKey.Enable(True)
        if prop.GetName() == 'EMode':
            if prop.GetValue() == 0:
                self.m_pESAddr.Enable(False)
                self.m_pELen.Enable(False)
            else:
                self.m_pESAddr.Enable(True)
                self.m_pELen.Enable(True)


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
        frame.Show()
        return True


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()

