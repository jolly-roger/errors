import cherrypy
import smtplib
import urllib
import pickle
from email.mime.text import MIMEText


def sendmail(status, message, traceback, version, subject, cprequest):
    sender = 'www@dig-dns.com (www)'
    recipient = 'roger@dig-dns.com'
    
    text = 'Base: ' + cprequest.base + '\n\n' +\
        'Request line: ' + cprequest.request_line + '\n\n' +\
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
    def sendmail(self, status, message, traceback, version, subject, cprequest):
        return sendmail(status, message, traceback, version, subject, cprequest)
    
    @cherrypy.expose
    def testmail(self):
        return sendmail('500', 'Test', 'Test traceback', 'None', 'Errors test error', cherrypy.request)
    
    @cherrypy.expose
    def testrequest(self):
        return pickle.dumps(cherrypy.request)

def error_page_default(status, message, traceback, version):
    return sendmail(status, message, traceback, version, 'Errors error', cherrypy.request)


cherrypy.tree.mount(robots())

cherrypy.config.update({'error_page.default': error_page_default})
cherrypy.config.update({'engine.autoreload_on':False})