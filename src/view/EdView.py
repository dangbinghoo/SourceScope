#!/usr/bin/env python2

# Copyright (c) 2014 Binghoo Dang <dangbinghoo@gmail.com>
# All rights reserved.
#
# License: BSD 

import os
import re
import array

from PyQt4 import QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

#
# Loading ktexteditor.
#
try:
	from PyKDE4.ktexteditor import *
	from PyKDE4.kdecore import KGlobal, KUrl, i18n
	
	from PyKDE4.kdecore import *
	from PyKDE4.kdeui import *
	from PyKDE4.kparts import *

	seascope_editor_tab_width = None
	try:
		seascope_editor_tab_width = int(os.getenv('SEASCOPE_EDITOR_TAB_WIDTH'))
	except:
		pass

except ImportError as e:
	print e
	print "Error: required PyKDE4/ktexteditor package not found"
	print " try to install kde4 python bindings and try again."
	raise ImportError


class EditorViewBase(QSplitter):
	def __init__(self, parent=None):
		QSplitter.__init__(self)
		#self.__editor = KTextEditor.EditorChooser.editor()
		#self.doc = self.__editor.createDocument(self)
		#self.edit = self.doc.createView(self)
		
		
		#self.confIF.setConfigValue(self, "line-number", True)
		
		#self.confIF.setConfigValue(self.edit, "line-number", true)
		
		factory = KLibLoader.self().factory("katepart")
		self.doc = factory.create(self, "KatePart")
		self.edit = self.doc.widget()
		#self.confIF = super(KTextEditor.ConfigInterface, self.edit)
		self.addWidget(self.edit)


		#self.__editor.configDialog(self)

class EditorView(EditorViewBase):
	sig_text_selected = pyqtSignal(str)
	cursorPositionChanged = pyqtSignal(int, int)
	def __init__(self, parent=None):
		EditorViewBase.__init__(self, parent)
		self.edit.cursorPositionChanged.connect(self.onCursorPosChanged)
		self.edit.selectionChanged.connect(self.onSelectionChanged) 

	def get_filename(self):
		return self.filename

	def show_line_number_cb(self, showln):
		if (showln):
			print 'show line number'
		else:
			print 'not show line number'

	def show_folds_cb(self, enablefolds):
		if enablefolds:
			print 'enable folds'
		else:
			print 'disable folds'

	def toggle_folds_cb(self):
		print 'all folds open up.'
		

	def open_file(self, filename):
		self.fileurl = "file://"
		self.fileurl += filename
		self.doc.openUrl(KUrl(self.fileurl))
		self.filename = filename    
		self.edit.setFocus()
		
	def refresh_file(self, filename):
		self.open_file(self, filename)

	def goto_line(self, nline):
		if nline ==  0:
			line = 1
			
		line = nline - 1
		self.edit.setCursorPosition(KTextEditor.Cursor(line, 0))
	
	#
	# Context view event.
	#
	def onSelectionChanged(self, view):
		if(self.hasSelectedText()):
			self.query_text = self.selectedText()
			#print 'selectedText ----', self.query_text
			self.sig_text_selected.emit(self.query_text)
				
	def getCursorPosition(self):
		return (self.edit.cursorPositionVirtual().line() + 1, 
	           self.edit.cursorPositionVirtual().column() + 1)
	           
	def setCursorPos(self, line, column):
		if line == 0 :
			nline = line
		else:
			nline = line - 1	
		if column == 0 :
			ncolumn = column
		else :
			ncolumn = column - 1 
		self.edit.setCursorPosition(KTextEditor.Cursor(nline, ncolumn))
		
	def selectedText(self):
		return self.edit.selectionText()
		
	def hasSelectedText(self):
		return self.edit.selection()
	
	def text(self, line):
		if line > 0 :
			nline = line - 1
		else:
			nline = line
		return self.doc.line(nline)
	
	def lines(self):
		return self.doc.lines()
    
	def codemark_add(self, line):
		self.markerAdd(line, self.codemark_marker)

	def codemark_del(self, line):
		self.markerDelete(line, self.codemark_marker)

	def goto_marker(self, is_next):
		(eline, inx) = self.getCursorPosition()
		if is_next:
			val = self.markerFindNext(eline + 1, -1)
		else:
			val = self.markerFindPrevious(eline - 1, -1)
		if val >= 0:
			self.setCursorPosition(val - 1, 0)
	
	def isWordCharacter(self, line):
		print 'is word isWordCharacter '
		
	def onCursorPosChanged(self, view):
		cursor = view.cursorPositionVirtual()
		self.cursorPositionChanged.emit(cursor.line() + 1, cursor.column() + 1)
		
	def isModified(self):
		return self.doc.isModified()

