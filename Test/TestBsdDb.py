from bsddb3 import db                   # the Berkeley db data base
import json
# Part 1: Create database and insert 4 elements
#
filename = 'fruit'

# Get an instance of BerkeleyDB
fruitDB = db.DB()
# 	There are also, B+tree and Recno access methods
fruitDB.open(filename, None, db.DB_HASH, db.DB_CREATE | db.DB_DIRTY_READ)

# Print version information
print('\t', db.DB_VERSION_STRING)

# Insert new elements in database
fruitDB.put(b"apple","red")
fruitDB.put(b"orange","orange")
fruitDB.put(b"banana","yellow")
fruitDB.put(b"tomato","red")
fruitDB.put(b"test", json.dumps({"t": 1}))
# Close database
fruitDB.close()

# Part 2: Open database and write its contents out
#
fruitDB = db.DB()
# Open database
#	Access method: Hash
#	set isolation level to "dirty read (read uncommited)"
fruitDB.open(filename, None, db.DB_HASH, db.DB_DIRTY_READ)

# get database cursor and print out database content
cursor = fruitDB.cursor()
rec = cursor.first()
while rec:
        print(rec)
        rec = cursor.next()

test_string = fruitDB.get(b"test")
if test_string:
        json_data = json.loads(test_string)
        print(json_data)
fruitDB.close()