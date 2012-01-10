#! /usr/bin/env python
#coding=utf-8

from api import *
import config
import time,sys,codecs

def process(api_from, api_to, total_tasks, cur_task):
	f=open('usrs-%d.txt' % cur_task)
	uids=map(int, f.readlines())
	f.close()
	fw=codecs.open('rsts-%d.txt' % cur_task, 'w', 'utf8')
	for i,uid in enumerate(uids):
		if i%100==0: douban=DoubanAPI(api_from, api_to)
		print time.ctime(), 'processing', i, uid
		recs=douban.getRecs(uid)
		print 'recs:', len(recs)
		for rec in recs: fw.write(unicode(rec)+'\n')
	fw.close()

if __name__=='__main__':
	if len(sys.argv)<3: 
		print 'Usage: python', __file__, 'total fid'
		sys.exit(0)
	total_tasks=int(sys.argv[1])
	cur_task=int(sys.argv[2])
	total_api=config.readInt('parms', 'apis')
	part_len=total_api/total_tasks
	api_from=cur_task*part_len
	api_to=api_from+part_len-1
	print 'Total:',total_tasks,'Task:', cur_task, 'API_from', api_from, 'API_to', api_to
	process(api_from, api_to, total_tasks, cur_task)
