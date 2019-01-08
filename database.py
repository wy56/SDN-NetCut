import sqlite3

class database:
    
    def __init__(self):
        try:
            self.db = sqlite3.connect('test.db')
            print "Opened database successfully"
            self.db_createtable()
        except Exception, e:
            print "Error : Failed to access database ",str(e)

    
    def db_createtable(self):
        try:
            self.db.execute('''CREATE TABLE USER
                (ID INT PRIMARY  KEY      NOT NULL,
                ADDRESS         CHAR(20) NOT NULL,
                ACCESS          INT      NOT NULL);''')
        except Exception, e:
            print "Warning : Failed to create table ",str(e)

    def db_getMaxID(self):
        try:
            cc = 0
            cursor = self.db.execute("SELECT max(ID) FROM USER")
            if cursor :
                for row in cursor:
                    if row[0] == None:
                        cc = 0
                    else:
                        cc = int(row[0])+1
            return cc
        except Exception, e:
            print "Error : Failed to insert record ",str(e)

    def db_insert(self, address, access):
        try:
            cc = self.db_getMaxID()
            print cc
            self.db.execute("INSERT INTO USER (ID,ADDRESS,ACCESS) \
                             VALUES ("+str(cc)+", '"+address+"', "+str(access)+")");
            self.db.commit()
        except Exception, e:
            print "Error : Failed to insert record ",str(e)

    def db_getList(self):
    
        try:
            list = []
            cursor = self.db.execute("SELECT ID, ADDRESS, ACCESS from USER")
            if cursor :
                for row in cursor:
                    if row[0] != None:
                        data = {}
                        data["id"] = row[0]
                        data["address"] = row[1]
                        data["access"] = row[2]
                        list.append(data)
            return list
        except Exception, e:
            print "Error : Failed to read record ",str(e)

    def db_getHttptable(self):
        
        try:
            data = ""
            cursor = self.db.execute("SELECT ID, ADDRESS, ACCESS from USER")
            if cursor :
                for row in cursor:
                    if row[0] != None:
                        data+="<tr>"
                        data+="<td>"+row[1]+"</td >"
                        if row[2]==0 :
                            data+="<td>"+"ALLOW"+"</td>"
                        else :
                            data+="<td>"+"DENY"+"</td>"
                        data+="</tr>"
            return data
        except Exception, e:
            print "Error : Failed to read record ",str(e)