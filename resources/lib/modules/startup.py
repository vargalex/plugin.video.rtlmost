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


import sys,xbmc,xbmcaddon,json
__addon__ = xbmcaddon.Addon()


def get_installedversion():
    # retrieve current installed version
    json_query = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["version", "name"]}, "id": 1 }')
    if sys.version_info[0] >= 3:
        json_query = str(json_query)
    else:
        json_query = unicode(json_query, 'utf-8', errors='ignore')
    json_query = json.loads(json_query)
    mpd_addon = 'false'
    if 'result' in json_query and 'version' in json_query['result']:
        version_installed  = json_query['result']['version']['major']
        if version_installed >= 18:
            mpd_addon = 'true'
        else:
            __addon__.setSetting('use_dash', 'false')
    __addon__.setSetting('dash_support', mpd_addon)

get_installedversion()
