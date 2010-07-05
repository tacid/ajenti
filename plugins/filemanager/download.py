import os.path
import mimetypes
from datetime import datetime

from ajenti.com import *
from ajenti.app.urlhandler import URLHandler, url

class FMDownloader(URLHandler, Plugin):

    @url('^/download/.+')
    def process_dl(self, req, start_response):
        path = '/' + req['PATH_INFO'].split('/', 2)[2]
        return self.serve_file(req, start_response, path)

    def serve_file(self, req, start_response, file):
        # Check if this is a file
        if not os.path.isfile(file):
            start_response('404 Not Found',[])
            return ''

        headers = []
        # Check if we have any known file type
        # For faster response, check for known types:
        content_type = 'application/octet-stream'
        if file.endswith('.css'):
            content_type = 'text/css'
        elif file.endswith('.js'):
            content_type = 'application/javascript'
        elif file.endswith('.png'):
            content_type = 'image/png'
        else:
            (mimetype, encoding) = mimetypes.guess_type(file)
            if mimetype is not None:
                content_type = mimetype
        headers.append(('Content-type',content_type))

        size = os.path.getsize(file)
        mtimestamp = os.path.getmtime(file)
        mtime = datetime.utcfromtimestamp(mtimestamp)

        rtime = req.get('HTTP_IF_MODIFIED_SINCE', None)
        if rtime is not None:
            try:
                self.log.debug('Asked for If-Modified-Since: %s'%rtime)
                rtime = datetime.strptime(rtime, '%a, %b %d %Y %H:%M:%S GMT')
                if mtime <= rtime:
                    start_response('304 Not Modified',[])
                    return ''
            except:
                pass 

        headers.append(('Content-length',str(size)))
        headers.append(('Last-modified',mtime.strftime('%a, %b %d %Y %H:%M:%S GMT')))

        start_response('200 OK', headers)

        self.log.debug('Finishing download: %s'%req['PATH_INFO'])
        return req['wsgi.file_wrapper'](open(file))

