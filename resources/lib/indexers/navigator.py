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


import os,sys,re,xbmc,xbmcgui,xbmcplugin,xbmcaddon,urllib,json,time,locale
from resources.lib.modules import net
from  collections import OrderedDict
if sys.version_info[0] == 3:
    import urllib.parse as urlparse
    from urllib.parse import quote_plus
else:
    import urlparse
    from urllib import quote_plus

from resources.lib.modules.utils import py2_encode


sysaddon = sys.argv[0] ; syshandle = int(sys.argv[1])
addon = xbmcaddon.Addon
addonFanart = addon().getAddonInfo('fanart')

base_url = 'https://pc.middleware.6play.fr/6play/v2/platforms/m6group_web/services/rtlhu_rtl_most'
img_link = 'https://images.6play.fr/v2/images/%s/raw'
cat_link = '/folders?limit=100&offset=0'
prog_link = '/folders/%s/programs?limit=100&offset=0&csa=5&with=parentcontext'
episode_link = '/programs/%s/videos?csa=5&with=clips,freemiumpacks&type=vi,vc,playlist&limit=50&offset=0&subcat=%s&sort=subcat'
episode_subcat_link = '/programs/%s?with=links,subcats,rights'
video_link = '/videos/%s?csa=5&with=clips,freemiumpacks,program_images,service_display_images'
livechannels_link = '/live?channel=rtlhu_rtl_klub,rtlhu_rtl_ii,rtlhu_rtl_gold,rtlhu_cool,rtlhu_rtl_plus,rtlhu_film_plus,rtlhu_sorozat_plus,rtlhu_muzsika_tv&with=freemiumpacks,service_display_images,nextdiffusion,extra_data'
live_stream_link = '/live?channel=%s&with=freemiumpacks,service_display_images,nextdiffusion,extra_data'
freemiumsubscriptions_url = 'https://6play-users.6play.fr/v2/platforms/m6group_web/users/%s/freemiumsubscriptions'
freemium_subscription_needed_errormsg = 'A hozzáféréshez RTL Most+ előfizetés szükséges.\nRészletek: https://www.rtlmost.hu/premium'
deviceID_url = 'https://e.m6web.fr/info?customer=rtlhu'

