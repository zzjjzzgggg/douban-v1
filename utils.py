# encoding: utf-8

import time
import os, re
import codecs

rex_num=re.compile(r'\d+')
def getNums(numstr):
	return map(int, rex_num.findall(numstr))

if __name__=='__main__':
	print getNums('asfdsa123sadfas4353')