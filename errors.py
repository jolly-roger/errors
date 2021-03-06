import cherrypy
import smtplib
import urllib.request
import urllib.parse
import json
import os.path
from email.mime.text import MIMEText


def sendmail(status, message, traceback, version, data):
    sender = 'www@dig-dns.com (www)'
    recipient = 'roger@dig-dns.com'
    
    if 'headers' not in data:
        data['headers'] = ''
    
    text = 'Base: ' + data['base'] + '\n\n' +\
        'Request line: ' + data['request_line'] + '\n\n' +\
        'Headers: ' + data['headers'] + '\n\n' +\
        'Status: ' + status + '\n\n' + 'Message: ' + message + '\n\n' +\
        'Traceback: ' + traceback + '\n\n' + 'Version: ' + version
    
    msg = MIMEText(text)
    msg['Subject'] = data['subject']
    msg['From'] = sender
    msg['To'] = recipient

    s = smtplib.SMTP('localhost')
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()
    
    return 'Error'


class errors(object):
    @cherrypy.expose
    def sendmail(self, status, message, traceback, version, data):
        return sendmail(status, message, traceback, version, json.loads(data))
    
    @cherrypy.expose
    def testmail(self):
        return sendmail('500', 'Test', 'Test traceback', 'None',
            json.loads(json.dumps({'subject': 'Errors test error', 'base': cherrypy.request.base,
                'request_line': cherrypy.request.request_line})))
    
    @cherrypy.expose
    def testrequest(self):
        d = urllib.parse.urlencode({'status': '500', 'message': 'Test', 'traceback': 'Test traceback', 'version': 'None',
            'data': json.dumps({'subject': 'Errors test error',
                'base': cherrypy.request.base, 'request_line': cherrypy.request.request_line})})
        d = d.encode('utf-8')
        req = urllib.request.Request('http://localhost:18404/sendmail')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded;charset=utf-8')
        res = urllib.request.urlopen(req, d)
        return res.read().decode()
    

def error_page_default(status, message, traceback, version):
    return sendmail(status, message, traceback, version,
        {'subject': 'Errors error', 'base': cherrypy.request.base, 'request_line': cherrypy.request.request_line})

def wsgi():
    conf = os.path.join(os.path.dirname(__file__), "errors.conf")
    tree = cherrypy._cptree.Tree()
    app = tree.mount(errors(), config=conf)
    app.config.update({'/': {'error_page.default': error_page_default}})
    tree.bind_address = (app.config['global']['server.socket_host'], app.config['global']['server.socket_port'])
    cherrypy.log.screen = False
    return tree