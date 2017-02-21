# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Mote PC Controller", pos = wx.DefaultPosition, size = wx.Size( 300,400 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE|wx.MINIMIZE_BOX|wx.SYSTEM_MENU|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )
		
		self.menu = wx.MenuBar( 0 )
		self.filemenu = wx.Menu()
		self.menuAbout = wx.MenuItem( self.filemenu, wx.ID_ABOUT, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.filemenu.AppendItem( self.menuAbout )
		
		self.menuExit = wx.MenuItem( self.filemenu, wx.ID_EXIT, u"Exit", wx.EmptyString, wx.ITEM_NORMAL )
		self.filemenu.AppendItem( self.menuExit )
		
		self.menu.Append( self.filemenu, u"File" ) 
		
		self.SetMenuBar( self.menu )
		
		sizerMain = wx.BoxSizer( wx.VERTICAL )
		
		self.notebookMain = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.panelSystem = wx.Panel( self.notebookMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.panelSystem.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )
		
		sizerSystem = wx.BoxSizer( wx.VERTICAL )
		
		self.labelColour = wx.StaticText( self.panelSystem, wx.ID_ANY, u"Colour", wx.Point( -1,-1 ), wx.DefaultSize, 0 )
		self.labelColour.Wrap( -1 )
		sizerSystem.Add( self.labelColour, 0, wx.ALL, 5 )
		
		self.pickerBaseColour = wx.ColourPickerCtrl( self.panelSystem, wx.ID_ANY, wx.Colour( 0, 0, 0 ), wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
		self.pickerBaseColour.SetMinSize( wx.Size( 100,-1 ) )
		
		sizerSystem.Add( self.pickerBaseColour, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.checkMonitorTemp = wx.CheckBox( self.panelSystem, wx.ID_ANY, u"Set colour based on CPU temperature", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkMonitorTemp.SetToolTipString( u"Requires 'Open Hardware Monitor' to be running" )
		
		sizerSystem.Add( self.checkMonitorTemp, 0, wx.ALL, 5 )
		
		menuGradChoiceChoices = []
		self.menuGradChoice = wx.Choice( self.panelSystem, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, menuGradChoiceChoices, 0 )
		self.menuGradChoice.SetSelection( 0 )
		sizerSystem.Add( self.menuGradChoice, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_staticline1 = wx.StaticLine( self.panelSystem, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizerSystem.Add( self.m_staticline1, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.labelDynamicst3 = wx.StaticText( self.panelSystem, wx.ID_ANY, u"Dynamics", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelDynamicst3.Wrap( -1 )
		sizerSystem.Add( self.labelDynamicst3, 0, wx.ALL, 5 )
		
		self.checkMonitorLoad = wx.CheckBox( self.panelSystem, wx.ID_ANY, u"Pulse based on CPU load", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizerSystem.Add( self.checkMonitorLoad, 0, wx.ALL, 5 )
		
		self.m_staticline4 = wx.StaticLine( self.panelSystem, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		sizerSystem.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )
		
		sizerTemperature = wx.BoxSizer( wx.HORIZONTAL )
		
		sizerTmin = wx.BoxSizer( wx.VERTICAL )
		
		self.label_Tmin = wx.StaticText( self.panelSystem, wx.ID_ANY, u"Minimum T", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.label_Tmin.Wrap( -1 )
		sizerTmin.Add( self.label_Tmin, 0, wx.ALL, 5 )
		
		self.spinTmin = wx.SpinCtrl( self.panelSystem, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS|wx.TE_PROCESS_ENTER, 0, 100, 0 )
		sizerTmin.Add( self.spinTmin, 0, wx.ALL, 5 )
		
		
		sizerTemperature.Add( sizerTmin, 1, wx.EXPAND, 5 )
		
		sizerTmax = wx.BoxSizer( wx.VERTICAL )
		
		self.labelTmax = wx.StaticText( self.panelSystem, wx.ID_ANY, u"Maximum T", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelTmax.Wrap( -1 )
		sizerTmax.Add( self.labelTmax, 0, wx.ALL, 5 )
		
		self.spinTmax = wx.SpinCtrl( self.panelSystem, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS|wx.TE_PROCESS_ENTER, 0, 100, 0 )
		sizerTmax.Add( self.spinTmax, 0, wx.ALL, 5 )
		
		
		sizerTemperature.Add( sizerTmax, 1, wx.EXPAND, 5 )
		
		
		sizerSystem.Add( sizerTemperature, 1, wx.SHAPED, 5 )
		
		
		self.panelSystem.SetSizer( sizerSystem )
		self.panelSystem.Layout()
		sizerSystem.Fit( self.panelSystem )
		self.notebookMain.AddPage( self.panelSystem, u"System", False )
		self.panelRainbow = wx.Panel( self.notebookMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.panelRainbow.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOW ) )
		
		sizerRainbow = wx.BoxSizer( wx.VERTICAL )
		
		self.labelExtras = wx.StaticText( self.panelRainbow, wx.ID_ANY, u"Rainbow mode activated", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelExtras.Wrap( -1 )
		sizerRainbow.Add( self.labelExtras, 0, wx.ALL, 5 )
		
		
		self.panelRainbow.SetSizer( sizerRainbow )
		self.panelRainbow.Layout()
		sizerRainbow.Fit( self.panelRainbow )
		self.notebookMain.AddPage( self.panelRainbow, u"Rainbow", False )
		self.panelCinema = wx.Panel( self.notebookMain, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.panelCinema.SetBackgroundColour( wx.Colour( 255, 255, 255 ) )
		
		sizerCinema = wx.BoxSizer( wx.VERTICAL )
		
		self.labelContrast = wx.StaticText( self.panelCinema, wx.ID_ANY, u"Contrast", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelContrast.Wrap( -1 )
		sizerCinema.Add( self.labelContrast, 0, wx.ALL, 5 )
		
		self.sliderContrast = wx.Slider( self.panelCinema, wx.ID_ANY, 25, 1, 50, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		sizerCinema.Add( self.sliderContrast, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.labelBrightness = wx.StaticText( self.panelCinema, wx.ID_ANY, u"Brightness", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.labelBrightness.Wrap( -1 )
		sizerCinema.Add( self.labelBrightness, 0, wx.ALL, 5 )
		
		self.sliderBrightness = wx.Slider( self.panelCinema, wx.ID_ANY, 100, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL )
		sizerCinema.Add( self.sliderBrightness, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		self.panelCinema.SetSizer( sizerCinema )
		self.panelCinema.Layout()
		sizerCinema.Fit( self.panelCinema )
		self.notebookMain.AddPage( self.panelCinema, u"Cinema", True )
		
		sizerMain.Add( self.notebookMain, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( sizerMain )
		self.Layout()
		self.statusbarMain = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.Bind( wx.EVT_MENU, self.OnAbout, id = self.menuAbout.GetId() )
		self.Bind( wx.EVT_MENU, self.OnExit, id = self.menuExit.GetId() )
		self.notebookMain.Bind( wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onNotebookChange )
		self.pickerBaseColour.Bind( wx.EVT_COLOURPICKER_CHANGED, self.OnColourChange )
		self.checkMonitorTemp.Bind( wx.EVT_CHECKBOX, self.OnMonitorTempChange )
		self.menuGradChoice.Bind( wx.EVT_CHOICE, self.onGradChoice )
		self.checkMonitorLoad.Bind( wx.EVT_CHECKBOX, self.OnMonitorLoadChange )
		self.spinTmin.Bind( wx.EVT_SPINCTRL, self.onTchange )
		self.spinTmin.Bind( wx.EVT_TEXT_ENTER, self.onTchange )
		self.spinTmax.Bind( wx.EVT_SPINCTRL, self.onTchange )
		self.spinTmax.Bind( wx.EVT_TEXT_ENTER, self.onTchange )
		self.sliderContrast.Bind( wx.EVT_SCROLL, self.onContrastChange )
		self.sliderBrightness.Bind( wx.EVT_SCROLL, self.onBrightnessChange )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnAbout( self, event ):
		event.Skip()
	
	def OnExit( self, event ):
		event.Skip()
	
	def onNotebookChange( self, event ):
		event.Skip()
	
	def OnColourChange( self, event ):
		event.Skip()
	
	def OnMonitorTempChange( self, event ):
		event.Skip()
	
	def onGradChoice( self, event ):
		event.Skip()
	
	def OnMonitorLoadChange( self, event ):
		event.Skip()
	
	def onTchange( self, event ):
		event.Skip()
	
	
	
	
	def onContrastChange( self, event ):
		event.Skip()
	
	def onBrightnessChange( self, event ):
		event.Skip()
	

