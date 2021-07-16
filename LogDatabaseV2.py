import os
from abc import ABC, abstractmethod
'''
---------------------------------------
database  |  database type | \n
---------------------------------------
database | key | val | attribute |\n
---------------------------------------
'''
HashDBName = 'HashDB'
ListDBName = 'ListDB'
BucketDBName = 'BucketDB'

class BaseDB(ABC):
    # writ: return Boolean, msg
    # get: return content or None
    # delete: no return 
    # get_keys: return keys
    attr_delimit = ':'
    
    def __init__(self, db_name, db_type, delimits, storage_file, write = True, child_note = ''):
        
        self.db_name, self.db_type = db_name, self.db_type
        self.child_note = child_note
        
        self.storage_file = storage_file
        self.error_log = storage_file.split('.')[0] + '-log.txt'
        
        self.delimit, self.sub_delimit, self.new_line = delimits
        self.delimits = delimits
        self.replacements = [('\n', self.new_line)]
        
        assert not db_name in self.delimits, self._log('Invalid DB name',db_name)
        if write:
            self._create_presist()

    def _create_presist(self):
        # database  |  database type | \n
        with open(self.storage_file, 'a') as f:
            f.write(self.delimit.join([self.db_name, self.db_type,'\n']))
    
    def write(self, key, val, persist = True, **keywords):
        validated = self._validate_str(key,val)
        if not validated: return False
        
        saved = self._write_(key,val, **keywords)
        if not saved: return False
                   
        if persist:
            self._to_persist(key, keywords)
        return True
    def _encode_to_persist(self,s):
        for find, replace in self.replacements:
            s = s.replace(find, replace)
        return s
    @abstractmethod
    def _write_(self, key, val, **keywords): # child method
        # return Boolean, Msg. Update internal DB.
        pass
    
    def _to_persist(self, key, delete = False):
        # database | key | val | attribute |\n
        # database | key | | \n
        
        attr = self.sub_delimit.join([self.child_note])
        if not delete:    
            content = self._to_persist_(key, attr)
        else:
            key = self._encode_to_persist(key)
            content = self.delimit.join([self.db_name, key, attr, '\n'])
        with open(self.storage_file, 'a') as f:
            if content:
                f.write(content)
    
    @abstractmethod
    def _to_persist_(self, key, attrs): 
        # val exists. Return content to write
        pass
    
    def delete(self, key, persist = True):
        self._delete_(key) 
        if persist:
            self._to_persist(key, delete = True)

    @abstractmethod
    def _delete_(self, key):
        # Update internal DB.
        pass

    def from_persist(self, content):
        # database | key | val | attribute |\n
        # database | key |  |\n
        content = content.split(self.delimit)
        if len(content) == 5:
            _, key, val, attrs, _ = content
            wrote = self._from_persist_(key, val, attrs)
            self.child_note = attrs
            if not wrote: return False
            else: return True
        elif len(content) == 4:
            _, key, _, _ = content  
            self.delete(key, persist = False)
            return True
        else: 
            self._log('Failed to get from persist with content',content)
            return False
    @abstractmethod
    def _from_persist_(self, key, val, attrs):
        # return Boolean, Msg. Update internal DB.
        pass
    
    @abstractmethod
    def get(self, key, default = None):
        # return key or default
        pass
    def _decode_from_persist(self,s):
        for replace, find in self.replacements:
            s = s.replace(find, replace)
        return s

    @abstractmethod
    def get_keys(self):
        # return keys
        pass

    def _validate_str(self, key, val):
        val = val if type(val)==type([]) else [val]
        if key in self.delimits:
            self._log('Invalid String with key and val',key,val)
            return False
        for v in val:
            if v in self.delimits:
                self._log('Invalid String with key and val',key,val)
                return False
        return True

    def _log(self, msg, *args):
        
        output = ''
        for arg in args:
            arg = arg if type(arg)==type([]) else [arg]
            output += ' '.join(arg)
        output = '< '+self.db_name +'-'+ msg+ ' with params '+output+' >'
        print(output)
        with open(self.error_log,'a') as f:
            f.write(output+'\n')

