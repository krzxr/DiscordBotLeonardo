from LeonardoBotV3 import *

def test(include, result):
    if result==None:
        print('#############\nerror! for expected',include,'\n################')
    elif not include in result:
        print('error!:: <' +include + '> is not in result <'+result+'>')
    else: 
        print('success!:: '+result)
file_name = 'test-leo-bot.txt'
recorded_file = file_name.split('.')[0]+'-v2.txt'
if os.path.exists(recorded_file): os.remove(recorded_file)
leo = Leonardo(file_name,'test')
test('saved',leo.respond('!!save a b',''))
test('saved',leo.respond('!!save a b c',''))
test('b',leo.respond('!!get a',''))
test('removed',leo.respond('!!del a',''))
test('does not',leo.respond('!!get a',''))
test('saved',leo.respond('!!save a 1',''))
test('1',leo.respond('!!get a',''))
test('supports',leo.respond('!!show-all',''))
test('test', leo.respond('!! hi!','test'))
test('test', leo.respond('Hi Leo!','test'))
test('help', leo.respond('leo his!','test'))
test('supports', leo.respond('leo help','test'))
test('test', leo.respond('Hello Leonardo!','test'))
test('test', leo.respond('Hi!!','test'))

