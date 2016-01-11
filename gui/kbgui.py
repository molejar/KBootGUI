# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.dataview
import wx.propgrid as pg

###########################################################################
## Class AppMain
###########################################################################

class AppMain ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"KBoot GUI", pos = wx.DefaultPosition, size = wx.Size( 724,584 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.Size( 724,584 ), wx.Size( -1,-1 ) )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		
		self.m_menubar = wx.MenuBar( 0 )
		self.m_mFile = wx.Menu()
		self.m_mOpen = wx.MenuItem( self.m_mFile, wx.ID_ANY, u"&Open"+ u"\t" + u"Ctrl+O", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mFile.AppendItem( self.m_mOpen )
		
		self.m_mSave = wx.MenuItem( self.m_mFile, wx.ID_ANY, u"&Save"+ u"\t" + u"Ctrl+S", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mFile.AppendItem( self.m_mSave )
		self.m_mSave.Enable( False )
		
		self.m_mFile.AppendSeparator()
		
		self.m_mExit = wx.MenuItem( self.m_mFile, wx.ID_ANY, u"E&xit"+ u"\t" + u"Ctrl+X", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mFile.AppendItem( self.m_mExit )
		
		self.m_menubar.Append( self.m_mFile, u"&File" ) 
		
		self.m_mInterface = wx.Menu()
		self.m_mUsbHid = wx.MenuItem( self.m_mInterface, wx.ID_ANY, u"&USB-HID", wx.EmptyString, wx.ITEM_RADIO )
		self.m_mInterface.AppendItem( self.m_mUsbHid )
		
		self.m_mUart = wx.MenuItem( self.m_mInterface, wx.ID_ANY, u"&RS232", wx.EmptyString, wx.ITEM_RADIO )
		self.m_mInterface.AppendItem( self.m_mUart )
		self.m_mUart.Enable( False )
		
		self.m_menubar.Append( self.m_mInterface, u"&Interface" ) 
		
		self.m_mTools = wx.Menu()
		self.m_mSettings = wx.MenuItem( self.m_mTools, wx.ID_ANY, u"S&ettings"+ u"\t" + u"Ctrl+E", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mTools.AppendItem( self.m_mSettings )
		self.m_mSettings.Enable( False )
		
		self.m_menubar.Append( self.m_mTools, u"&Tools" ) 
		
		self.m_mHelp = wx.Menu()
		self.m_mAbout = wx.MenuItem( self.m_mHelp, wx.ID_ANY, u"&About"+ u"\t" + u"F1", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_mHelp.AppendItem( self.m_mAbout )
		
		self.m_menubar.Append( self.m_mHelp, u"&Help" ) 
		
		self.SetMenuBar( self.m_menubar )
		
		m_sizer = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer = wx.FlexGridSizer( 6, 0, 0, 0 )
		fgSizer.AddGrowableCol( 0 )
		fgSizer.AddGrowableRow( 2 )
		fgSizer.SetFlexibleDirection( wx.BOTH )
		fgSizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_ALL )
		
		fgSizer2 = wx.FlexGridSizer( 0, 4, 0, 0 )
		fgSizer2.AddGrowableCol( 1 )
		fgSizer2.SetFlexibleDirection( wx.BOTH )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_stxDevice = wx.StaticText( self, wx.ID_ANY, u"USB Device:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stxDevice.Wrap( -1 )
		fgSizer2.Add( self.m_stxDevice, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.LEFT|wx.RIGHT, 5 )
		
		m_chDeviceChoices = []
		self.m_chDevice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_chDeviceChoices, 0 )
		self.m_chDevice.SetSelection( 0 )
		self.m_chDevice.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		
		fgSizer2.Add( self.m_chDevice, 1, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		self.m_bRefresh = wx.Button( self, wx.ID_ANY, u"Refresh", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		fgSizer2.Add( self.m_bRefresh, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.SHAPED, 2 )
		
		self.m_bConnect = wx.Button( self, wx.ID_ANY, u"Connect", wx.DefaultPosition, wx.Size( 90,-1 ), 0 )
		self.m_bConnect.Enable( False )
		
		fgSizer2.Add( self.m_bConnect, 0, wx.ALL|wx.SHAPED|wx.ALIGN_CENTER_VERTICAL, 2 )
		
		
		fgSizer.Add( fgSizer2, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		fgSizer.Add( self.m_staticline1, 0, wx.EXPAND|wx.ALL, 5 )
		
		self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,370 ), wx.NB_FIXEDWIDTH|wx.NB_TOP )
		self.m_panel1 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel1.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		bSizer3 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_dvlcMcuInfo = wx.dataview.DataViewListCtrl( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_ROW_LINES|wx.dataview.DV_VERT_RULES )
		bSizer3.Add( self.m_dvlcMcuInfo, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel1.SetSizer( bSizer3 )
		self.m_panel1.Layout()
		bSizer3.Fit( self.m_panel1 )
		self.m_notebook1.AddPage( self.m_panel1, u"MCU Info", True )
		self.m_panel2 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel2.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		fgSizer4 = wx.FlexGridSizer( 2, 0, 0, 0 )
		fgSizer4.AddGrowableCol( 0 )
		fgSizer4.AddGrowableRow( 1 )
		fgSizer4.SetFlexibleDirection( wx.BOTH )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		bSizer61 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_stxtDataInfo = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Source:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stxtDataInfo.Wrap( -1 )
		bSizer61.Add( self.m_stxtDataInfo, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		self.m_txtcDataInfo = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY )
		self.m_txtcDataInfo.SetBackgroundColour( wx.Colour( 240, 240, 240 ) )
		
		bSizer61.Add( self.m_txtcDataInfo, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_bpOpen = wx.BitmapButton( self.m_panel2, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FILE_OPEN,  ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpOpen.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.m_bpOpen.SetToolTipString( u"Load Data From File" )
		
		bSizer61.Add( self.m_bpOpen, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		self.m_bpSave = wx.BitmapButton( self.m_panel2, wx.ID_ANY, wx.ArtProvider.GetBitmap( wx.ART_FILE_SAVE,  ), wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW )
		self.m_bpSave.Enable( False )
		self.m_bpSave.SetToolTipString( u"Save Data Into File" )
		
		bSizer61.Add( self.m_bpSave, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		fgSizer4.Add( bSizer61, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 2 )
		
		self.m_dvlcDataBuff = wx.dataview.DataViewListCtrl( self.m_panel2, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_dvlcDataBuff.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
		
		fgSizer4.Add( self.m_dvlcDataBuff, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel2.SetSizer( fgSizer4 )
		self.m_panel2.Layout()
		fgSizer4.Fit( self.m_panel2 )
		self.m_notebook1.AddPage( self.m_panel2, u"Data Buffer", False )
		self.m_panel5 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel5.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		bSizer51 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_pGridOptions = pg.PropertyGrid(self.m_panel5, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_BOLD_MODIFIED|wx.propgrid.PG_DEFAULT_STYLE|wx.propgrid.PG_SPLITTER_AUTO_CENTER|wx.SUNKEN_BORDER)
		self.m_pGridOptions.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		bSizer51.Add( self.m_pGridOptions, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.m_panel5.SetSizer( bSizer51 )
		self.m_panel5.Layout()
		bSizer51.Fit( self.m_panel5 )
		self.m_notebook1.AddPage( self.m_panel5, u"CMD Options", False )
		self.m_panel7 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panel7.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		fgSizer3 = wx.FlexGridSizer( 2, 0, 0, 0 )
		fgSizer3.AddGrowableCol( 0 )
		fgSizer3.AddGrowableRow( 0 )
		fgSizer3.SetFlexibleDirection( wx.BOTH )
		fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_tcLogger = wx.TextCtrl( self.m_panel7, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_DONTWRAP|wx.TE_MULTILINE|wx.TE_NOHIDESEL|wx.TE_READONLY )
		self.m_tcLogger.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
		self.m_tcLogger.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		self.m_tcLogger.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		fgSizer3.Add( self.m_tcLogger, 1, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )
		
		bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_staticText3 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Level:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText3.Wrap( -1 )
		bSizer5.Add( self.m_staticText3, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		m_chLogLevelChoices = [ u"Debug", u"Info", u"Error" ]
		self.m_chLogLevel = wx.Choice( self.m_panel7, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_chLogLevelChoices, 0 )
		self.m_chLogLevel.SetSelection( 0 )
		self.m_chLogLevel.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		
		bSizer5.Add( self.m_chLogLevel, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.LEFT, 5 )
		
		
		bSizer5.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
		
		self.m_bClearLog = wx.Button( self.m_panel7, wx.ID_ANY, u"Clear", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		bSizer5.Add( self.m_bClearLog, 0, wx.ALL, 5 )
		
		self.m_bSaveLog = wx.Button( self.m_panel7, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.Size( 70,-1 ), 0 )
		bSizer5.Add( self.m_bSaveLog, 0, wx.ALL, 5 )
		
		
		fgSizer3.Add( bSizer5, 1, wx.EXPAND|wx.RIGHT|wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5 )
		
		
		self.m_panel7.SetSizer( fgSizer3 )
		self.m_panel7.Layout()
		fgSizer3.Fit( self.m_panel7 )
		self.m_notebook1.AddPage( self.m_panel7, u"Logger", False )
		
		fgSizer.Add( self.m_notebook1, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 5 )
		
		fgSizer5 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer5.AddGrowableCol( 1 )
		fgSizer5.AddGrowableRow( 0 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
		
		self.m_tcTime = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,24 ), wx.TE_CENTRE|wx.TE_READONLY )
		self.m_tcTime.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		self.m_tcTime.SetForegroundColour( wx.Colour( 0, 0, 0 ) )
		self.m_tcTime.SetBackgroundColour( wx.Colour( 224, 224, 224 ) )
		
		fgSizer5.Add( self.m_tcTime, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.RIGHT|wx.LEFT, 6 )
		
		self.m_gProgBar = wx.Gauge( self, wx.ID_ANY, 100, wx.DefaultPosition, wx.DefaultSize, wx.GA_HORIZONTAL|wx.GA_SMOOTH )
		self.m_gProgBar.SetValue( 0 ) 
		fgSizer5.Add( self.m_gProgBar, 1, wx.ALIGN_CENTER_VERTICAL|wx.BOTTOM|wx.RIGHT|wx.LEFT|wx.EXPAND, 1 )
		
		self.m_tcState = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,24 ), wx.TE_CENTRE|wx.TE_READONLY )
		self.m_tcState.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		self.m_tcState.SetForegroundColour( wx.Colour( 0, 0, 0 ) )
		self.m_tcState.SetBackgroundColour( wx.Colour( 224, 224, 224 ) )
		
		fgSizer5.Add( self.m_tcState, 1, wx.ALIGN_CENTER|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.RIGHT|wx.LEFT, 6 )
		
		
		fgSizer.Add( fgSizer5, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND|wx.ALL, 5 )
		
		gSizer1 = wx.GridSizer( 0, 5, 0, 0 )
		
		gSizer1.SetMinSize( wx.Size( -1,50 ) ) 
		self.m_bReset = wx.Button( self, wx.ID_ANY, u"Reset", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_bReset.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		self.m_bReset.Enable( False )
		
		gSizer1.Add( self.m_bReset, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
		
		self.m_bUnlock = wx.Button( self, wx.ID_ANY, u"Unlock", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_bUnlock.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		self.m_bUnlock.Enable( False )
		
		gSizer1.Add( self.m_bUnlock, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_bErase = wx.Button( self, wx.ID_ANY, u"Erase", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_bErase.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		self.m_bErase.Enable( False )
		
		gSizer1.Add( self.m_bErase, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_bWrite = wx.Button( self, wx.ID_ANY, u"Write", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_bWrite.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		self.m_bWrite.Enable( False )
		
		gSizer1.Add( self.m_bWrite, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		self.m_bRead = wx.Button( self, wx.ID_ANY, u"Read", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_bRead.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 92, False, wx.EmptyString ) )
		self.m_bRead.Enable( False )
		
		gSizer1.Add( self.m_bRead, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
		
		
		fgSizer.Add( gSizer1, 1, wx.EXPAND|wx.FIXED_MINSIZE|wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_HORIZONTAL, 5 )
		
		
		fgSizer.AddSpacer( ( 0, 10), 1, wx.EXPAND, 5 )
		
		
		m_sizer.Add( fgSizer, 1, wx.EXPAND|wx.FIXED_MINSIZE, 5 )
		
		
		self.SetSizer( m_sizer )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_MENU, self.OnOpen, id = self.m_mOpen.GetId() )
		self.Bind( wx.EVT_MENU, self.OnSave, id = self.m_mSave.GetId() )
		self.Bind( wx.EVT_MENU, self.OnExit, id = self.m_mExit.GetId() )
		self.Bind( wx.EVT_MENU, self.OnSelUsbHid, id = self.m_mUsbHid.GetId() )
		self.Bind( wx.EVT_MENU, self.OnSelUart, id = self.m_mUart.GetId() )
		self.Bind( wx.EVT_MENU, self.OnSettings, id = self.m_mSettings.GetId() )
		self.Bind( wx.EVT_MENU, self.OnAbout, id = self.m_mAbout.GetId() )
		self.m_bRefresh.Bind( wx.EVT_BUTTON, self.OnRefresh )
		self.m_bConnect.Bind( wx.EVT_BUTTON, self.OnConnect )
		self.m_bpOpen.Bind( wx.EVT_BUTTON, self.OnOpen )
		self.m_bpSave.Bind( wx.EVT_BUTTON, self.OnSave )
		self.m_tcLogger.Bind( wx.EVT_LEAVE_WINDOW, self.OnLeaveLogger )
		self.m_chLogLevel.Bind( wx.EVT_CHOICE, self.OnChoiceLogLevel )
		self.m_bClearLog.Bind( wx.EVT_BUTTON, self.OnClearLog )
		self.m_bSaveLog.Bind( wx.EVT_BUTTON, self.OnSaveLog )
		self.m_bReset.Bind( wx.EVT_BUTTON, self.OnReset )
		self.m_bUnlock.Bind( wx.EVT_BUTTON, self.OnUnlock )
		self.m_bErase.Bind( wx.EVT_BUTTON, self.OnErase )
		self.m_bWrite.Bind( wx.EVT_BUTTON, self.OnWrite )
		self.m_bRead.Bind( wx.EVT_BUTTON, self.OnRead )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnOpen( self, event ):
		event.Skip()
	
	def OnSave( self, event ):
		event.Skip()
	
	def OnExit( self, event ):
		event.Skip()
	
	def OnSelUsbHid( self, event ):
		event.Skip()
	
	def OnSelUart( self, event ):
		event.Skip()
	
	def OnSettings( self, event ):
		event.Skip()
	
	def OnAbout( self, event ):
		event.Skip()
	
	def OnRefresh( self, event ):
		event.Skip()
	
	def OnConnect( self, event ):
		event.Skip()
	
	
	
	def OnLeaveLogger( self, event ):
		event.Skip()
	
	def OnChoiceLogLevel( self, event ):
		event.Skip()
	
	def OnClearLog( self, event ):
		event.Skip()
	
	def OnSaveLog( self, event ):
		event.Skip()
	
	def OnReset( self, event ):
		event.Skip()
	
	def OnUnlock( self, event ):
		event.Skip()
	
	def OnErase( self, event ):
		event.Skip()
	
	def OnWrite( self, event ):
		event.Skip()
	
	def OnRead( self, event ):
		event.Skip()
	

