#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""docstring"""


import os
from nasdb import DATABSE
from isilon import ISILON
from netapp import NETAPP


# PWD
# dirpath = os.path.dirname(os.path.realpath(__file__))
# fhand = open(os.path.join(dirpath, 'netapp_fs_report_out.html'), 'w')


class NAS(object):
  """docstring"""
  def __init__(self):

    # Storage arrays list
    self.netapp_filers_list = ('filer1', 'filer2', 'filer3')

    self.isilon_clusters_list = ('filer1', 'filer2', 'filer3')

    # init database
    self.db = DATABSE()

  def dbreset(self):
    """DROPS EXISTING DATA AND TABLES FROM DB"""    
    self.db.droptable()

  def dbcreate(self):
    """create tables if not exists"""
    self.db.createtable()

  def isilon_dump(self):
    for cluster in self.isilon_clusters_list:
      isicls = ISILON(cluster)
      quotas = isicls.quotas()
      self.db.filesystemtable('Isilon', cluster, quotas)


  def netapp_dump(self):
    for filer in self.netapp_filers_list:
      netcls = NETAPP(filer)
      vol = netcls.volume()
      self.db.filesystemtable('netapp', filer, vol)
      agg = netcls.aggr()
      self.db.pooltable('netapp', filer, agg)

def main():
  n = NAS()
  n.dbreset()
  n.dbcreate()
  n.isilon_dump()
  n.netapp_dump()
  n.db.close()


if __name__ == '__main__':
    main()

