from LeonardoBot import *

def test(include, result):
    if result==None:
        print('error! for expected',include)
    elif not include in result:
        print('error!:: <' +include + '> is not in result <'+result+'>')
    else: 
        print('success!:: '+result)

leo = Leonardo('test-bot.txt','test')
test('saved',leo.respond('!!save a b',''))
test('b',leo.respond('!!get a',''))
test('removed',leo.respond('!!del a',''))
test('does not',leo.respond('!!get a',''))
test('saved',leo.respond('!!save a 1',''))
test('1',leo.respond('!!get a',''))
test('supports',leo.respond('!!show-all',''))
test('test', leo.respond('!! hi!','test'))
test('test', leo.respond('Hi Leo!','test'))
test('test', leo.respond('Hello Leonardo!','test'))
test('test', leo.respond('Hi!!','test'))
