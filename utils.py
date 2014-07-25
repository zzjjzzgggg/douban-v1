#! /usr/bin/env python
#coding=utf-8

import re

rex_num=re.compile(r'\d+')
def getNums(numstr):
	return map(int, rex_num.findall(numstr))

if __name__=='__main__':
	print getNums('asfdsa123sadfas4353')
