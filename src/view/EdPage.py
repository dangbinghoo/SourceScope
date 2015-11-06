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

from FileContextView import *
from EdView import EditorView

class EditorPage(QSplitter):
	def __init__(self, parent=None):
		QSplitter.__init__(self)
		self.fcv = FileContextView(self)
		self.ev = self.new_editor_view()
		self.addWidget(self.fcv)
		self.addWidget(self.ev)
		# taglist and edit view.
		self.setSizes([1, 650])

		self.ev.cursorPositionChanged.connect(self.fcv.sig_ed_cursor_changed)
		self.fcv.sig_goto_line.connect(self.ev.goto_line)

	def new_editor_view(self):
		return EditorView(self)

	def open_file(self, filename):
		self.ev.open_file(filename)
		self.fcv.run(filename)

	def refresh_file(self):
		filename = self.get_filename()
		self.fcv.rerun(filename)
		self.ev.refresh_file(filename)

	def get_filename(self):
		return self.ev.get_filename() 
