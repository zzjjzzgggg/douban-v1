

f=open('usr_recs_count.dat')
fw=None
for i,uid in enumerate(f):
	if i%10000==0: 
		if fw!=None: fw.close()
		fw=open('usrs-%d.txt' % (i/10000), 'w')
	fw.write(uid)
fw.close()
f.close()
