#!/usr/bin/env python2

# Copyright (c) 2013 dangbinghoo <dangbinghoo@gmail.com>
# All rights reserved.
#
# License: BSD

import os
import re
import array

from PyQt4 import QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from EdViewSci import EditorView

# code context view
class ContextEditorView(EditorView):
	sig_dblclick = pyqtSignal()

	def __init__(self, parent = None):
		EditorView.__init__(self, parent)

		self.setCaretLineBackgroundColor(QtGui.QColor("#ffaa7f"))
		
	def mouseReleaseEvent(self, ev):
		super(EditorView, self).mouseReleaseEvent(ev)
		
	def mousePressEvent(self, ev):
		pass
	
	def keyPressEvent(self, ev):
		pass
	
	def contextMenuEvent(self, ev):
		pass
	
	def mouseDoubleClickEvent(self, ev):
		self.sig_dblclick.emit()

	def show_file_line(self, fname, line):
		self.open_file(fname)
		self.goto_line(int(line))
		self.show()

class codeResultView(QTextBrowser):
	sig_result_view_openfile = pyqtSignal(str, int)
	def __init__(self, parent = None):
		QTextBrowser.__init__(self)
		self.setReadOnly(True)
		
	def showResultList(self, sym, res):
		self.res = res
		richstr = '<div align="center">'
		richstr += '<span style="font-size:10px;color:#990000;">Query of &lt; <strong><span style="color:#000099;">'
		richstr += str(sym)
		richstr += '</span></strong></span> <span style="font-size:10px;color:#990000;"> &gt; list</span>'
		richstr += '<div align="left" style="line-height:2px">'
		richstr += '<hr />'
		for itm in res:
			filename = itm[1]
			linenum = itm[2]
			context = itm[3]
			richstr += 'Line <span style="font-size:10px;color:#6600CC;">'
			richstr += str(linenum)
			richstr += '</span> of <em><a href="'
			richstr += str(filename)
			richstr += '#'
			richstr += str(linenum)
			richstr += '">'
			richstr += str(filename)
			richstr += '</a>'
			richstr += '</span></span></em>'
			richstr += '<pre style="line-height:0px"><span style="font-size:10px;color:#006600;line-height:2px;">'
			richstr += str(context)
			richstr += '</span></pre>'
		richstr += '</div></div>'
		#print richstr
		self.setHtml(richstr)
		self.setReadOnly(True)
		self.anchorClicked.connect(self.anchorClicked_ev)
		
	def anchorClicked_ev(self, qurl):
		urlstr = qurl.toString()
		urlinfo = urlstr.split('#')
		fname = str(urlinfo[0])
		linen = int(urlinfo[1])
		self.sig_result_view_openfile.emit(fname, int(linen))
	
	#
	# NOTE: Don't remove this!
	# overload this method to prevent anchor-click reload the source file.
	def setSource(self, qurl):
		pass

# contextView Page
class CodeContextViewPage(QFrame):
	def __init__(self, parent = None):
		QFrame.__init__(self)
		self.vlay = QVBoxLayout()

		self.cv_filetitle = QLabel()
		self.cv = ContextEditorView()
		self.resv = codeResultView()
		self.vlay.addWidget(self.cv_filetitle)
		self.vlay.addWidget(self.cv)
		self.vlay.addWidget(self.resv)
		#self.setSizes([1,1,1])
		self.resv.show()
		self.cv.hide()
		self.cv_filetitle.hide()

		self.setLayout(self.vlay)

	def showFileView(self, fname, line, sym, font):
		self.filename = fname
		self.linenum = line
		t = '%s:%s   %s' % (fname, line, sym)
		self.cv_filetitle.setText(t)
		self.cv_filetitle.show()

		cv = self.cv
		cv.set_lexer(fname)
		cv.set_font(font)
		cv.show_line_number_cb(True)
		cv.show_file_line(fname, line)
		cv.show()

# ContextView Manager
class CodeContextViewManager(CodeContextViewPage):
	sig_codecontext_showfile = pyqtSignal(str, int)
	def __init__(self):
		CodeContextViewPage.__init__(self)
		self.cur_query = ''
		self.cvp_cv_openedFile = False
		self.cv_font = "Monospace,9,-1,5,50,0,0,0,0,0"

		self.cv.sig_dblclick.connect(self.contextViewPage_openfile)
		self.resv.sig_result_view_openfile.connect(self.resultViewPage_openfile)
	
	def is_new_query(self, text):
		if self.cur_query == text:
			return False
		self.cur_query = text
		return True

	def showResult(self, sym, res):
		#if sym != self.cur_query:
		#	return
		
		#self.cv.clear()
			
		# if queried one, show the file, or, list results.
		if (len(res) == 1):
			self.resv.hide()
			itm = res[0]
			self.showFileView(itm[1], itm[2], sym, self.cv_font)
			self.cvp_cv_openedFile = True
		else:
			self.cv.hide()
			self.cv_filetitle.hide()
			self.resv.showResultList(sym, res)
			self.resv.show()
	
	def contextViewPage_openfile(self):
		self.sig_codecontext_showfile.emit(self.filename, int(self.linenum))
	
	def resultViewPage_openfile(self, filename, line):
		self.sig_codecontext_showfile.emit(filename, int(line))
			
	def clear(self):
		print 'calling clear ....'
		self.cv_filetitle.clear()
		self.resv.clear()
		self.cv.clear()
		#self.cvp.cv.hide()
