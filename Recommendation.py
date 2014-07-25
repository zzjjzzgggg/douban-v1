#! /usr/bin/env python
#coding=utf-8

from api import *
import dao
import time,sys

def process(api_from, api_to, total_tasks, cur_task):
	while True:
		douban=DoubanAPI(api_from, api_to)
		uids=dao.getUids(50, total_tasks, cur_task)
		if len(uids)==0: break
		for i,uid in enumerate(uids):
			print time.ctime(), 'processing', i, uid
			recs=douban.getRecs(uid)
			dao.saveRecs(uid, recs)
			conts=douban.getContacts(uid)
			dao.saveContacts(uid, conts)
			print 'recs:', len(recs), 'conts', len(conts)
		dao.delete(uids)

if __name__=='__main__':
	if len(sys.argv)<3: 
		print 'Usage: python', __file__, 'total_tasks cur_task'
		sys.exit(0)
	total_tasks=int(sys.argv[1])
	cur_task=int(sys.argv[2])
	total_api=config.readInt('parms', 'apis')
	part_len=total_api/total_tasks
	api_from=cur_task*part_len
	api_to=api_from+part_len-1
	print 'Total:',total_tasks,'Task:', cur_task, 'API_from', api_from, 'API_to', api_to
	process(api_from, api_to, total_tasks, cur_task)