class HashDB(BaseDB):
    # write(key, val)
    # get(key, default)
    # delete(key)
    # get_keys()

    db_type = HashDBName
    def __init__(self, db_name, delimits, storage_file, write = True, child_note = ''):
        
        super().__init__(db_name, self.db_type, delimits, storage_file, write, child_note)
        self.db = {}
    
    def _write_(self, key, val):
        self.db[key] = val
        return True

    def _to_persist_(self, key, attrs):  # return content to write
        val = self._encode_to_persist(self.db[key])
        key = self._encode_to_persist(key)
        content = self.delimit.join([self.db_name, key, val, attrs,'\n'])
        return content
        
    def get(self, key, default = None): # return key or default
        return self.db.get(key, default)
    
    def _delete_(self, key): # Update internal DB.
        if key in self.db:
            self.db.pop(key)
    def _from_persist_(self, key, val, attrs): # return Boolean, Msg. Update internal DB.
        self.db[key] = val
        return True

    def get_keys(self):
        return self.db.keys()
            
class ListDB(BaseDB):
    # write(key, val, overwrite = False)
    # get(key, default)
    # delete(key)
    # pop(key,val)
    # get_keys()
    db_type = ListDBName
    def __init__(self, db_name, delimits, storage_file, write=True, child_note = ''):
        super().__init__(db_name, self.db_type, delimits, storage_file,write, child_note)
        self.db = {}

    def _write_(self, key, val, **kwargs):
        OVERWRITE = 'overwrite'
        overwrite = False if not OVERWRITE in kwargs else kwargs[OVERWRITE]

        val = val if type(val) == type([]) else [val]
        if overwrite:
            self.db[key] = val 
        else:
            if not key in self.db: self.db[key] = []
            self.db[key] = self.db[key] + val
        return True

    def _to_persist_(self, key, attrs):  # return content to write

        content = self.sub_delimit.join(self.db[key])
        content = self._encode_to_persist(content)
        key = self._encode_to_persist(key)
        return self.delimit.join([self.db_name, key, content, attrs,'\n'])
        
    def get(self, key, default = []): # return key or default
        return self.db.get(key, default)
    
    def pop(self, key, val):
        if key in self.db and val in self.db[key]:
            self.db[key].remove(val)
            self._to_persist(self, key)

    def _delete_(self, key): # Update internal DB.
        if key in self.db:
            self.db.pop(key)
    def _from_persist_(self, key, val, attrs): # return Boolean, Msg. Update internal DB.
        val = val.split(self.sub_delimit)
        self.db[key] = val
        return True
    
    def get_keys(self):
        return self.db.keys()

class BucketDB(BaseDB):
    # write(key, val)
    # get(key, default)
    # delete(key)
    # get_keys()
    # get_bucket(bucket_key)
    # get_bucket_keys()
    db_type = BucketDBName
    def __init__(self, db_name, delimits, storage_file, write = True, buckets = {}, is_list = False, child_note = ''):
        super().__init__(db_name, self.db_type, delimits, storage_file, write, child_note)
        self.db = ListDB(db_name, delimits, storage_file,  self.child_note)
        self.buckets = {bucket:[] for bucket in buckets}
        self.is_list = is_list
    
    def _write_(self, key, val, **kwargs):
        BUCKET_KEY = 'bucket_key'
        if not BUCKET_KEY in kwargs:
            return False,self._log('Argument bucket_key is missing')
        bucket_key = kwargs[BUCKET_KEY]

        val = self._encode_content_(key, val, bucket_key)
        wrote = self.db.write(key,val)
        if not wrote: 
            self._log('From Hash: '+msg)
            return False
        
        self.buckets[bucket_key] = self.buckets.get(bucket_key,[])+[key]

        return True

    def _to_persist_(self, key, bucket_key,attrs):  # return content to write
        return None

    def _encode_content_(self,key, val, bucket_key):
        val = [val, bucket_key] if not self.is_list else val + [bucket_key]
        return val

    def _decode_content_(self, val, from_file):
        assert val != None, 'Value input cannot be null'
        if from_file:
            val = val.split(self.sub_delimit)
        bucket_key = val[-1]
        val = val[:-1]
        return val, bucket_key
    
    def get(self, key, default = None): # return key or default
        val = self.db.get(key, default)
        val, _ = self._decode_content_(val, from_file = False)
        if val == None: return default
        return val
    
    def get_bucket(self, bucket_key, default = []):
        return self.buckets.get(bucket_key, default) 

    def get_bucket_keys(self):
        return list(self.buckets.keys())
    
    def _delete_(self, key): # Update internal DB.
        val = self.db.get(key, default = None)
        val, bucket_key = self._decode_content_(val,from_file = False)
        self.db.delete(key)
        if bucket_key in self.buckets and key in self.buckets[bucket_key]:
            self.buckets[bucket_key].remove(key)

    def _from_persist_(self, key, val, attrs): # return Boolean, Msg. Update internal DB.    
        val, bucket_key = self._decode_content_(val,from_file = True)
        wrote = self.write(key,val, persist = False, bucket_key = bucket_key)
        if not wrote: 
            self._log('From Hash persit: '+msg)
            return False
        return True

    def get_keys(self):
        return self.db.keys()

    def get_bucket_keys(self):
        return self.buckets.keys()

