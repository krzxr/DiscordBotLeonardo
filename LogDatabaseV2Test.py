from LogDatabaseV2 import *
file_name_prefix = 'test-log2'

def test(expected, actual, msg = None):
    if expected == actual: 
        pass
    else:
        print('++ expected:<',expected,'>, actual:<',actual,'>',msg)
def include(expected, actual, msg= None):
    if expected in actual: 
        pass
    else:
        print('++ expected:<',expected,'>, actual:<',actual,'>',msg)

print('Hash DB')
file_name = file_name_prefix+'-hash.txt'
f = open(file_name, 'w')
f.close()
db = HashDB('hash', ['|', '-','*'], file_name,[])
db.write('key','val')
test({'key':'val'}, db.db)
test('val',db.get('key'))
test(  False, db._validate_str('key','|'),'0' )
test( True, db.from_persist('hash|1|2||\n'),'1')
test( {'key':'val','1':'2'}, db.db)
db.delete('1')
test( {'key':'val'}, db.db)
test( False, db.from_persist('hash||||2||\n'),'2')
test( True, db.from_persist('hash|1| |\n'),'3')

print('List DB')
file_name = file_name_prefix+'-list.txt'
f = open(file_name, 'w')
f.close()
db = ListDB('list', ['|', '-','*'], file_name,[])
db.write('key',['val2'])
test({'key':['val2']}, db.db)
db.write('key',['val'],overwrite=True)
test(['val'],db.get('key'))
test(  False, db._validate_str('key','|'),'0' )
test( True, db.from_persist('hash|1|2-3||\n'))
test( {'key':['val'],'1':['2','3']}, db.db)
db.delete('1')
test( {'key':['val']}, db.db)
test(  False, db.from_persist('hash||||2||\n'))
test( True, db.from_persist('hash|1| |\n'),'1')
db.write('key2',[])
test({'key':['val'],'key2':[]}, db.db)
test('list|key2|||\n',db._to_persist_('key2',''),'list')

print('Bukcet DB')
file_name = file_name_prefix+'-bucket.txt'
f = open(file_name, 'w')
f.close()
db = BucketDB('bucket', ['|', '-','*'], file_name,[],['1','0'],is_list=True)
db.write('key',['val'],bucket_key = '1')
test({'key':['val','1']}, db.db.db,'0')
test({'1':['key'],'0':[]}, db.buckets,'1')
test(['val'],db.get('key'),'2')
test( True, db.from_persist('hash|1|2-3-0||\n'),'3')
test( {'key':['val','1'],'1':['2','3','0']}, db.db.db,'4')
test({'1':['key'],'0':['1']}, db.buckets,'5')
db.delete('1')
test( {'key':['val','1']}, db.db.db,'6')
test({'1':['key'],'0':[]}, db.buckets,'7')


