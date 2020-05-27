# [START imports]
import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)
import traceback        

import os
import datetime, time
import io
import stat
import mimetypes
import StringIO
import json
import re   


from testharness import *
from sdoutil import *

DEFROOT = "./staticbuild"
CHECKEDLOCATIONS = []

class FileCacheItem():
    def __init__(self,stat=None,content=None):
        self.stat = stat
        self.content = content

class SdoFileCache():
    READONLY = "ReadOnly"
    READWRITE = "ReadWrite"

    def __init__(self,writemode):
        if writemode == SdoFileCache.READONLY:
            self.WRITEMODE = False
        elif writemode == SdoFileCache.READWRITE:
            self.WRITEMODE = True
        else:
            raise ValueError("SdoFileCache: invalid writemode value '%s" % mode)
            
        log.info("CWD: %s" % os.getcwd())
        self.root = DEFROOT
        if not os.path.isdir(self.root):
            try:
                os.mkdir(self.root)
            except Exception as e:
                log.error("Error creating cache root: (%s): %s" % (self.root,e))
            
        self.cleanCache()
        
    def getPath(self,cacheFile):
        cacheFile = self.root + "/" + cacheFile
        return cacheFile
    
        
    def buildNameType(self,filename,ftype):
        #log.info(">>>> %s %s" % (filename,ftype))
        dataext = os.path.splitext(filename)
        ext =  dataext[1]
        if ext and len(ext) and ext.startswith('.'):
            ext = ext[1:]
        if ftype and ext != ftype:
            if ftype != "html":
                filename = filename + '.' + ftype
            
        #log.info("buildNameType: filename:%s ftype: %s  ext: %s" % (filename, ftype, ext))
                    
        return filename

    def checkLocationPath(self,location):
        if location not in CHECKEDLOCATIONS:
            CHECKEDLOCATIONS.append(location)
            path = self.root + "/" + location
            try:
                os.makedirs(path)
            except OSError as e:
                if not os.path.isdir(path):
                    raise e
    
    def buildCacheFile(self,filename,ftype,location):
        #log.info("buildCacheFile( %s %s %s )" % (filename,ftype,location))
    
        filename = self.buildNameType(filename,ftype)
        
        loc = getAppVar("LocationOverride")
        if loc:
            #log.info("OverridingLocation to: %s" % loc)
            location = loc
            
    
        if not location:
            if re.match('^[a-z].*',filename):
                location = "terms/properties/" + filename[0]
            elif re.match('^[0-9A-Z].*',filename):
                location = "terms/types/" + filename[0]
            
                
        if not location:
            if ftype:
                location = ftype
        if location:        
            cacheFile = location + "/" + filename
            self.checkLocationPath(location)
        else:
            cacheFile = filename
        if ftype and not cacheFile.endswith("."+ftype):
            cacheFile = cacheFile +"."+ftype

        mimetype = None

        if ftype == "html":
            mimetype = "text/html; charset=utf-8"
        elif ftype == "jsonld" or ftype == "json-ld" :
            mimetype = "application/ld+json; charset=utf-8"
        elif ftype == "json":
            mimetype = "application/json; charset=utf-8"
        elif ftype == "ttl":
            mimetype = "application/x-turtle; charset=utf-8"
        elif ftype == "rdf" or ftype == "xml":
            mimetype = "application/rdf+xml; charset=utf-8"
        elif ftype == "nt":
            mimetype = "text/plain"
        elif ftype == "txt":
            mimetype = "text/plain"
            
        if not mimetype:
            mimetype, contentType = mimetypes.guess_type(cacheFile)
            log.info("Guessed mimetype %s contenttype %s" % (mimetype,contentType))
        #log.info("buildCacheFile: %s '%s' (%s)" % (cacheFile,mimetype,contentType))

        return cacheFile, mimetype

