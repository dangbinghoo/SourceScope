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
	from PyKDE4 import ktexteditor
	from PyKDE4.kdecore import KGlobal, KUrl, i18n

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


class EditorViewBase(QWidget):
	def __init__(self, parent=None):
		QWidget.__init__(self)
		self.__editor = ktexteditor.KTextEditor.EditorChooser.editor() 
		self.edconfig = self.__editor.readConfig()
		self.doc = self.__editor.createDocument(self)
		self.edit = self.doc.createView(self)
		

class EditorView(EditorViewBase):
	ev_popup = None
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
		
	def codemark_add(self, line):
		print 'add code mark with line'
		print line

	def codemark_del(self, line):
		print 'del code mark with line'
		print line

	def goto_marker(self, is_next):
		if is_next:
			print 'find marker next'
		else:
			print 'find marker prev'

	def open_file(self, filename):
		self.fileurl = "file://"
		self.fileurl += filename
		self.doc.openUrl(KUrl(self.fileurl))
		self.filename = filename
		self.edit.resize(900, 500)
		self.edit.setFocus()
		

	def refresh_file(self, filename):
		self.open_file(self, filename)

	def goto_line(self, nline):
		if nline ==  0:
			line = 1
			
		line = nline - 1
		self.edit.setCursorPosition(ktexteditor.KTextEditor.Cursor(line, 0))

	def contextMenuEvent(self, ev):
		if not EditorView.ev_popup:
			return
		f = EditorView.ev_popup.font()
		EditorView.ev_popup.setFont(QFont("San Serif", 8))
		EditorView.ev_popup.exec_(QCursor.pos())
		EditorView.ev_popup.setFont(f)
	
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
		setCursorPosition(ktexteditor.KTextEditor.Cursor(nline, ncolumn))
		
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
		
