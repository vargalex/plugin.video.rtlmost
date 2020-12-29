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


import os,sys,re,xbmc,xbmcgui,xbmcplugin,xbmcaddon,urllib,urlparse,json,time
from resources.lib.modules import net
from  collections import OrderedDict


sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addon = xbmcaddon.Addon
addonFanart = addon().getAddonInfo('fanart')

base_url = 'aHR0cHM6Ly9wYy5taWRkbGV3YXJlLjZwbGF5LmZyLzZwbGF5L3YyL3BsYXRmb3Jtcy9tNmdyb3VwX3dlYi9zZXJ2aWNlcy9ydGxodV9ydGxfbW9zdA=='.decode('base64')
img_link = 'aHR0cHM6Ly9pbWFnZXMuNnBsYXkuZnIvdjIvaW1hZ2VzLyVzL3Jhdw=='.decode('base64')
cat_link = 'L2ZvbGRlcnM/bGltaXQ9MTAwJm9mZnNldD0w'
prog_link = 'L2ZvbGRlcnMvJXMvcHJvZ3JhbXM/bGltaXQ9MTAwJm9mZnNldD0wJmNzYT01JndpdGg9cGFyZW50Y29udGV4dA=='
episode_link = 'L3Byb2dyYW1zLyVzL3ZpZGVvcz9jc2E9NSZ3aXRoPWNsaXBzLGZyZWVtaXVtcGFja3MmdHlwZT12aSx2YyxwbGF5bGlzdCZsaW1pdD01MCZvZmZzZXQ9MCZzdWJjYXQ9JXMmc29ydD1zdWJjYXQ='
episode_subcat_link = 'L3Byb2dyYW1zLyVzP3dpdGg9bGlua3Msc3ViY2F0cyxyaWdodHM='
video_link = 'L3ZpZGVvcy8lcz9jc2E9NSZ3aXRoPWNsaXBzLGZyZWVtaXVtcGFja3MscHJvZ3JhbV9pbWFnZXMsc2VydmljZV9kaXNwbGF5X2ltYWdlcw=='
livechannels_link = 'L2xpdmU/Y2hhbm5lbD1ydGxodV9ydGxfa2x1YixydGxodV9ydGxfaWkscnRsaHVfcnRsX2dvbGQscnRsaHVfY29vbCxydGxodV9ydGxfcGx1cyxydGxodV9maWxtX3BsdXMscnRsaHVfc29yb3phdF9wbHVzLHJ0bGh1X211enNpa2FfdHYmd2l0aD1mcmVlbWl1bXBhY2tzLHNlcnZpY2VfZGlzcGxheV9pbWFnZXMsbmV4dGRpZmZ1c2lvbixleHRyYV9kYXRhCg=='
live_stream_link = 'L2xpdmU/Y2hhbm5lbD0lcyZ3aXRoPWZyZWVtaXVtcGFja3Msc2VydmljZV9kaXNwbGF5X2ltYWdlcyxuZXh0ZGlmZnVzaW9uLGV4dHJhX2RhdGEK'
freemiumsubsriptions_url = 'aHR0cHM6Ly82cGxheS11c2Vycy42cGxheS5mci92Mi9wbGF0Zm9ybXMvbTZncm91cF93ZWIvdXNlcnMvJXMvZnJlZW1pdW1zdWJzY3JpcHRpb25z'
freemium_subscription_needed_errormsg = 'QSBob3p6w6Fmw6lyw6lzaGV6IFJUTCBNb3N0KyBlbMWRZml6ZXTDqXMgc3rDvGtzw6lnZXMuClLDqXN6bGV0ZWs6IGh0dHBzOi8vd3d3LnJ0bG1vc3QuaHUvcHJlbWl1bQ=='


