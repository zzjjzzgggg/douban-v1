#! /usr/bin/env python
#coding=utf-8
import configparser


config = configparser.ConfigParser()
config.read('config.ini')
def readParm(region,key):
	return config.get(region, key)

def readInt(region,key):
	return int(config.get(region, key))

if __name__=='__main__':
	print(readParm('keys','key0'))

