CREATE TABLE "contacts" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "name" TEXT, "mail" TEXT, "note" TEXT, "keydir" TEXT, "member_id" INTEGER);
CREATE TABLE "members" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "login" TEXT, "password" TEXT, "last_logon" DATETIME);
CREATE TABLE "shared" ("id" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL , "name" TEXT, "keydir" TEXT, "type" BOOL,"member_id" INTEGER);

