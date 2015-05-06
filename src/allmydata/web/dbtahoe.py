import sqlite3,os

sql=[
'CREATE TABLE "members" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "username" TEXT UNIQUE, "password" TEXT, "full_name" TEXT,"last_logon" DATETIME,"encrypted" TEXT,"DIR" TEXT);',
'CREATE TABLE "shared" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "name" TEXT, "key" TEXT, "member_id" INTEGER, "password" TEXT, add_directory BOOL, upload_file BOOL);']


db=sqlite3.connect('tahoe.db')

def createDB():
   for line in sql:
      db.execute(line)

def all_members():
   return db.execute('select username,full_name,last_logon,DIR from members')

def add_member(login,full_name,password,DIR):
   db.execute("insert into members(username,full_name,password,DIR) values('"+login+"','"+full_name+"',"+"'"+password+"','"+DIR+"')")
   db.commit()
   return True

def del_member(login):
   
   db.execute("delete members where login='"+login+"'");
   return True

def add_contacts():
   pass

def del_contacts():
   pass

def modify_contact():
   pass

def modify_members():
   pass

def add_place():
   pass

def add_share():
   pass

def del_share():
   pass

def del_place():
   pass

def modify_place():
   pass

def modify_share():
   pass

def checkMembers(username,password):
   
   #db=sqlite3.connect('tahoe.db')
   query=db.execute("select username,full_name from members where username='"+username+"' and password='"+password+"'")
   F=query.fetchone()
   if(F != None):
      return F

   return False

def getDir(username):
   query=db.execute("select DIR from members where username='"+username+"'")
   return query.fetchone

