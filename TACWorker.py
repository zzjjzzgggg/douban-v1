#coding: utf-8

import threading
import Queue,time
import dao,api
from mysampler import *
from FileStorer import *

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

class ProducerS1(threading.Thread):
	def __init__(self, qu):
		threading.Thread.__init__(self)
		self.daemon=True
		self.qu=qu
		self.stop=False
		self.sampler=MySampler()
		self.sampler.initS1()
		self.storer=FileStorer('S1')
	
	def stopWorking(self):
		self.stop=True
		self.storer.close()

	def run(self):
		while not self.stop:
			uids=self.sampler.sampleS1()
			if uids is None: continue
			self.storer.savePair(uids)
			if not dao.isSampled(uids[0]): self.qu.put(uids[0])
			if not dao.isSampled(uids[1]): self.qu.put(uids[1])
		print 'Producer stopped.'

class ProducerS2(threading.Thread):
	def __init__(self, qu):
		threading.Thread.__init__(self)
		self.daemon=True
		self.qu=qu
		self.stop=False
		self.sampler=MySampler()
		self.sampler.initS2()
		self.storer=FileStorer('S2')
	
	def stopWorking(self):
		self.stop=True
		self.storer.close()

	def run(self):
		while not self.stop:
			uids=self.sampler.sampleS2()
			if uids is None: continue
			self.storer.savePair(uids)
			if not dao.isSampled(uids[0]): self.qu.put(uids[0])
			if not dao.isSampled(uids[1]): self.qu.put(uids[1])
		print 'Producer stopped.'

class TACHarvestor(threading.Thread):
	def __init__(self, uidQu, usrQu):
		threading.Thread.__init__(self)
		self.daemon=True
		self.uidQu=uidQu
		self.usrQu=usrQu

	def run(self):
		n=0
		while True:
			if n%100==0: dapi=api.DoubanAPI()
			uid=self.uidQu.get()
			self.uidQu.task_done()
			self.usrQu.put(dapi.getRichUser(uid))
			dao.markAsSampled(uid)
			n+=1

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
			dat=[q.qsize() for q in self.qus]
			print 'Qsize:', dat


