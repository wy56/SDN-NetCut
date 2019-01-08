from database import database

db = database()
datas = db.db_getHttptable()
print datas
list = db.db_getList()
for data in list:
    print data["id"],"(",type(data["id"]),")"," ",data["address"],"(",type(data["address"]),")"," ",data["access"],"(",type(data["access"]),")"
