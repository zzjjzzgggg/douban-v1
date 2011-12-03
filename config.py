#! /usr/bin/env python
#coding=utf-8
import ConfigParser


config = ConfigParser.ConfigParser()
def readParm(region,key):
	config.read('config.ini')
	return config.get(region, key)

def readInt(region,key):
	config.read('config.ini')
	return int(config.get(region, key))

def writeParm(region,key,value):
	config.read('config.ini')
	config.set(region, key, value)
	config.write(open('config.ini', "w"))

if __name__=='__main__':
	print readParm('urls','usrinfo_base_url')

