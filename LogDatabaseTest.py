from LogDatabase import *

db = LogDatabase('test.txt')
db._log_write_error('db','key','val','msg')
db._log_read_error('s','msg')
db.create_db('db')
db.create_db(['db2'])
db.write_val('db','key','val')
db.write_to_ls('db','ls key','ls val')
db.write_to_ls('db','ls key',['ls val 2'])
db.write_val('db','key2','val2')
db.write_to_ls('db','ls key',['ls val 3'])
db.write_to_ls('db','ls key2',['ls 2 val'])
print(db.db)
print(db.db == {'db': {'key': 'val', 'ls key': ['ls val', 'ls val 2', 'ls val 3'], 'key2': 'val2', 'ls key2':['ls 2 val']}, 'db2': {}})
print(db.delete('db','key2'))
print(db.pop_from_ls('db','ls key','ls val 3'))
print(db.delete('db','ls key2'))
print(db.db)
