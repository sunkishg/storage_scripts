#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

from vmax import VMAX

x = VMAX()
y = x.sg_to_dict('1079', 'testserver01')
print(y)
z = x.vmax3_create_dev(sid='1079', count=1, size=256, storage_group='weiping_test_sg', action='prepare')
print(z)
