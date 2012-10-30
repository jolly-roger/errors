import cherrypy
import smtplib
import urllib.request
import urllib.parse
import json
from email.mime.text import MIMEText


def sendmail(status, message, traceback, version, subject, cpdata):
    sender = 'www@dig-dns.com (www)'
    recipient = 'roger@dig-dns.com'
    
    text = 'Base: ' + cpdata['base'] + '\n\n' +\
        'Request line: ' + cpdata['request_line'] + '\n\n' +\
        'Status: ' + status + '\n\n' + 'Message: ' + message + '\n\n' +\
        'Traceback: ' + traceback + '\n\n' + 'Version: ' + version
    
    msg = MIMEText(text)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()


class robots(object):
    @cherrypy.expose
    def sendmail(self, status, message, traceback, version, subject, cpdata):
        return sendmail(status, message, traceback, version, subject, json.loads(cpdata))
    
    @cherrypy.expose
    def testmail(self):
        return sendmail('500', 'Test', 'Test traceback', 'None', 'Errors test error',
            json.dumps({'base': cherrypy.request.base, 'request_line': cherrypy.request.request_line}))
    
    @cherrypy.expose
    def testrequest(self):
        d = urllib.parse.urlencode({'status': '500', 'message': 'Test', 'traceback': 'Test traceback',
            'version': 'None', 'subject': 'Errors test error',
            'cpdata': json.dumps({'base': cherrypy.request.base, 'request_line': cherrypy.request.request_line})})
        r = urllib.request.urlopen('http://localhost:18404/sendmail', d)
        
        return r.read()

def error_page_default(status, message, traceback, version):
    return sendmail(status, message, traceback, version, 'Errors error',
        {'base': cherrypy.request.base, 'request_line': cherrypy.request.request_line})


cherrypy.tree.mount(robots())

cherrypy.config.update({'error_page.default': error_page_default})
cherrypy.config.update({'engine.autoreload_on':False})