# [START write]
    def writeFormattedFile(self, filename, ftype=None, location=None, content="", raw=False, extrameta=None):
        #log.info("writeFormattedFile(%s, ftype=%s, location=%s, contentlen=%d, raw=%s,extrameta=%s)" % (filename, ftype, location, len(content), raw, extrameta))
        """Create a file."""
        cacheFile, mtype  = self.buildCacheFile(filename,ftype,location)
        if ftype != 'html':
            raw = True
        self.write_file(cacheFile, mtype, content, raw=raw, extrameta=extrameta)

    def write_file(self, cacheFile, mtype=None, content="", raw=False,  extrameta=None):
        """Create a file."""

        log.info('Creating file {} ({})'.format(cacheFile,mtype))
        cacheFile = self.getPath(cacheFile)
        return self._write_file(cacheFile=cacheFile, mtype=mtype, content=content, raw=raw, extrameta=extrameta)

    def _write_file(self, cacheFile, mtype=None, content="", raw=False, extrameta=None):
        #log.info("Attempting to write: %s %s %s" % (cacheFile, mtype, raw))
        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.

        setAppVar(FILESTAT,None)
        moremeta = getAppVar(FILEEXTRAMETA)
        setAppVar(FILEEXTRAMETA,None) #clear out now potentially stale values
        
        if extrameta and moremeta:
            extrameta.update(moremeta)
        else:
            extrameta = moremeta

        try:
            write_options = {}
            if extrameta:
                write_options.update(extrameta)
            if not raw:
                log.info("Encoding to utf8")
                content = content.encode('utf-8')
            with io.open(
                    cacheFile, 'w',
                    encoding="utf-8") as storage_file:
                        storage_file.write(content.decode('utf-8'))
        except Exception as e:
            log.error("File write error: (%s): %s" % (cacheFile,e))
            log.error(traceback.format_exc())
            return False
        
        setAppVar(FILESTAT,self._stat_file(cacheFile,cache=False))
        return True
        

    def write_json_file(self, cacheFile, mtype="application/json", data={}):
        """Create a file."""
        
        cacheFile = self.getPath(cacheFile)
        return self._write_json_file(cacheFile=cacheFile, mtype=mtype, data=data)


    def _write_json_file(self, cacheFile, mtype="application/json", data={}):
        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        log.info("Attempting to write: %s" % cacheFile)
        try:
            with io.open(
                cacheFile, 'w',
                    encoding="utf-8") as storage_file:
                        json.dump(data,storage_file)
        except Exception as e:
            log.info("File write error: (%s): %s" % (cacheFile,e))
            return False
        return True
                    
# [END write]

# [START stat]
    def statFormattedFile(self, filename, ftype="html", location=None, cache=True):
        #log.info("statFormattedFile(%s,%s,%s,%s)" % (filename, ftype, location, cache))
        cacheFile, mtype  = self.buildCacheFile(filename,ftype,location)
        return self.stat_file(cacheFile, ftype, cache)
        
    def stat_file(self, cacheFile, ftype=None, cache=True):
        cacheFile = self.getPath(cacheFile)
        return self._stat_file(cacheFile, ftype=ftype, cache=cache)

    def _stat_file(self, cacheFile, ftype=None, cache=True):
        #log.info("_stat_file(%s,%s,%s)" % (cacheFile, ftype, cache))
        ret = None
        if cache:
            item = self.readCache(cacheFile,ftype)
            if item:
                ret = item.stat
                log.info("Got from readCache")
            
        if not ret:
            #log.info('Stating file {}'.format(cacheFile))
            try:
                ret = os.stat(cacheFile)
            except Exception as e:
                #log.info("Stat error(%s): %s" % (cacheFile,e))
                pass

            if ret:
                #log.info("Stat {}".format(ret))
                itm = FileCacheItem(ret,None)
                self.writeCache(cacheFile, itm, ftype)
        return ret

# [END stat]

