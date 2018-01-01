#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
def gb2cyl(size):
    """
    This function calculate the number of cylinders.

    - LUN between 1GB and 9GB have 1093 Cylinders
    - LUN >= 10GB < 50GB (and multiples) has 10924 Cylinders
      (+1093 cylinders for GB).
      Samples:
        . 10GB LUN has 10924 cylinders
        . 15GB LUN has 10*10924 + 5*1093 cylinders
        . 23GB LUN has 10924*2 + 3*1093 cylinders
    - LUN >= 50 (ad multiples) has 54626 (+10924 for 10GB multiples and
      +1093 cylinder per GB)
      Samples:
        . 50GB LUN has 54620 cylinders
        . 53GB LUN has 54620 + 3*1093  cylinders
        . 75GB LUN has 54620 + 2*10924 + 1093 cylinders
    :param size: size of lun in GB

    :return: Value of GB in CYL
    """

    gb = 1093
    teen_gb = 10924
    fifty_gb = 54620

    def base10(valueb10):
        int10 = valueb10/10
        flt10 = valueb10%10

        result_b10 = (int10*teen_gb)+(flt10*gb)
        return result_b10

    def base50(valueb50):
        int50 = valueb50/50
        flt50 = valueb50%50

        if flt50 == 0:
            result_b50 = (int50*fifty_gb)
            return result_b50

        elif (flt50 > 0) and (flt50 < 10):
            return (int50*fifty_gb)+(flt50*gb)

        else:
            return (int50*fifty_gb)+base10(flt50)

    if size < 10:
        size *= gb
        return size

    elif 10 <= size <= 49:

        if size == 10:
            size = teen_gb
            return size

        else:
            return base10(size)

    else:
        return base50(size)
