#coding: utf-8

import threading
import Queue,time
import dao,api

class Producer(threading.Thread):
	def __init__(self, qu):
		threading.Thread.__init__(self)
		self.daemon=True
		self.qu=qu
		self.stop=False
	
	def stopWorking(self):
		self.stop=True

	def run(self):
		while not self.stop:
			uid=dao.swr()
			self.qu.put(uid)
		print 'Producer stopped.'

class TACHarvestor(threading.Thread):
	def __init__(self, uidQu, usrQu):
		threading.Thread.__init__(self)
		self.daemon=True
		self.uidQu=uidQu
		self.usrQu=usrQu

	def run(self):
		dapi=api.DoubanAPI()
		while True:
			uid=self.uidQu.get()
			self.uidQu.task_done()
			self.usrQu.put(dapi.getRichUser(uid))

class Storer(threading.Thread):
	def __init__(self, qu, fstorer):
		threading.Thread.__init__(self)
		self.daemon=True
		self.queue=qu
		self.fstorer=fstorer

	def run(self):
		while True:	
			item=self.queue.get()
			self.fstorer.save(item)
			self.queue.task_done()
	
class MyMonitor(threading.Thread):
	def __init__(self, qus):
		threading.Thread.__init__(self)
		self.daemon=True
		self.qus=qus
	
	def run(self):
		while True:
			time.sleep(7)
			for q in self.qus: print q.qsize()