class navigator:
    def __init__(self):
        try:
            locale.setlocale(locale.LC_ALL, "")
        except:
            pass
        self.username = xbmcaddon.Addon().getSetting('email').strip()
        self.password = xbmcaddon.Addon().getSetting('password').strip()

        if not (self.username and self.password) != '':
            if xbmcgui.Dialog().ok('RTL Most', u'A kieg\u00E9sz\u00EDt\u0151 haszn\u00E1lat\u00E1hoz add meg a bejelentkez\u00E9si adataidat.'):
                xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
                addon(addon().getAddonInfo('id')).openSettings()                
            sys.exit(0)
        if xbmcaddon.Addon().getSetting('deviceid') == "":
            r = net.request(deviceID_url)
            jsonparse = json.loads(r)
            xbmcaddon.Addon().setSetting('deviceid', jsonparse['device_id'])
        self.Login()


    def root(self):
        query = base_url + cat_link
        categories = net.request(query)

        self.addDirectoryItem('Élő adás', 'liveChannels', '', 'DefaultTVShows.png')
        for i in json.loads(categories):
            self.addDirectoryItem(py2_encode(i['name']), 'programs&url=%s' % str(i['id']), '', 'DefaultTVShows.png')

        self.endDirectory()


    def liveChannels(self):
        liveChannels = {'rtlhu_rtl_klub': 'RTL Klub', 'rtlhu_rtl_ii': 'RTL II', 'rtlhu_cool': 'Cool TV', 'rtlhu_rtl_gold': 'RTL Gold', 'rtlhu_rtl_plus': 'RTL+', 'rtlhu_film_plus': 'Film+', 'rtlhu_sorozat_plus': 'Sorozat+', 'rtlhu_muzsika_tv': 'Muzsika TV'}
        query = base_url + livechannels_link
        lives = net.request(query)
        for (i,j) in json.loads(lives, object_pairs_hook=OrderedDict).items():
            self.addDirectoryItem("[B]"+liveChannels[i] + "[/B] - " + py2_encode(j[0]['title']) + "  [COLOR gold][" + py2_encode(j[0]['diffusion_start_date'])[11:-3] + " - " + py2_encode(j[0]['diffusion_end_date'])[11:-3] + "][/COLOR]", 'liveChannel&url=%s' % i, '', 'DefaultTVShows.png')
        self.endDirectory()

    def liveChannel(self, channel):
        headers = {
            'x-6play-freemium': '1',
            'x-auth-gigya-uid': xbmcaddon.Addon().getSetting('userid'),
            'x-auth-gigya-signature': xbmcaddon.Addon().getSetting('signature'),
            'x-auth-gigya-signature-timestamp': xbmcaddon.Addon().getSetting('s.timestamp'),
            'Origin': 'https://www.rtlmost.hu'}
        query = base_url + live_stream_link
        live = net.request(query % channel, headers=headers)
        live = json.loads(live)
        assets = live[channel][0]['live']['assets']
        if assets != []:
            streams = [{'container': 'live', 'path': i['full_physical_path']} for i in assets]
            meta = {'title': live[channel][0]['title']}
            from resources.lib.modules import player
            player.player().play(channel, streams, None, json.dumps(meta))
        else:
            xbmcgui.Dialog().ok(u'Lej\u00E1tsz\u00E1s sikertelen.', freemium_subscription_needed_errormsg)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())

    def programs(self, id):
        query = base_url + prog_link
        programs = net.request(query % id)
        prgs={}
        for i in json.loads(programs):
            prg = {}
            title = py2_encode(i['title'])
            try: thumb = img_link % [x['external_key'] for x in i['images'] if x['role'] == 'logo'][0]
            except: thumb = ''
            try: fanart = img_link % [x['external_key'] for x in i['images'] if x['role'] == 'mea'][0]
            except: fanart = None
            id = str(i['id'])
            plot = py2_encode(i['description'])
            extraInfo = ""
            if xbmcaddon.Addon().getSetting('show_content_summary') == 'true':
                try:
                    if (i['count']['vi']>0):
                        extraInfo = " (%d %s)" % (i['count']['vi'], py2_encode(i['program_type_wording']['plural']) if i['program_type_wording'] != None else 'Teljes adás')
                    else:
                        extraInfo = " (%d előzetes és részletek)" % (i['count']['vc'])
                except: pass
            prg = {'extraInfo': extraInfo, 'id': id, 'fanart': fanart, 'thumb': thumb, 'plot': plot}
            prgs[title] = prg
        prgTitles = list(prgs.keys())
        if (xbmcaddon.Addon().getSetting('sort_programs') == 'true'):
            prgTitles.sort(key=locale.strxfrm)
        for prg in prgTitles:
            #self.addDirectoryItem("%s[I][COLOR silver]%s[/COLOR][/I]" % (title, extraInfo), 'episodes&url=%s&fanart=%s' % (id, fanart), thumb, 'DefaultTVShows.png', Fanart=fanart, meta={'plot': plot})
            self.addDirectoryItem("%s[I][COLOR silver]%s[/COLOR][/I]" % (prg, prgs[prg]['extraInfo']), 'episodes&url=%s&fanart=%s' % (prgs[prg]['id'], prgs[prg]['fanart']), prgs[prg]['thumb'], 'DefaultTVShows.png', Fanart=prgs[prg]['fanart'], meta={'plot': prgs[prg]['plot']})

        self.endDirectory(type='tvshows')

    def episodes(self, id, fanart, subcats=None):
        try: myfreemiumcodes = json.loads(xbmcaddon.Addon().getSetting('myfreemiumcodes'))
        except: myfreemiumcodes = {}

        class title_sorter:
            PATTERNS_IN_PRIORITY_ORDER = [
                re.compile(r'^(?P<YEAR>\d{2,4})-(?P<MONTH>\d{2})-(?P<DAY>\d{2})$'),          # Date-only
                re.compile(r'^(?P<SEASON>\d+)\. évad (?P<EPISODE>\d+)\. rész$'),             # Only Season + Episode
                re.compile(r'^(?P<EPISODE>\d+)\. rész$'),                                    # Only Episode
                re.compile(r'.* (?P<YEAR>\d{2,4})-(?P<MONTH>\d{2})-(?P<DAY>\d{2})$'),        # Title + Date
                re.compile(r'.* \((?P<YEAR>\d{2,4})-(?P<MONTH>\d{2})-(?P<DAY>\d{2})\)$'),    # Title + (Date)
                re.compile(r'^(?P<YEAR>\d{2,4})-(?P<MONTH>\d{2})-(?P<DAY>\d{2}) .*'),        # Date + Title
                re.compile(r'.* (?P<SEASON>\d+)\. évad (?P<EPISODE>\d+)\. rész$'),           # Title + Season + Episode
                re.compile(r'.* (?P<EPISODE>\d+)\. rész$')                                   # Title + Episode
            ]

            @classmethod
            def find_first_common_pattern(cls, episodes):
                xbmcgui.Dialog().ok("a", "itt")
                for pattern in cls.PATTERNS_IN_PRIORITY_ORDER:
                    if all([ pattern.match(ep.get('title', '')) is not None for ep in episodes ]):
                        return pattern
                return None

            @classmethod
            def all_match_same_pattern(cls, episodes):
                return cls.find_first_common_pattern(episodes) is not None

            @classmethod
            def sorted(cls, episodes, reverse):
                def key(episode):
                    m = pattern.match(episode.get('title', ''))
                    return tuple(int(i) for i in m.groups())
                pattern = cls.find_first_common_pattern(episodes)
                return sorted(episodes, key=lambda ep: key(ep), reverse=reverse)

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
            query = base_url + episode_subcat_link
            subcats = net.request(query % id)
            subcats = [i for i in json.loads(subcats)['program_subcats'] if 'id' in i]

        if len(subcats) > 1:
            # the show has multiple seasons or subcategories, list these, and let the user to choose one
            for item in subcats:
                str(item['id'])
                self.addDirectoryItem(py2_encode(item['title']), 'episodes&url=%s&fanart=%s&subcats=%s' % (id, fanart, quote_plus(json.dumps([item]))), '', 'DefaultFolder.png', Fanart=fanart)
            self.endDirectory(type='seasons')
            return

        query = base_url + episode_link
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
            elif title_sorter.all_match_same_pattern(episodes):
                sortedEpisodes = title_sorter.sorted(episodes, reverse=reverseSorting)
            else:
                sortedEpisodes = sorted(episodes, key=getClipID, reverse=reverseSorting)

        hasItemsListed = False
        for item in sortedEpisodes:
            try:
                eligible = userIsEligibleToPlayEpisode(item)
                if (not hidePlus) or eligible:
                    title = py2_encode(item['title'])
                    if not eligible:
                        title = '[COLOR red]' + title + ' [B](Most+)[/B][/COLOR]'
                    plot = py2_encode(item['description'])
                    duration = str(item['duration'])
                    try: thumb = img_link % [i['external_key'] for i in item['images'] if i['role'] == 'vignette'][0]
                    except: thumb = img_link % item['display_image']['external_key']
                    thumb = thumb
                    assets = item['clips'][0].get('assets')
                    clip_id = py2_encode(item['id'])
                    meta = {'title': title, 'plot': plot, 'duration': duration}
                    self.addDirectoryItem(title, 'play&url=%s&meta=%s&image=%s' % (quote_plus(clip_id), quote_plus(json.dumps(meta)), thumb), thumb, 'DefaultTVShows.png', meta=meta, isFolder=False, Fanart=fanart)
                    hasItemsListed = True
            except:
                pass

        self.endDirectory(type='episodes')

        if hidePlus and not hasItemsListed and len(sortedEpisodes) > 0:
            xbmcgui.Dialog().ok('RTL Most', freemium_subscription_needed_errormsg)
            xbmc.executebuiltin("XBMC.Action(Back)")


    def get_video(self, id, meta, image):
        query = base_url + video_link
        clip = net.request(query % id, headers=self.addAuthenticationHeaders())
        clip = json.loads(clip)
        assets = clip['clips'][0].get('assets')
        if assets is not None and assets != []:
            streams = [{'container': i['video_container'], 'path': i['full_physical_path']} for i in assets]
            from resources.lib.modules import player
            player.player().play(id, streams, image, meta)
        else:
            xbmcgui.Dialog().ok(u'Lej\u00E1tsz\u00E1s sikertelen.', freemium_subscription_needed_errormsg)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), False, xbmcgui.ListItem())


    def myFreemiumCodes(self):
        my_uid = xbmcaddon.Addon().getSetting('userid')
        rsp = net.request(freemiumsubscriptions_url % my_uid, headers=self.addAuthenticationHeaders())

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

        r = net.request(login_url % (api_src['domain'], self.username, quote_plus(self.password), api_src['key']))
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

        r = net.request(deviceID_url)
        jsonparse = json.loads(r)
        xbmcaddon.Addon().setSetting('deviceid', jsonparse['device_id'])


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
            xbmcaddon.Addon().setSetting('deviceid', '')
            xbmc.executebuiltin("XBMC.Container.Update(path,replace)")
            xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
            dialog.ok('RTL Most', u'Sikeresen kijelentkezt\u00E9l.\nAz adataid t\u00F6r\u00F6lve lettek a kieg\u00E9sz\u00EDt\u0151b\u0151l.')
        
        return


    def addDirectoryItem(self, name, query, thumb, icon, context=None, queue=False, isAction=True, isFolder=True, Fanart=None, meta=None):
        url = '%s?action=%s' % (sysaddon, query) if isAction == True else query
        if thumb == '': thumb = icon
        cm = []
        if queue == True: cm.append((queueMenu, 'RunPlugin(%s?action=queueItem)' % sysaddon))
        if not context == None: cm.append((py2_encode(context[0]), 'RunPlugin(%s?action=%s)' % (sysaddon, context[1])))
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
