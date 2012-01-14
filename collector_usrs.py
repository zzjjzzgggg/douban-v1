#! /usr/bin/env python
#coding=utf-8

from api import *
import config
import time,sys,codecs

def process(api_from, api_to, cur_task):
	f=open('usrs-%d.txt' % cur_task)
	uids=map(int, f.readlines())
	f.close()
	fw=codecs.open('rsts-%d.txt' % cur_task, 'w', 'utf8')
	for i,uid in enumerate(uids):
		if i%50==0: douban=DoubanAPI(api_from, api_to)
		print time.ctime(), 'processing', i, uid
		recs=douban.getRecs(uid)
		print 'recs:', len(recs)
		for rec in recs: fw.write(unicode(rec)+'\n')
	fw.close()

if __name__=='__main__':
	if len(sys.argv)<2: 
		print 'Usage: python', __file__, 'fid'
		sys.exit(0)
	cur_task=int(sys.argv[1])
	process(0, 50, cur_task)
