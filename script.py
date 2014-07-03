import sys
import json
file=open(sys.argv[1],'r')
obj=json.loads(file.read())
print obj
result=obj[u'result']
output=open("output.txt","w")
for result_ in result:
    print result_[u'name']
    output.write((result_[u'name']+","+sys.argv[2]+'\n').encode('utf8'))
output.close()