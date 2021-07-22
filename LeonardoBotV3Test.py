from LeonardoBotV3 import *

def test(include, result):
    if result==None:
        if include != None:
            include= '<Empty String>' if include=='' else include
            print('#############\nerror! Got <None> for expected',include,'\n################')
        else:
            print('success!:: Expect <None> Got <None>')
    elif not include in result:
        include= '<Empty String>' if include=='' else include
        print('error!:: <' +include + '> is not in result <'+result+'>')
    else: 
        print('success!:: '+result)
file_name = 'test-leo-bot.txt'
recorded_file = file_name.split('.')[0]+'-v2.txt'
if os.path.exists(recorded_file): os.remove(recorded_file)
leo = Leonardo(file_name,'test')
test('saved',leo.respond('!&save a b',''))
test('saved',leo.respond('!&save a b c',''))
test('b',leo.respond('!&get a',''))
test('removed',leo.respond('!&del a',''))
test('does not',leo.respond('!&get a',''))
test('saved',leo.respond('!&save a 1',''))
test('1',leo.respond('!&get a',''))
test('supports',leo.respond('!&show-all',''))
test('test', leo.respond('!& hi!','test'))
test('test', leo.respond('Hi Leo!','test'))
test('help', leo.respond('leo his!','test'))
test('supports', leo.respond('leo help','test'))
test('test', leo.respond('Hello Leonardo!','test'))
test(None, leo.respond('Hi!!','test'))

test('saved', leo.respond('https://zoom_user_name_abc','user_name_abc'))
test('https://zoom/user_name_abc', leo.respond('leo zoom','user_name_abc'))
test('deleted', leo.respond('leo zoom-del','user_name_abc'))
'''
test('Want', leo.respond('https://zoom',''))
test('https://zoom', leo.respond('Yes alias',''))
test(None, leo.respond('hi',''))
test('https://zoom', leo.respond('Leo get alias',''))
test('Want', leo.respond('https://zoom1',''))
test('Got', leo.respond('No',''))
test('Want', leo.respond('https://zoom2',''))
test('Missing', leo.respond('Yes',''))
test('https://zoom2', leo.respond('Yes alias2',''))
test('Want', leo.respond('https://zoom3',''))
test('forget', leo.respond('Hi',''))
'''
