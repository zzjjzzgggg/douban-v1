#! /usr/bin/env python
#coding=utf-8

import config
from TACWorker import *
from FileStorer import *


def process():
	uidQueue=Queue.Queue(50)
	ufoQueue=Queue.Queue(20)

	# producer is ready
	producer=ProducerS2_(uidQueue)
	producer.start()
	time.sleep(2)
	
	# storer is ready
	fstorer=FileStorer()
	storer=Storer(ufoQueue, fstorer)
	storer.start()

	# monitor is ready
	monitor=MyMonitor([uidQueue, ufoQueue])
	monitor.start()

	while True:
		ch=raw_input()[0]
		if ch=='q':
			producer.stopWorking()
			break

	uidQueue.join()
	ufoQueue.join()
	time.sleep(5)
	fstorer.close()
	
if __name__=='__main__':
	process()