class navigator:
    def __init__(self):
        self.username = xbmcaddon.Addon().getSetting('email').strip()
        self.password = xbmcaddon.Addon().getSetting('password').strip()

        if not (self.username and self.password) != '':
            if xbmcgui.Dialog().ok('RTL Most', u'A kieg\u00E9sz\u00EDt\u0151 haszn\u00E1lat\u00E1hoz add meg a bejelentkez\u00E9si adataidat.'):
                xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
                addon(addon().getAddonInfo('id')).openSettings()                
            sys.exit(0)

        self.Login()


    def root(self):
        query = base_url + cat_link.decode('base64')
        categories = net.request(query)

        self.addDirectoryItem('Élő adás', 'liveChannels', '', 'DefaultTVShows.png')
        for i in json.loads(categories):
            self.addDirectoryItem(i['name'].encode('utf-8'), 'programs&url=%s' % str(i['id']), '', 'DefaultTVShows.png')

        self.endDirectory()


    def liveChannels(self):
        liveChannels = {'rtlhu_rtl_klub': 'RTL Klub', 'rtlhu_rtl_ii': 'RTL II', 'rtlhu_cool': 'Cool TV', 'rtlhu_rtl_gold': 'RTL Gold', 'rtlhu_rtl_plus': 'RTL+', 'rtlhu_film_plus': 'Film+', 'rtlhu_sorozat_plus': 'Sorozat+', 'rtlhu_muzsika_tv': 'Muzsika TV'}
        query = base_url + livechannels_link.decode('base64')
        lives = net.request(query)
        for (i,j) in json.loads(lives, object_pairs_hook=OrderedDict).items():
            self.addDirectoryItem("[B]"+liveChannels[i.encode('utf-8')] + "[/B] - " + j[0]['title'].encode('utf-8') + "  [COLOR gold][" + j[0]['diffusion_start_date'].encode('utf-8')[11:-3] + " - " + j[0]['diffusion_end_date'].encode('utf-8')[11:-3] + "][/COLOR]", 'liveChannel&url=%s' % i.encode('utf-8'), '', 'DefaultTVShows.png')
        self.endDirectory()

    def liveChannel(self, channel):
        headers = {
            'x-6play-freemium': '1',
            'x-auth-gigya-uid': xbmcaddon.Addon().getSetting('userid'),
            'x-auth-gigya-signature': xbmcaddon.Addon().getSetting('signature'),
            'x-auth-gigya-signature-timestamp': xbmcaddon.Addon().getSetting('s.timestamp'),
            'Origin': 'https://www.rtlmost.hu'}
        query = base_url + live_stream_link.decode('base64')
        live = net.request(query % channel, headers=headers)
        live = json.loads(live)
        assets = live[channel][0]['live']['assets']
        if assets != []:
            streams = [i['full_physical_path'] for i in assets]
            meta = {'title': live[channel][0]['title']}
            from resources.lib.modules import player
            player.player().play(channel, streams, None, json.dumps(meta))
        else:
            xbmcgui.Dialog().ok(u'Lej\u00E1tsz\u00E1s sikertelen.', freemium_subscription_needed_errormsg.decode('base64').decode('utf-8'))
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())

    def programs(self, id):
        query = base_url + prog_link.decode('base64')
        programs = net.request(query % id)

        for i in json.loads(programs):
            title = i['title'].encode('utf-8')
            try: thumb = img_link % [x['external_key'] for x in i['images'] if x['role'] == 'logo'][0]
            except: thumb = ''
            try: fanart = img_link % [x['external_key'] for x in i['images'] if x['role'] == 'mea'][0]
            except: fanart = None
            id = str(i['id'])
            plot = i['description'].encode('utf-8')
            extraInfo = ""
            if xbmcaddon.Addon().getSetting('show_content_summary') == 'true':
                try:
                    if (i['count']['vi']>0):
                        extraInfo = " (%d %s)" % (i['count']['vi'], i['program_type_wording']['plural'].encode('utf-8') if i['program_type_wording'] != None else 'Teljes adás')
                    else:
                        extraInfo = " (%d előzetes és részletek)" % (i['count']['vc'])
                except: pass
            self.addDirectoryItem("%s[I][COLOR silver]%s[/COLOR][/I]" % (title, extraInfo), 'episodes&url=%s&fanart=%s' % (id, fanart), thumb, 'DefaultTVShows.png', Fanart=fanart, meta={'plot': plot})

        self.endDirectory(type='tvshows')

    def episodes(self, id, fanart, subcats=None):
        try: myfreemiumcodes = json.loads(xbmcaddon.Addon().getSetting('myfreemiumcodes'))
        except: myfreemiumcodes = {}

        def getClipID(item):
            return int(item['clips'][0]['id'])
        
        def getEpisode(item):
            return int(item['clips'][0]['product']['episode'])

        def allEpisodeFilled(episodes):
            allFilled = True
            for item in episodes:
                if (item['clips'][0]['product']['episode'] is None):
                    allFilled = False
            return allFilled

        def episodeIsMostPlus(episode):
            return (('freemium_products' in item) and (len(item['freemium_products']) > 0))

        def userIsEligibleToPlayEpisode(episode):
            if not episodeIsMostPlus(episode):
                return True
            for product in item['freemium_products']:
                code = product["code"]
                id = product["id"]
                if code in myfreemiumcodes and id in myfreemiumcodes[code]:
                    return True
            return False

        try: subcats = json.loads(subcats)
        except: pass
        if subcats == None:
            query = base_url + episode_subcat_link.decode('base64')
            subcats = net.request(query % id)
            subcats = [i for i in json.loads(subcats)['program_subcats'] if 'id' in i]

        if len(subcats) > 1:
            # the show has multiple seasons or subcategories, list these, and let the user to choose one
            for item in subcats:
                str(item['id'])
                self.addDirectoryItem(item['title'].encode('utf-8'), 'episodes&url=%s&fanart=%s&subcats=%s' % (id, fanart, json.dumps([item])), '', 'DefaultFolder.png', Fanart=fanart)
            self.endDirectory(type='seasons')
            return

        query = base_url + episode_link.decode('base64')
        episodes = net.request(query % (id, str(subcats[0]['id'])))
        episodes = json.loads(episodes)

        hidePlus = xbmcaddon.Addon().getSetting('hide_plus') == 'true'

        sortedEpisodes = episodes
        if (xbmcaddon.Addon().getSetting('sort_episodes') == 'true'):
            reverseSorting = False
            if (xbmcaddon.Addon().getSetting('sort_reverse') == 'true'):
                reverseSorting = True
            if (allEpisodeFilled(episodes)):
                sortedEpisodes = sorted(episodes, key=getEpisode, reverse=reverseSorting)
            else:
                sortedEpisodes = sorted(episodes, key=getClipID, reverse=reverseSorting)

        hasItemsListed = False
        for item in sortedEpisodes:
            try:
                eligible = userIsEligibleToPlayEpisode(item)
                if (not hidePlus) or eligible:
                    title = item['title'].encode('utf-8')
                    if not eligible:
                        title = '[COLOR red]' + title + ' [B](Most+)[/B][/COLOR]'
                    plot = item['description'].encode('utf-8')
                    duration = str(item['duration'])
                    try: thumb = img_link % [i['external_key'] for i in item['images'] if i['role'] == 'vignette'][0]
                    except: thumb = img_link % item['display_image']['external_key']
                    thumb = thumb.encode('utf-8')
                    assets = item['clips'][0].get('assets')
                    clip_id = item['id'].encode('utf-8')
                    meta = {'title': title, 'plot': plot, 'duration': duration}
                    self.addDirectoryItem(title, 'play&url=%s&meta=%s&image=%s' % (urllib.quote_plus(clip_id), urllib.quote_plus(json.dumps(meta)), thumb), thumb, 'DefaultTVShows.png', meta=meta, isFolder=False, Fanart=fanart)
                    hasItemsListed = True
            except:
                pass

        self.endDirectory(type='episodes')

        if hidePlus and not hasItemsListed and len(sortedEpisodes) > 0:
            xbmcgui.Dialog().ok('RTL Most', freemium_subscription_needed_errormsg.decode('base64').decode('utf-8'))
            xbmc.executebuiltin("XBMC.Action(Back)")


    def get_video(self, id, meta, image):
        query = base_url + video_link.decode('base64')
        clip = net.request(query % id, headers=self.addAuthenticationHeaders())
        clip = json.loads(clip)
        assets = clip['clips'][0].get('assets')
        if assets is not None and assets != []:
            streams = [i['full_physical_path'] for i in assets]
            from resources.lib.modules import player
            player.player().play(id, streams, image, meta)
        else:
            xbmcgui.Dialog().ok(u'Lej\u00E1tsz\u00E1s sikertelen.', freemium_subscription_needed_errormsg.decode('base64').decode('utf-8'))
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())


    def myFreemiumCodes(self):
        my_uid = xbmcaddon.Addon().getSetting('userid')
        rsp = net.request(freemiumsubsriptions_url.decode('base64') % my_uid, headers=self.addAuthenticationHeaders())

        my_freemium_product_codes = dict()
        for subscription in json.loads(rsp):
            for product in subscription.get("freemium_products", []):
                code = product["code"]
                id = product["id"]
                if code not in my_freemium_product_codes:
                    # list: if the account has multiple subscriptions, they might provide
                    # the same code under different ids (not very likely, but let's prepare)
                    my_freemium_product_codes[code] = list()
                my_freemium_product_codes[code].append(id)

        return my_freemium_product_codes


    def addAuthenticationHeaders(self, headers = dict()):
        headers.update({
            'x-6play-freemium': '1',
            'x-auth-gigya-uid': xbmcaddon.Addon().getSetting('userid'),
            'x-auth-gigya-signature': xbmcaddon.Addon().getSetting('signature'),
            'x-auth-gigya-signature-timestamp': xbmcaddon.Addon().getSetting('s.timestamp'),
            'Origin': 'https://www.rtlmost.hu'
        })
        return headers


    def Login(self):
        t1 = int(xbmcaddon.Addon().getSetting('s.timestamp'))
        t2 = int(time.time())
        update = (abs(t2 - t1) / 3600) >= 24 or t1 == 0
        if update == False:
            return

        login_url = 'https://%s/accounts.login?loginID=%s&password=%s&targetEnv=mobile&format=jsonp&apiKey=%s&callback=jsonp'
        most_baseUrl = 'https://www.rtlmost.hu'

        most_source = net.request(most_baseUrl)
        client_js = re.search('''<script\s*type=['"]module['"]\s*src=['"](\/?client-.+?)['"]''', most_source).group(1)
        api_src = net.request(urlparse.urljoin(most_baseUrl, client_js))
        api_src = re.findall('gigya\s*:\s*(\{[^\}]+\})', api_src)
        api_src = [i for i in api_src if 'login.rtlmost.hu' in i][0]
        api_src = json.loads(re.sub('([{,:])(\w+)([},:])','\\1\"\\2\"\\3', api_src))

        r = net.request(login_url % (api_src['domain'], self.username, self.password, api_src['key']))
        r = re.search('\(([^\)]+)', r).group(1)
        jsonparse = json.loads(r)

        if 'errorMessage' in jsonparse:
            xbmcgui.Dialog().ok(u'Bejelentkez\u00E9si hiba', jsonparse['errorMessage'])
            xbmcaddon.Addon().setSetting('loggedin', 'false')
            xbmcaddon.Addon().setSetting('s.timestamp', '0')
            sys.exit(0)

        xbmcaddon.Addon().setSetting('userid', jsonparse['UID'])
        xbmcaddon.Addon().setSetting('signature', jsonparse['UIDSignature'])
        xbmcaddon.Addon().setSetting('s.timestamp', jsonparse['signatureTimestamp'])
        xbmcaddon.Addon().setSetting('loggedin', 'true')
        xbmcaddon.Addon().setSetting('myfreemiumcodes', json.dumps(self.myFreemiumCodes()))


    def Logout(self):
        dialog = xbmcgui.Dialog()
        if 1 == dialog.yesno(u'RTL Most kijelentkez\u00E9s', u'Val\u00F3ban ki szeretn\u00E9l jelentkezni?', '', ''):
            xbmcaddon.Addon().setSetting('userid', '')
            xbmcaddon.Addon().setSetting('signature', '')
            xbmcaddon.Addon().setSetting('s.timestamp', '0')
            xbmcaddon.Addon().setSetting('loggedin', 'false')
            xbmcaddon.Addon().setSetting('myfreemiumcodes', '')
            xbmcaddon.Addon().setSetting('email', '')
            xbmcaddon.Addon().setSetting('password', '')
            xbmc.executebuiltin("XBMC.Container.Update(path,replace)")
            xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
            dialog.ok('RTL Most', u'Sikeresen kijelentkezt\u00E9l.\nAz adataid t\u00F6r\u00F6lve lettek a kieg\u00E9sz\u00EDt\u0151b\u0151l.')
        
        return


    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None):
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        if thumb == '': thumb = icon
        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None: cm.append((context[0].encode('utf-8'), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
        item = xbmcgui.ListItem(label=name)
        item.addContextMenuItems(cm)
        item.setArt({'icon': thumb, 'thumb': thumb, 'poster': thumb})
        if Fanart == None: Fanart = addonFanart
        item.setProperty('Fanart_Image', Fanart)
        if isFolder == False: item.setProperty('IsPlayable', 'true')
        if not meta == None: item.setInfo(type='Video', infoLabels = meta)
        xbmcplugin.addDirectoryItem(handle=syshandle, url=url, listitem=item, isFolder=isFolder)


    def endDirectory(self, type='addons'):
        xbmcplugin.setContent(syshandle, type)
        #xbmcplugin.addSortMethod(syshandle, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.endOfDirectory(syshandle, cacheToDisc=True)
