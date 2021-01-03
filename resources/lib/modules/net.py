# -*- coding: utf-8 -*-

'''
    RTL Most Add-on
    Copyright (C) 2018

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import sys,urllib,urllib2,random,cookielib


def request(url, post=None, headers={}, redirect=True, timeout=30):
    handlers = []
    if (2, 7, 8) < sys.version_info < (2, 7, 12):
        try:
            import ssl; ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            handlers += [urllib2.HTTPSHandler(context=ssl_context)]
            opener = urllib2.build_opener(*handlers)
            opener = urllib2.install_opener(opener)
        except:
            pass

    headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
        'Referer': 'https://www.rtlmost.hu/',
        'x-customer-name': 'rtlhu',
        'Accept-Language': 'hu-HU,hu;q=0.8,en-US;q=0.5,en;q=0.3'})

    if isinstance(post, dict):
        post = urllib.urlencode(post)
    
    if redirect == False:

        class NoRedirectHandler(urllib2.HTTPRedirectHandler):
            def http_error_302(self, req, fp, code, msg, headers):
                infourl = urllib.addinfourl(fp, headers, req.get_full_url())
                infourl.status = code
                infourl.code = code
                return infourl
            http_error_300 = http_error_302
            http_error_301 = http_error_302
            http_error_303 = http_error_302
            http_error_307 = http_error_302

        opener = urllib2.build_opener(NoRedirectHandler())
        urllib2.install_opener(opener)

        try: del headers['Referer']
        except: pass

    request = urllib2.Request(url, data=post, headers=headers)
    response = urllib2.urlopen(request, timeout=timeout)

    if redirect == False:
        result = response.headers.get('location')

    else: 
        result = response.read(5242880)
    response.close()
    return result
