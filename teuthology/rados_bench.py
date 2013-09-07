import logging
import MySQLdb
import os
import re

log = logging.getLogger(__name__)

"""
The coverage database can be created in mysql with:

CREATE TABLE `rados_bench` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `suite` varchar(255) NOT NULL,
  `pid` integer NOT NULL,
  `bandwidth` float unsigned NOT NULL,
  `stddev` float unsigned NOT NULL,
   PRIMARY KEY (`run_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
"""

def connect_to_db(info):
    db = MySQLdb.connect(
        host=info['host'],
        user=info['user'],
        db=info['db_name'],
        passwd=info['passwd'],
        )
    db.autocommit(False)
    return db

def txtfind(ftext, stext):
    indx = ftext.find(stext)
    if indx < 1:
        return False
    tstrng = ftext[indx:]
    tstrng = tstrng[:tstrng.find('\n')]
    return tstrng.split()[::-1][0].strip() 

def xtract_date(text):
    p = re.match('.*\-[-0-9]*_[:0-9]*',text)
    pdate = p.group(0)
    pdate = pdate[pdate.find('-')+1:]
    return pdate.replace('_',' ')
    
def add2db(date,suite,pid,bandwidth,stddev,db):
    c = db.cursor()
    pattern1 = 'select * from rados_bench where suite="%s" and pid=%s'
    if c.execute(pattern1 % (suite,pid)) > 0:
        return
    pattern2 = 'insert rados_bench (date, suite, pid, bandwidth, stddev) values ("%s","%s",%s,%s,%s)'
    c = db.cursor()
    c.execute(pattern2 % (date, suite, pid, bandwidth, stddev))
    db.commit()

def scan_for_records(indir, db):
    for suite in os.listdir(indir):
        dir1 = "%s/%s" % (indir,suite)
        for pid in os.listdir(dir1):
            if pid.isdigit():
                tfile = "%s/%s/teuthology.log" % (dir1,pid)
                if os.path.exists(tfile):
                    with open(tfile, 'r') as f:
                        txt = f.read()
                        bandwidth = txtfind(txt,'Bandwidth (MB/sec):')
                        if bandwidth:
                            stddev = txtfind(txt,'Stddev Bandwidth:')
                            date = xtract_date(suite)
                            add2db(date,suite,pid,bandwidth,stddev,db)

def collect():
    """
    This is the entry point to the rados benchmark data collector.
    /a is scanned for teuthology.log entries.  Any entry that has
    bandwidth data that is already not stored in the database is saved.
    """
    logging.basicConfig( level=logging.INFO,)
    info = dict(host='deeby.inktank.com',user='perf_test',db_name='perf_test',passwd='speedkills',)
    db = connect_to_db(info)
    c = db.cursor()
    c.execute('show tables')
    a = scan_for_records('/a', db)
