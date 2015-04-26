import sqlite3,os

sql=['CREATE TABLE "contacts" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "name" TEXT, "mail" TEXT, "note" TEXT, "keydir" TEXT, "member_id" INTEGER);',
'CREATE TABLE "members" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "username" TEXT, "password" TEXT, "full_name" TEXT,"last_logon" DATETIME,"DIR" TEXT);',
'CREATE TABLE "shared" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "name" TEXT, "keydir" TEXT, "type" BOOL,"member_id" INTEGER);']


def createDB():

   db=sqlite3.connect('tahoe.db')
   for line in sql:
      db.execute(line)

   db.close()

def all_members():
   db=sqlite3.connect('tahoe.db')
   return db.execute('select username,full_name,last_logon,DIR from members')
  



def add_member(login,full_name,password,DIR):
   db=sqlite3.connect('tahoe.db')
   db.execute("insert into members(username,full_name,password,DIR) values('"+login+"','"+full_name+"',"+"'"+password+"','"+DIR+"')")
   db.commit()
   return 0

def del_member(login):
   
   db=sqlite3.connect('tahoe.db')
   db.execute("delete members where login='"+login+"'");

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


