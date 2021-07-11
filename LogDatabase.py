import os
class LogDatabase():

    def __init__(self, storage_file, delimit = None, ls_delimit = None):
        self.db = {}
        self.STORAGE = storage_file 
        self.DELIMIT = delimit
        self.LS_DELIMIT = ls_delimit
        self.ERROR_LOG = storage_file.split('.')[0] + '-log.txt'

        # constants
        self.VAL, self.LS, self.DEL, self.DB = 'VAL','LS', 'DEL', 'DB'
        
        self.symbols = [self.DELIMIT, self.LS_DELIMIT] # having self.DEL is actually ok bc it is now an element type
        self._init_db_files()
        

    def _init_db_files(self):
        if not os.path.exists(self.STORAGE):
            defaults = ['||','---']

            self.DELIMIT, self.LS_DELIMIT = defaults
            format_symbol = lambda s: s[1] if not s[0] else ''.join(i if i!=' ' else '' for i in s[0])
            output = ''
            for s, default in zip(self.symbols, defaults):
                output = output + format_symbol([s, default]) + ' '
            output += '\n'
            with open(self.STORAGE,'w') as f:
                f.write(output)
        else:
            with open(self.STORAGE,'r') as f:
                self.DELIMIT, self.LS_DELIMIT = f.readline().strip().split()
                self._from_file()
        if not os.path.exists(self.ERROR_LOG):
            f = open(self.ERROR_LOG, 'w')
            f.close()
    
    def _log_write_error(self, db, key, val, msg):
        with open(self.ERROR_LOG,'a') as f:
            string = '++ Writing entry to DB '+db+' with key '+ key + ' and val ' + val+' is rejected beccause of ' + msg + '.\n'
            f.write(string)
    def _log_read_error(self, s, msg):
        with open(self.ERROR_LOG,'a') as f:
            string = '++ Reading line '+ s.strip() +' is rejected because of corrupted formattin - '+msg+'.\n'
            f.write(string)


    def _exist_validate(self,db,key):
        if not db in self.db or not key in self.db[db]:
            return False
        return True
    def _string_validate(self, strings):
        for string in strings:
            if string in self.symbols or '\n' in string:
                return False
        return True
    def _write_validate(self, db, key, val, msg = ''):
        val = val if type(val) == type([]) else [val]
        exist, string = db in self.db, self._string_validate([db,key]+val)
        if not exist:
            self._log_write_error(db,key,' '.join(val), 'invalid db name'+msg)
        if not string:
            self._log_write_error(db,key,' '.join(val), 'unauthoized symbol'+msg)
        return exist and string

    def create_db(self,dbs, write = True):
        dbs = dbs if type(dbs) == type([]) else [dbs]
        if not self._string_validate(dbs):
            self._log_write_error(db,'', '','unauthoized symbol')
            return False
        for db in dbs:
            self.db[db] = {}
            if write: 
                self._to_file(db,' ',' ', self.DB)
        return True

    def write_val(self, db, key, val, write = True):
        if not self._write_validate(db,key,val,'from write val'):
            return False
        self.db[db][key] = val
        if write:
            self._to_file(db,key,val, self.VAL)
        return True

    def write_to_ls(self, db, key, val, overwrite = None, write = True):
        if not self._write_validate(db,key,val,'from write val'):
            return True
        
        if overwrite:
            self.db[db][key] = val 
        else:
            if not key in self.db[db]: self.db[db][key] = []
            val = val if type(val)==type([]) else [val]
            self.db[db][key] = self.db[db][key] + val
        if write:
            ls_str = self.LS_DELIMIT.join(self.db[db][key])
            self._to_file(db,key, ls_str, self.LS)
        return True
    
    def delete(self,db,key, write= True):
        if self._exist_validate(db, key):
            self.db[db].pop(key)
            if write: self._to_file(db, key, '', self.DEL)
            return True
        else: 
            self._log_write_error(db, key, '', 'invalid delete')
            return False
    def pop_from_ls(self,db,key, ls_element):
        if self._exist_validate(db,key) and ls_element in self.db[db][key]:
            self.db[db][key].remove(ls_element)
            ls_str = self.LS_DELIMIT.join(self.db[db][key])
            self._to_file(db, key, ls_str, self.LS)
            return True
        else: 
            self._log_write_error(db, key, '', 'pop element')
            return False

    def _to_file(self, db, key, val, element_type):
        with open(self.STORAGE,'a') as f:
            string = self.DELIMIT.join([db,key,element_type,val,'\n'])
            f.write(string)

    def _from_file(self):
        skip_first = True
        with open(self.STORAGE,'r') as f:
            while True:
                s = f.readline()
                if skip_first: 
                    skip_first = False
                    continue
                if s == None or s=='': break
                ls = s.split(self.DELIMIT)
                if len(ls) != 5: 
                    self._log_read_error(s, 'too few columns in this entry')
                    continue
                else:
                    db, key, element_type, val, _ = ls
                    if not db in self.db or element_type == self.DB:
                        self.create_db(db, write=False)
                    if element_type == self.VAL:
                        self.write_val(db,key,val, write = False)
                    elif element_type == self.LS:
                        ls = val.split(self.LS_DELIMIT)
                        self.write_to_ls(db,key,ls, overwrite = True, write = False)
                    elif element_type == self.DEL:
                        self.delete(db,key, write = False)
                    else: 
                        self._log_read_error(s, 'incorrect element type')

    def get(self,db,key, default = None):
        if self._exist_validate(db,key):
            return self.db[db][key]
        else:
            return default
    def get_keys(self, db, default = None):
        if db in self.db:
            return list(self.db[db].keys())
        else:
            return default

