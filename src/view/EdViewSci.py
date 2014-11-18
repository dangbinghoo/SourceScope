#!/usr/bin/env python2

# Copyright (c) 2010 Anil Kumar
# All rights reserved.
#
# License: BSD 

import os
import re
import array

from PyQt4 import QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

try:
	from PyQt4.Qsci import QsciScintilla, QsciScintillaBase
	from PyQt4.Qsci import QsciLexerCPP, QsciLexerJava
	from PyQt4.Qsci import QsciLexerPython, QsciLexerRuby
	from PyQt4.Qsci import QsciLexerBash, QsciLexerDiff, QsciLexerMakefile
	from PyQt4.Qsci import QsciLexerLua, QsciLexerSQL, QsciLexerTCL, QsciLexerTeX
	from PyQt4.Qsci import QsciLexerHTML, QsciLexerCSS
	from PyQt4.Qsci import QsciLexerPerl, QsciLexerVHDL

	suffix_to_lexer = [
		[['c', 'h', 'cpp', 'hpp', 'cc', 'hh', 'cxx', 'hxx', 'C', 'H', 'h++'], QsciLexerCPP],
		[['java'], QsciLexerJava],
		[['py', 'pyx', 'pxd', 'pxi', 'scons'], QsciLexerPython],
		[['rb', 'ruby'], QsciLexerRuby],
		[['sh', 'bash'], QsciLexerBash],
		[['diff', 'patch'], QsciLexerDiff],
		[['mak', 'mk'], QsciLexerMakefile],
		[['lua'], QsciLexerLua],
		[['sql'], QsciLexerSQL],
		[['tcl', 'tk', 'wish', 'itcl'], QsciLexerTCL],
		[['tex'], QsciLexerTeX],
		[['htm', 'html'], QsciLexerHTML],
		[['css'], QsciLexerCSS],
		[['pl', 'perl'], QsciLexerPerl],
		[['vhdl', 'vhd'], QsciLexerVHDL],
	]
	filename_to_lexer = [
		[['Makefile', 'makefile', 'Makefile.am', 'makefile.am', 'Makefile.in', 'makefile.in'], QsciLexerMakefile],
	]

	seascope_editor_tab_width = None
	try:
		seascope_editor_tab_width = int(os.getenv('SEASCOPE_EDITOR_TAB_WIDTH'))
	except:
		pass

except ImportError as e:
	print e
	print "Error: required qscintilla-python package not found"
	raise ImportError

import DialogManager
from FileContextView import *

class EditorViewBase(QsciScintilla):
	def __init__(self, parent=None):
		QsciScintilla.__init__(self, parent)
		self.font = None
		self.lexer = None

	def set_font(self, font):
		if not font:
			return
		if not self.font:
			self.font = QtGui.QFont()
		self.font.fromString(font)

		# the font metrics here will help
		# building the margin width later
		self.fm = QtGui.QFontMetrics(self.font)

		## set the default font of the editor
		## and take the same font for line numbers
		self.setFont(self.font)
		self.setMarginsFont(self.font)

		self.lexer.setFont(self.font,-1)
		self.setLexer(self.lexer)

	def lpropChanged(self, prop, val):
		print 'lpropChanged', prop, val

	def setProperty(self, name, val):
		name_buff = array.array('c', name + "\0")
		val_buff = array.array("c", str(val) + "\0")
		address_name_buffer = name_buff.buffer_info()[0]
		address_val_buffer = val_buff.buffer_info()[0]
		self.SendScintilla(QsciScintillaBase.SCI_SETPROPERTY, address_name_buffer, address_val_buffer)

	def getProperty(self, name):
		name_buff = array.array('c', name + "\0")
		val_buff = array.array("c", str(0) + "\0")
		address_name_buffer = name_buff.buffer_info()[0]
		address_val_buffer = val_buff.buffer_info()[0]
		self.SendScintilla(QsciScintillaBase.SCI_GETPROPERTY, address_name_buffer, address_val_buffer)
		return ''.join(val_buff)

	def printPropertyAll(self):
		sz = self.SendScintilla(QsciScintillaBase.SCI_PROPERTYNAMES, 0, 0)
		if not sz:
			return
		val_buff = array.array("c", (' ' * sz) + "\0")
		address_val_buffer = val_buff.buffer_info()[0]
		self.SendScintilla(QsciScintillaBase.SCI_PROPERTYNAMES, 0, address_val_buffer)
		print '###>'
		for p in ''.join(val_buff).splitlines():
			v = self.getProperty(p)
			print '    %s = %s' % (p, v)

	def lexer_for_file(self, filename):
		(prefix, ext) = os.path.splitext(filename)
		for (el, lxr) in suffix_to_lexer:
			if ext in el:
				return lxr
		for (el, lxr) in filename_to_lexer:
			if filename in el:
				return lxr
		return QsciLexerCPP

	def set_lexer(self, filename):
		if not self.lexer:
			lexerClass = self.lexer_for_file(filename)
			self.lexer = lexerClass()
			self.setLexer(self.lexer)
			self.setProperty("lexer.cpp.track.preprocessor", "0")
			is_debug = os.getenv("SEASCOPE_QSCI_LEXER_DEBUG", 0)
			if is_debug:
				self.lexer.propertyChanged.connect(self.lpropChanged)
				self.printPropertyAll()


