#! /usr/bin/env python
#coding=utf-8

import douban.service
import gdata.service
import string,time,random
import utils,config

# denotes a recommendation
class RecEntry:
	def __init__(self, uid, id, title, pubdate, content):
		self.uid=uid
		self.id=id
		self.title=title
		self.pubdate=pubdate
		self.content=content
	
	def __getTuple(self):
		return (str(self.uid), self.id, self.pubdate, self.title, self.content)

	def getDic(self):
		return {'_id':self.id, 'uid':self.uid, 'title':self.title, 'date':self.pubdate, 'content':self.content}

	def __unicode__(self):
		return string.join(self.__getTuple(), '\n').decode('utf8')

	def __str__(self):
		return str(self.uid)+'\n'+self.id+'\n'+self.pubdate

# denote a user
class UsrEntry:
	def __init__(self, id, name):
		self.id=id
		self.name=name
	
	def __getTuple(self):
		return (str(self.id), self.name)

	def getDic(self):
		return {'_id':self.id, 'name':self.name}

	def __unicode__(self):
		return string.join(self.__getTuple(), '\n')

	def __str__(self):
		return str(self.id)+'\n'+self.name

# a collection
class CollecEntry:
	def __init__(self, uid, id, pubdate, status):
		self.uid=uid
		self.id=id
		self.pubdate=pubdate
		self.status=status

	def __getTuple(self):
		return (self.uid, self.id, self.pubdate, self.status)

	def __unicode__(self):
		return string.join(map(str, self.__getTuple()), u'\n').decode('utf8')

class RichUserEntry:
	def __init__(self, uid, tags, collections):
		self.uid=uid
		self.tags=tags
		self.collections=collections
	
	def __unicode__(self):
		dat=(str(self.uid)+'\n'+string.join(self.tags, '\n')+'\n').decode('utf8')
		for colls in self.collections:
			for coll in colls: dat+=unicode(coll)+'\n'
			dat+='#'*50+'\n'
		return dat.rstrip()

class DoubanAPI:

	def __init__(self, api_from=None, api_to=None):
		if api_from is None or api_to is None:
			api_from, api_to = 0, config.readInt('parms', 'apis')-1
		i=random.randint(api_from, api_to)
		API_KEY=config.readParm('keys', 'key'+str(i))
		SECRET=config.readParm('keys', 'sec'+str(i))
		self.client=douban.service.DoubanService(server='api.douban.com', api_key=API_KEY, secret=SECRET)
		print 'Using', i, '-th API: API_KEY =', API_KEY, 'SECRET =', SECRET

	def getRecs(self, uid, max_pages=5):
		rst=[]
		start=1
		while True:
			time.sleep(2)
			try:
				feed=self.client.GetRecommendations('/people/%d/recommendations' % uid, start, 50)
				for entry in feed.entry:
					rec=RecEntry(uid, entry.id.text, entry.title.text, entry.published.text, entry.content.text)
					rst.append(rec)
				if len(feed.entry)<45 or start>50*max_pages: break
				start+=50
			except gdata.service.RequestError:
				print 'Request Error! <recommendations>'
				break
			except Exception, e:
				print e
				break
		return rst

	def getContacts(self, uid):
		usrs=[]
		start=1
		while True:
			time.sleep(2)
			try:
				feed=self.client.GetContacts('/people/%d/contacts?start-index=%d&max-results=50' % (uid, start))
				for entry in feed.entry: 
					usr=UsrEntry(utils.getNums(entry.id.text)[-1], entry.uid.text)
					usrs.append(usr)
				total=int(feed.total_results.text)
				if start<total: start+=50
				else: break
			except gdata.service.RequestError:
				print 'Request Error! <recommendations>'
				break
			except Exception, e:
				print e
				break
		return usrs

	def getTags(self, uid):
		tags=['']*3
		for i,cat in enumerate(['movie', 'book', 'music']):
			time.sleep(2)
			try:
				feed=self.client.GetTagFeed('/people/%d/tags' % uid, cat, 1, 50)
				tags[i]=string.join(['%s(%s)' % (entry.title.text, entry.count.text) for entry in feed.entry], '\t')
			except gdata.service.RequestError:
				print 'Request Error! <tags>'
				break
			except Exception, e:
				print e
				break
		return tags

	def getCollections(self, uid, cat):
		colls=[]
		start=1
		while True:
			time.sleep(2)
			try:
				feed=self.client.GetCollectionFeed('/people/%d/collection' % uid, cat, start, 50)
				for entry in feed.entry: 
					eid=entry.subject.id.text
					pdate=entry.updated.text
					status=entry.status.text
					coll=CollecEntry(uid, eid, pdate, status)
					colls.append(coll)
				total=int(feed.total_results.text)
				if start<total and start<100: start+=50
				else: break
			except gdata.service.RequestError:
				print 'Request Error! <recommendations>'
				break
			except Exception, e:
				print e
				break
		return colls

	def getRichUser(self, uid):
		tags=self.getTags(uid)
		cols=[self.getCollections(uid, cat) for cat in ['movie', 'book', 'music']]
		return RichUserEntry(uid, tags, cols)

def test():
	api=DoubanAPI()
	recs=api.getRecs(1755725)
	print len(recs)
	#for rec in recs: print rec
	#usrs=api.getContacts(41953424)
	#print len(usrs)
	#tags=api.getTags(1573459)
	#colls=api.getCollections(1573459, 'music')
	#print len(colls)

if __name__=='__main__':
	test()

