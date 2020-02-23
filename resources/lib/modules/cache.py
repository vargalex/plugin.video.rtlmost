# -*- coding: utf-8 -*-

import re,hashlib,time,xbmc,os,xbmcaddon

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')
cacheFile = os.path.join(dataPath, 'cache.db')

def get(function, timeout, *args, **table):
    try:
        response = None

        f = repr(function)
        f = re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        a = hashlib.md5()
        for i in args: a.update(str(i))
        a = str(a.hexdigest())
    except:
        pass

    try:
        table = table['table']
    except:
        table = 'rel_list'

    try:
        control.makeFile(dataPath)
        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        match = dbcur.fetchone()

        response = eval(match[2].encode('utf-8'))

        t1 = int(match[3])
        t2 = int(time.time())
        update = (abs(t2 - t1) / 3600) >= int(timeout)
        if update == False:
            return response
    except:
        pass

    try:
        r = function(*args)
        if (r == None or r == []) and not response == None:
            return response
        elif (r == None or r == []):
            return r
    except:
        return

    try:
        r = repr(r)
        t = int(time.time())
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s (""func TEXT, ""args TEXT, ""response TEXT, ""added TEXT, ""UNIQUE(func, args)"");" % table)
        dbcur.execute("DELETE FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        dbcur.execute("INSERT INTO %s Values (?, ?, ?, ?)" % table, (f, a, r, t))
        dbcon.commit()
    except:
        pass

    try:
        return eval(r.encode('utf-8'))
    except:
        pass


def timeout(function, *args, **table):
    try:
        response = None

        f = repr(function)
        f = re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        a = hashlib.md5()
        for i in args: a.update(str(i))
        a = str(a.hexdigest())
    except:
        pass

    try:
        table = table['table']
    except:
        table = 'rel_list'

    try:
        control.makeFile(dataPath)
        dbcon = database.connect(cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        match = dbcur.fetchone()
        return int(match[3])
    except:
        return
