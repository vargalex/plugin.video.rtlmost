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


import urlparse,sys, xbmcgui

params = dict(urlparse.parse_qsl(sys.argv[2].replace('?','')))

action = params.get('action')

fanart = params.get('fanart')

subcats = params.get('subcats')

url = params.get('url')

image = params.get('image')

meta = params.get('meta')

if action == None:
    from resources.lib.indexers import navigator
    navigator.navigator().root()

elif action == 'programs':
    from resources.lib.indexers import navigator
    navigator.navigator().programs(url)

elif action == 'episodes':
    from resources.lib.indexers import navigator
    navigator.navigator().episodes(url, fanart, subcats)

elif action == 'play':
    from resources.lib.indexers import navigator
    navigator.navigator().get_video(url, meta, image)

elif action == 'liveChannels':
    from resources.lib.indexers import navigator
    navigator.navigator().liveChannels()

elif action == 'liveChannel':
    from resources.lib.indexers import navigator
    navigator.navigator().liveChannel(url)

elif action == 'drmSettings':
    import xbmcaddon
    xbmcaddon.Addon(id='inputstream.adaptive').openSettings()