# [START Read]
    def readFormattedFile(self, filename, ftype="html", location=None, cache=True):
        #log.info("readFormattedFile(%s,ftype=%s,location=%s,cache=%s)" % (filename,ftype,location,cache))
        stat, content = self.getFormattedFile(filename, ftype, location, cache)
        return content

    def read_file(self, cacheFile, cache=True, stat=None):
        log.info("read_file(%s,%s,%s)" % (cacheFile,cache,stat))
        stat, content = self.get_file(cacheFile,cache,stat)
        return content
        
        
    def getFormattedFile(self, filename, ftype="html", location=None, cache=True):
        #log.info("getFormattedFile(%s,%s,%s,%s)" % (filename,ftype,location,cache))

        cacheFile, mtype  = self.buildCacheFile(filename,ftype,location)
        stat, content = self.get_file(cacheFile,reqtype=ftype, cache=cache)
        return stat, content
        
    def get_file(self, cacheFile, reqtype=None, cache=True):
        cacheFile = self.getPath(cacheFile)
        return self._get_file(cacheFile=cacheFile, reqtype=reqtype, cache=cache)


    def _get_file(self, cacheFile, reqtype=None, cache=True):
        #log.info("_get_file(%s,%s)" % (cacheFile,cache))

        setAppVar(FILESTAT,None)
        
        stat = None
        content = None
        cached = False
        if cache:
            item = self.readCache(cacheFile,reqtype)
            if item:
                content = item.content
                stat = item.stat
                if content:
                    cached = True
                    log.info("Got from readCache")
                    
        if not stat:
            stat = self._stat_file(cacheFile,cache=False)
            if stat:
                #log.info('Opening file {}'.format(cacheFile))
                try:
                    with io.open(cacheFile) as storage_file:
                        content = storage_file.read()
                        storage_file.close()
                        
                except Exception as e:
                    log.info("File read error (%s): %s" % (cacheFile,e))
                    
        if not cached and content:
            #log.info("Adding to cache: %s" % cacheFile)
            val = FileCacheItem(stat=stat,content=content)
            self.writeCache(cacheFile,val, reqtype) 

        setAppVar(FILESTAT,stat)
        return stat, content
        
    def deleteFormattedFile(self, filename, ftype="html", location=None ):
        cacheFile, mtype  = self.buildCacheFile(filename,ftype,location)
        self.delete_file(cacheFile,ftype)
        
    def delete_file(self, cacheFile, ftype=None):
        cacheFile = self.getPath(cacheFile)
        return self._delete_file(cacheFile=cacheFile, ftype=ftype)
        
    def _delete_file(self, cacheFile, ftype=None):
        #log.info("Deleting: %s" % cacheFile)
        self.delCache(cacheFile, ftype)
        try:
              os.remove(cacheFile)
        except Exception as e:
            log.info("File remove error (%s): %s" % (cacheFile,e))
            
    def get_json_file(self, cacheFile):
        log.info("get_json_file(%s)" % (cacheFile))
        data = None
        stat = self.stat_file(cacheFile,cache=False)
        if stat:
            log.info('Opening file {}'.format(self.getPath(cacheFile)))
            try:
                with cloudstorage.open(self.getPath(cacheFile)) as cloudstorage_file:
                    data = json.load(cloudstorage_file)
                    cloudstorage_file.close()
            except cloudstorage.NotFoundError:
                log.info("File not found: %s" % self.getPath(cacheFile))
            except Exception as e:
                log.info("File read error (%s): %s" % (cacheFile,e))
        return data
            

# [END Read]

# [START Cache]
    def cleanCache(self,reqtype=None):
        self.cache = {}
        
    def emptyCache(self,reqtype):
        log.info("Emptying cache for %s" % reqtype)
        if not reqtype:
            self.cache = {}
        else:
            self.cache[reqtype] = {}
            
    def readCache(self, index, reqtype=None):
        if not reqtype:
            reqtype = "unknown"
        
        ctype = self.cache.get(reqtype)
        if ctype:
            return ctype.get(index)
        return None
        
    def writeCache(self, index, value, reqtype=None):
        if not reqtype:
            reqtype = "unknown"

        ctype = self.cache.get(reqtype)
        if not ctype:
            ctype = {}
            self.cache[reqtype] = ctype
        ctype[index] = value
        
    def delCache(self, index, reqtype=None):
        if not reqtype:
            reqtype = "unknown"
        ctype = self.cache.get(reqtype)
        if ctype:
            ctype.pop(index,None)

# [END Cache]

