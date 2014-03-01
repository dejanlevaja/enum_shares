#!/usr/bin/env python
__author__  = "Dejan Levaja"
__license__ = "GPL"
__version__ = "0.1"

import os
import sys
import ipcalc
import threading
import time
import Queue
import codecs
import argparse
from smb.SMBConnection import SMBConnection

lock = threading.Lock()
q = Queue.Queue()
me = 'EnumMaster'


class EnumShares():
    def __init__(self, user, pwd, output):
        self.user = user
        self.pwd = pwd
        self.output = output
        
    def get_shares(self):
        
        try:
            shares = self.conn.listShares(timeout=3)
            return shares
        except:
            pass
            

    def create_folder(self, name):
        # *** Try to create a folder ***
        if not name in ('IPC$', 'print$'):
            try:
                self.conn.createDirectory(name, test_folder)
                msg = '%s  =>  %s\t\tWRITABLE!' % (self.remote_ip, str(name).rjust(10)) #, writable)
                lock.acquire()
                print msg  
                if self.output:
                    logger.writer(msg)
                lock.release()  

            except:
                msg = '%s  =>  %s' % (self.remote_ip, name)
                lock.acquire()
                print msg   
                lock.release()

    def delete_folder(self, name):
        # *** Try to delete the folder ***
        if not name in ('IPC$', 'print$'):
            try:
                self.conn.deleteDirectory(name, test_folder)
            except:
                msg = '[!] Could not remove %s  from  "%s\%s" !' % (test_folder, self.remote_ip, name)
                lock.acquire()
                print msg   
                if self.output:
                    logger.writer(msg)
                lock.release()
   

    def connect(self, remote_ip):
        #print 'ip: ', remote_ip
        self.remote_ip = remote_ip
        self.conn = SMBConnection(self.user, self.pwd, me, self.remote_ip, domain=dom, use_ntlm_v2 = True, is_direct_tcp=True)
        try:
            assert self.conn.connect(self.remote_ip, 445, timeout=3)
        except Exception, e:
            lock.acquire()
            if 'Broken pipe' in str(e):
                print '[!] Cannot contact %s' % self.remote_ip
            else:
                print '[!] Acces Denied %s' % self.remote_ip
            lock.release()
            return
            
        shares = self.get_shares()
        
        if shares:
            for share in shares:
                if writetest:
                    self.create_folder(share.name)
                    self.delete_folder(share.name)
                else:
                        msg = '%s  =>  %s' % (self.remote_ip, str(share.name).rjust(10))
                        lock.acquire()
                        print msg
                        if self.output:
                            logger.writer(msg)
                        lock.release()
        else:
            return


class Logger():
    def __init__(self, output):
        self.output = output
        
    def writer(self, msg):    
        with codecs.open(self.output, 'a', encoding = 'utf-8') as f:
            f.write(msg+'\n')

def main():
    if ips[0].isdigit():
        if '/' in ips:
            for ip in ipcalc.Network(ips):
                q.put(ip)
            while 1:
                if not q.empty():
                    tcount = threading.active_count()
                    if tcount < numthreads:
                        ip = q.get()
                        es = EnumShares(user, pwd, output)
                        p = threading.Thread(target=es.connect, args=(str(ip),) )
                        p.daemon = False
                        p.start()  
                    else:
                        time.sleep(0.5)
                else:
                    break
        else:
            ip = ips
            es.connect(ip)
    else:
        print '\nNo computer names allowed, only IP adressess.'
        sys.exit()
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', required = True)
    parser.add_argument('-u', '--username', required = True)
    parser.add_argument('-p', '--password', required = True)
    parser.add_argument('-w', '--writable', action = 'store_true')
    parser.add_argument('-n', '--numthreads', default = '50')
    parser.add_argument('-o', '--outfile', default = None)
    args = parser.parse_args()
    
    ips = args.target
    usr = args.username
    if '\\' in usr:
        dom, user = usr.split('\\')
    else:
        user = usr
        dom = ''
    
    test_folder = 'EnumMaster_%s' % user.strip()

    pwd = args.password
    output = args.outfile
    if output and os.path.exists(output):
        oww =''
        while oww.lower() not in ('a', 'o'):
            msg = '\n[!] Output file "%s" already exists. Append or owerwrite [a/o] ? ' % output
            oww = raw_input(msg)
            if oww.lower() == 'o':
                with open(output, 'w') as f: pass
        
    writetest = args.writable
    if writetest:
        print '\n[!] To test if the share is writable, we need to try to create an empty folder named:"%s" in it.' % test_folder
        print '    We will try to remove that folder instantly, but it may fail for various reasons.'
        answer = ''
        while answer.lower() not in ('yes', 'no'):
            answer = raw_input('    Are you sure you want to test write access [yes/no] ? ')
            if answer.lower() == 'no':
                writetest = False
            
        
    print '\nSettings:'    
    print 'domain: ', dom
    print 'user: ', user
    print 'write test: ', writetest
    print 'output:' , output
    print '\n'
    
    numthreads = int(args.numthreads)
    
    
    if output:
        logger = Logger(output)
    
    main()
    sys.exit()
