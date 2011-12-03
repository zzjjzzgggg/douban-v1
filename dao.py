#encoding: utf-8

import pymongo
import time

db=pymongo.Connection('192.168.4.238').douban

def getUids(n,total,part):
	return [item['_id'] for item in db.to_visit.find({'_id':{'$mod':[total,part]}}, limit=n).sort('t', pymongo.ASCENDING)]

def delete(uids):
	for uid in uids: db.to_visit.remove(uid)

def remove(uid):
	db.to_visit.remove(uid)

def saveUsr(usr):
	db.visited.insert(usr.getDic())

def saveRecs(uid, recs):
	db.visited.update({'_id':uid}, {'$set':{'rec':[rec.getDic() for rec in recs]}})

def saveContacts(uid, conts):
	uids=[]
	for usr in conts: 
		saveUsr(usr)
		if db.visited.find_one({'_id':usr.id, 'rec':{'$exists':True}}) is None:
			db.to_visit.insert({'_id':usr.id,'t':int(time.time())})
		uids.append(usr.id)
	db.visited.update({'_id':uid}, {'$set':{'f':uids}})

def test():
	print getUids(2)
	delete([1])

if __name__=='__main__':
	test()
