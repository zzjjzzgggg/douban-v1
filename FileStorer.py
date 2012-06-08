#! /usr/bin/env python
#coding=utf-8

import codecs
import os, time

class FileStorer:
	def __init__(self, prefix='', data_dir='data/'):
		self.fw=None
		self.fw_pair=None
		self.wtd=0
		self.wtd_pair=0
		self.data_dir=data_dir
		if not os.path.exists(data_dir): os.mkdir(data_dir)
		self.prefix=prefix
	
	def save(self, item):
		if self.wtd>=10000 and self.fw is not None: 
			self.fw.close()
			self.fw=None
		if self.fw is None:
			self.fw=codecs.open(self.data_dir+'TAC_%d.txt' % int(time.time()), 'w', 'utf-8')
			self.wtd=0
		self.fw.write(unicode(item)+'\n')
		self.wtd+=1
	
	def savePair(self, item):
		if self.wtd_pair>=10000 and self.fw_pair is not None: 
			self.fw_pair.close()
			self.fw_pair=None
		if self.fw_pair is None:
			self.fw_pair=codecs.open(self.data_dir+self.prefix+'_%d.txt' % int(time.time()), 'w', 'utf-8')
			self.wtd_pair=0
		self.fw_pair.write(unicode(item)+'\n')
		self.wtd_pair+=1
	
	def close(self):
		if self.fw is not None: self.fw.close()
		if self.fw_pair is not None: self.fw_pair.close()