class LogDatabase2():

    def __init__(self, storage_file, delimit = None, sub_delimit = None, new_line = None):
        self.db = {} #name 2 db

        self.storage_file = storage_file.split('.')[0]+'-v2.txt'
        
        self.error_log = storage_file.split('.')[0] + '-v2-log.txt'
        
        self.delimit = delimit if delimit else '||'
        self.sub_delimit = sub_delimit if sub_delimit else '~~~'
        self.new_line = new_line if new_line else '|~x~|'
        self.delimits = [self.delimit, self.sub_delimit, self.new_line]

        self._init_db_files()
    def _init_db_files(self):
        if not os.path.exists(self.storage_file):
            output = ''
            format_symbol = lambda s: s[1] if not s[0] else ''.join(i if i!=' ' else '' for i in s[0])
            
            delimits = [self.delimit, self.sub_delimit, self.new_line]
            self.delimits = delimits
            for delimit in delimits:
                output = output + delimit + ' '
            output += '\n'
            
            with open(self.storage_file,'w') as f:
                f.write(output)

        else:
            with open(self.storage_file,'r') as f:
                content = f.readline()
                delimits = content.strip().split()
                self.delimit, self.sub_delimit, self.new_line = delimits
                self.delimits = delimits
                self._from_persist()

        if not os.path.exists(self.error_log):
            f = open(self.error_log, 'w')
            f.close()

    def _log_error(self, db, msg):
        string = '++ DB '+db+' faces problem ' + msg + '.\n'
        with open(self.error_log,'a') as f:
            f.write(string)
        return string
    def create_db(self,db_name, db_type, write = True, **kwargs):
        if db_name in self.delimits: 
            self._log_error(db_name,'unauthoized DB name symbol')
        db = None
        if db_type == HashDBName:
            db = HashDB(db_name, self.delimits, self.storage_file,  write = write)
        elif db_type == ListDBName:
            db = ListDB(db_name, self.delimits, self.storage_file,  write = write)
        elif db_type == BucketDBName:
            buckets = []
            if 'buckets' in kwargs: buckets = kwargs['buckets']
            db = BucketDB(db_name, self.delimits, self.storage_file, write= write, buckets = buckets)
        else:
            self._log_error(db_name,'missing bucket for bucket db')
        self.db[db_name] = db
        return db 
    def create_dbs(self, db_props, write = True, **kwargs):
        dbs = []

        for db_prop in db_props:
            if len(db_prop) == 2:
                db_name, db_type = db_prop
            elif len(db_prop) == 3:
                db_name, db_type, kwargs = db_prop
            else: raise(Exception(self._log_error(db_prop, 'Invalid db prop creation')))

            if db_type in [HashDBName,ListDBName]:
                dbs.append( self.create_db(db_name, db_type, write=write))            
            elif db_type in [BucketDBName]:
                dbs.append( self.create_db(db_name, db_type, write=write))            

            else: raise(Exception(self._log_error(db_name, 'Incorrect DB Name')))
        return dbs
    def get_db(self,db_name):
        if not db_name in self.db:
            raise(Exception(self._log_error(db_name, 'No DB found')))
        return self.db[db_name]
    def get_dbs(self,db_names):
        return [self.get_db(db_name) for db_name in db_names]

    def _from_persist(self):
        skip_first = True
        with open(self.storage_file,'r') as f:
            while True:
                s = f.readline()

                if skip_first: 
                    skip_first = False
                    continue
                if s == None or s=='': break
                ls = s.split(self.delimit)
                if len(ls) < 3: 
                    self._log_error('','too few columns in this entry: '+s)
                    continue
                elif len(ls)==3:
                    db_name, db_type,_ = s.split(self.delimit)
                    self.db[db_name] = self.create_db(db_name, db_type, write=False)
                else:
                    db_name = ls[0]
                    if not db_name in self.db: 
                        raise(Exception(self._log_error(db_name,'DB read error')))
                    s = self.db[db_name]._decode_from_persist(s)
                    self.db[db_name].from_persist(s)
                    


