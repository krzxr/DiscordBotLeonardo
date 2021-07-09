from discordbot import *

def test(include, result):
    if result==None:
        print('error!')
    elif not include in result:
        print('error!:: <' +include + '> is not in result <'+result+'>')
    else: 
        print('success!:: '+result)

leo = Leonardo()
test('saved',leo.respond('!!zoom set a b',''))
test('b',leo.respond('!!zoom get a',''))
test('removed',leo.respond('!!zoom del a',''))
test('does not',leo.respond('!!zoom get a',''))
test('saved',leo.respond('!!zoom set a 1',''))
test('https',leo.respond('!!zoom get a',''))

test('test', leo.respond('!! hi!','test'))
test('test', leo.respond('Hi Leo!','test'))
test('test', leo.respond('Hello Leonardo!','test'))
test('test', leo.respond('Hi!!','test'))
