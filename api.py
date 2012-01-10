#! /usr/bin/env python
#coding=utf-8

import douban.service
import gdata.service
import string,time,random
import utils,config


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

class DoubanAPI:
	def __init__(self, api_from=0, api_to=4):
		i=random.randint(api_from, api_to)
		API_KEY=config.readParm('keys', 'key'+str(i))
		SECRET=config.readParm('keys', 'sec'+str(i))
		self.client=douban.service.DoubanService(server='api.douban.com', api_key=API_KEY, secret=SECRET)
		print 'Using',i,'-th API: \nAPI_KEY=', API_KEY, '\nSECRET=', SECRET

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
				if len(feed.entry)!=50 or start>50*max_pages: break
				start+=50
			except gdata.service.RequestError:
				print 'Request Error! <recommendations>'
			except Exception, e:
				print e
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

def test():
	api=DoubanAPI()
	recs=api.getRecs(43793218)
	print len(recs)
	#for rec in recs: print rec
	#usrs=api.getContacts(41953424)
	#print len(usrs)

if __name__=='__main__':
	test()

