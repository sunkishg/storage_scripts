#!/usr/bin/env python
# -*- coding: utf-8 -*-
#


import sqlite3
import os

class DB(object):    
    """docstring"""

    def __init__(self, database='nasfilesystem.sqlite'):

        self.database = database
        self.connect()

    def connect(self):
        """Connect to the SQLite3 database."""

        self.con = sqlite3.connect(self.database)
        self.cur = self.con.cursor()
        self.connected = True

    def close(self): 
        """Close the SQLite3 database."""

        self.con.commit()
        self.con.close()
        self.connected = False


    def createtable(self):
        """creates database tables if not exists"""
        self.connect()
        self.cur.executescript("""
            CREATE TABLE IF NOT EXISTS vendor (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            vendor_name TEXT UNIQUE
            );
            CREATE TABLE IF NOT EXISTS array (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            vendor_id INTEGER,
            array_name TEXT UNIQUE
            );
            CREATE TABLE IF NOT EXISTS storage_pool (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            vendor_id INTEGER,
            array_id INTEGER,
            pool_name TEXT,
            total REAL,
            used REAL,
            avail REAL,
            cap REAL
            );
            CREATE TABLE IF NOT EXISTS volume (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            array_id INTEGER,
            filesystem TEXT,
            total REAL,
            advisory REAL,
            used REAL,
            avail REAL,
            cap REAL,
            iused INTEGER,
            ifree INTEGER,
            icap INTEGER
            );
            """)
        self.close()


    def droptable(self):
        """drops all tables"""
        self.connect()
        self.cur.executescript("""
            DROP TABLE IF EXISTS vendor;
            DROP TABLE IF EXISTS array;
            DROP TABLE IF EXISTS storage_pool;
            DROP TABLE IF EXISTS volume
            """)
        self.close()


    def vendortable(self, vendorname):
        """updates vendor table and returns Vendor ID"""
        self.connect()
        self.cur.execute('''INSERT OR IGNORE INTO vendor (vendor_name)
            VALUES (:vendorname)''', {'vendorname': vendorname} )
        self.con.commit()
        self.cur.execute('SELECT id FROM vendor WHERE vendor_name =:vendorname ', {'vendorname': vendorname})
        vid = self.cur.fetchone()[0]
        # self.close()
        return vid

    def arraytable(self, vendorname, array):
        """updates vendor array and returns array ID"""
        self.connect()
        vid = self.vendortable(vendorname)
        self.cur.execute('''INSERT OR IGNORE INTO array (vendor_id, array_name)
        VALUES (:vendor_id, :array_name)''', {'vendor_id': vid, 'array_name': array} )
        self.con.commit()
        self.cur.execute('SELECT id FROM array WHERE array_name =:array ', {'array': array})
        aid = self.cur.fetchone()[0]
        # self.close()
        return aid


    def filesystemtable(self, vendorname, array, fsdata=dict()):
        self.connect()
        array_id = self.arraytable(vendorname, array)
        for filesystem,filesysdata in fsdata.iteritems():
            total = filesysdata.get('total', 0)
            advisory = filesysdata.get('advisory', 0)
            used = filesysdata.get('used', 0)
            avail = filesysdata.get('avail', 0)
            cap = filesysdata.get('cap', 0)
            self.cur.execute('''INSERT OR REPLACE INTO volume (array_id, filesystem, total, advisory, used, avail, cap)
                VALUES (:array_id, :filesystem, :total, :advisory, :used, :avail, :cap)''',
                {'array_id': array_id, 'filesystem': filesystem, 'total': total, 'advisory': advisory, 'used': used, 'avail': avail, 'cap': cap})
            self.con.commit()
        self.close()


    def pooltable(self, vendorname, array, aggrdata=dict()):
        self.connect()
        array_id = self.arraytable(vendorname, array)
        for aggrname,aggrinfo in aggrdata.iteritems():
            total = aggrinfo.get('total', 0)
            used = aggrinfo.get('used', 0)
            avail = aggrinfo.get('avail', 0)
            cap = aggrinfo.get('cap', 0)
            self.cur.execute('''INSERT OR REPLACE INTO volume (array_id, filesystem, total, advisory, used, avail, cap)
                VALUES (:array_id, :filesystem, :total, :advisory, :used, :avail, :cap)''',
                {'array_id': array_id, 'filesystem': filesystem, 'total': total, 'advisory': advisory, 'used': used, 'avail': avail, 'cap': cap})
            self.con.commit()
        self.close()





def main():
    mydata = {'disk1': {'total': 500, 'used': 81, 'avail': 383, 'cap': 18, 'advisory': 400}}
    G = DB()
    G.droptable()
    G.createtable()
    G.filesystemtable('apple','govardhan-macbook-pro', mydata)
    data = {'cdlfas02c1': 'netapp', 'cdlfas02c2': 'netapp', 'cdlfas03c1': 'netapp', 'cdlfas03c2': 'netapp', 'cdlfas04c1': 'netapp', 'cdlfas04c2': 'netapp', 'cdlisilon01': 'isilon', 'dc01esisilon01': 'isilon', 'dc02esisilon01': 'isilon', '1605': 'vmax'}
    for k,v in data.iteritems():
        z = G.arraytable(v,k)
        print z



if __name__ == '__main__':
    main()