class EditorView(EditorViewBase):
	ev_popup = None
	sig_text_selected = pyqtSignal(str)
	def __init__(self, parent=None):
		EditorViewBase.__init__(self, parent)
		#self.setGeometry(300, 300, 400, 300)

		## Editing line color
		self.setCaretLineVisible(True)
		self.setCaretLineBackgroundColor(QtGui.QColor("#d4feff")) # orig: EEF6FF
		#self.setCaretWidth(2)

		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

		self.codemark_marker = self.markerDefine(self.Circle)

	def get_filename(self):
		return self.filename

	def ed_settings_1(self):
		## Margins colors
		# line numbers margin
		self.setMarginsBackgroundColor(QtGui.QColor("#333333"))
		self.setMarginsForegroundColor(QtGui.QColor("#CCCCCC"))

		# folding margin colors (foreground,background)
		self.setFoldMarginColors(QtGui.QColor("#888888"),QtGui.QColor("#eeeeee"))

		## Edge Mode shows a red vetical bar at 80 chars
		self.setEdgeMode(QsciScintilla.EdgeLine)
		self.setEdgeColumn(80)
		self.setEdgeColor(QtGui.QColor("#FF0000"))

		## Editing line color
		self.setCaretLineVisible(True)
		self.setCaretLineBackgroundColor(QtGui.QColor("#CDA869"))

		## set tab width
		if seascope_editor_tab_width:
			self.setTabWidth(seascope_editor_tab_width)

	def show_line_number_cb(self, val):
		if (val):
			width = self.fm.width( "00000" ) + 5
		else:
			width = 0

		self.setMarginWidth(0, width)
		self.setMarginLineNumbers(0, val)

	def show_folds_cb(self, val):
		if val:
			#self.setMarginsForegroundColor( QtGui.QColor("#404040") )
			#self.setMarginsBackgroundColor( QtGui.QColor("#888888") )

			## Folding visual : we will use circled tree fold
			self.setFolding(QsciScintilla.CircledTreeFoldStyle)
		else:
			self.setFolding(QsciScintilla.NoFoldStyle)
			self.clearFolds()

	def toggle_folds_cb(self):
		self.foldAll()
		
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
			self.setCursorPosition(val, 0)

	def open_file_begin(self, filename):
		self.filename = filename

		## Choose a lexer
		self.set_lexer(filename)

		## Braces matching
		self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

		## Render on screen
		self.show()

	def open_file_end(self):
		self.show()
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		#self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setFocus()

	def open_file(self, filename):
		self.open_file_begin(filename)

		## Show this file in the editor
		self.setText(open(filename).read())
		
		## Mark read-only
		self.setReadOnly(True)

		self.open_file_end()

	def refresh_file(self, filename):
		assert filename == self.filename
		pos = self.getCursorPosition()
		self.open_file(filename)
		self.setCursorPosition(*pos)
		self.cursorPositionChanged.emit(*pos)

	def goto_line(self, line):
		line = line - 1
		self.setCursorPosition(line, 0)

		self.ensureLineVisible(line)
		self.setFocus()

	def contextMenuEvent(self, ev):
		if not EditorView.ev_popup:
			return
		f = EditorView.ev_popup.font()
		EditorView.ev_popup.setFont(QFont("San Serif", 8))
		EditorView.ev_popup.exec_(QCursor.pos())
		EditorView.ev_popup.setFont(f)
		
	def mouseReleaseEvent(self, ev):
		super(EditorView, self).mouseReleaseEvent(ev)
		if(self.hasSelectedText()):
			self.query_text = self.selectedText()
			#print 'selectedText ----', self.query_text
			self.sig_text_selected.emit(self.query_text)


