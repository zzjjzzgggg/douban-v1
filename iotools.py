#! /usr/bin/env python
#encoding: utf-8

from datetime import datetime

class FileIO:
	def __init__(self, fname, sep='\t', echo=False, comment='#'):
		print 'Loading file', fname
		self.fname=fname
		self.sep=sep
		self.echo=echo
		self.comment=comment
		self.cnt=0
		self.fr=open(fname)
	
	def next(self):
		while True:
			self.l=self.fr.readline()
			if not self.l or self.l.strip()[0]!=self.comment: break
		if not self.l: 
			self.fr.close()
			print 'Totally',self.cnt, 'lines.'
		else:
			self.cnt+=1
			if self.echo and self.cnt%1E6==0: print 'Loaded lines = %d' % self.cnt 
			self.items=self.l.rstrip().split(self.sep)
		return bool(self.l)

	def getLine(self):
		return self.l
	
	def getItems(self):
		return self.items
	
	def getItemsCnt(self):
		return len(self.items)

	def reset(self):
		if self.fr: self.fr.close()
		self.fr=open(self.fname)

	def getStr(self, i):
		return self.items[i]
	
	def getInt(self, i):
		return int(self.items[i])
	
	def getInts(self):
		return map(int, self.items)
	
	def getFlt(self, i):
		return float(self.items[i])
	
	def getFlts(self):
		return map(float, self.items)

	def getTime(self, i):
		try:
			return datetime.strptime(self.items[i], '%Y-%m-%d %H:%M:%S')
		except:
			return None

	def getISOTime(self, i):
		try:
			return datetime.strptime(self.items[i][:19], '%Y-%m-%dT%H:%M:%S')
		except:
			return None
	
	def getLineNO(self):
		return self.cnt
		
def loadList(fname, col=True, sep=','):
	f=open(fname)
	l=f.readline()
	while l and l[0]=='#': l=f.readline()
	if not l: return []
	if col:
		rst=[]
		while l:
			rst.append(l.strip())
			l=f.readline()
	else: rst=l.split(sep)
	f.close()
	return rst

def loadInts(fname, col=True, sep=','):
	return map(int, loadList(fname, col, sep))

def loadFlts(fname, col=True, sep=','):
	return map(float, loadList(fname, col, sep))

def saveIntList(slist, fnm, anno=None):
	saveStrList(map(str, slist), fnm, anno)

def saveStrList(slist, fnm, anno=None):
	fw=open(fnm, 'w')
	fw.write('#file: '+fnm+'\n')
	if anno is not None: fw.write(anno.strip()+'\n')
	fw.write('\n'.join(slist))
	fw.close()

def saveIntMap(tmap, fnm, anno=None):
	fw=open(fnm, 'w')
	fw.write('#file: '+fnm+'\n')
	if anno is not None: fw.write(anno.strip()+'\n')
	for k in tmap: fw.write('%d\t%d\n' % (k, tmap[k]))
	fw.close()

def saveStrIntMap(tmap, fnm, anno=None):
	fw=open(fnm, 'w')
	fw.write('#file: '+fnm+'\n')
	if anno is not None: fw.write(anno.strip()+'\n')
	for k in tmap: fw.write('%s\t%d\n' % (k, tmap[k]))
	fw.close()

def saveIntStrMap(tmap, fnm, anno=None):
	fw=open(fnm, 'w')
	fw.write('#file: '+fnm+'\n')
	if anno is not None: fw.write(anno.strip()+'\n')
	for k in tmap: fw.write('%d\t%s\n' % (k, tmap[k]))
	fw.close()

def loadIntMap(fnm):
	rst={}
	fio=FileIO(fnm, echo=False)
	while fio.next(): rst[fio.getInt(0)]=fio.getInt(1)
	return rst

def loadStrIntMap(fnm, cols=0, coli=1):
	rst={}
	fio=FileIO(fnm, echo=False)
	while fio.next(): rst[fio.getStr(cols)]=fio.getInt(coli)
	return rst

def loadIntStrMap(fnm, coli=0, cols=1):
	rst={}
	fio=FileIO(fnm, echo=False)
	while fio.next(): rst[fio.getInt(coli)]=fio.getStr(cols)
	return rst


