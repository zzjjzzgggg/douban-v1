# coding: utf-8

from dao import *
from iotools import *
import random

class MySampler:

	def __init__(self):
		self.sum=0
		self.pop=[]
	
	def initS1(self, fnm='deg.centr'):
		sum=0
		fio=FileIO(fnm)
		while fio.next(): 
			nid, deg = fio.getInts()
			self.sum+=deg
			self.pop.append((nid, self.sum))
	
	def sampleS1(self):
		tmp=random.random()*self.sum
		i=0
		while tmp>self.pop[i][1]: i+=1
		n1=self.pop[i][0]
		rst=sampleNbrs(n1, 1)
		return (n1, rst[0]) if rst is not None else None

if __name__=='__main__':
	sampler=MySampler()
	sampler.initS1()
	print sampler.sampleS1()
