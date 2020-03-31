#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Writer (c) 2019, Alejandro A. Popov
# Rev. 1.5.0

import json
import sys
import urllib
import urllib2
import os

import XbmcHelpers
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from urlparse import parse_qsl
from fshelpers.SerialHelper import SerialHelper
from gui.GUIConstructor import GUIConstructor

class OPTIONS:
    addonName = 'plugin.video.fanserials'
    host = u''
    userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0"
    useProxy = False
    proxyProtocol = u''
    proxyUrl = u'169.239.45.37:8080'


# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

def empty():
    return ""

def main_menu():
    GUI = GUIConstructor(_url, _handle)
    GUI.MainMenu(xbmcaddon.Addon(OPTIONS.addonName).getAddonInfo('Path'))

def listing(category, letter):
    helper = SerialHelper(OPTIONS)
    GUI = GUIConstructor(_url, _handle)

    if category == "search":
        keyword = XbmcHelpers.getUserInput(u'Поиск')

        if keyword:
            keyword = urllib.unquote_plus(keyword)
            page = helper.getPageContent(OPTIONS.host + "/search/?query=" + keyword)
            serials = helper.parseSearchResults(page)
            GUI.SearchResults(serials)
        else:
            main_menu()

    elif category == "last":
        page = helper.getPageContent(OPTIONS.host)
        serials = helper.parseLast(page)
        GUI.NewEpisodes(serials)

    elif category == "popular":
        page = helper.getPageContent(OPTIONS.host)
        serials = helper.parsePopular(page)
        GUI.ListSerials(serials)

    elif category == "new":
        page = helper.getPageContent(OPTIONS.host)
        serials = helper.parseNew(page)
        GUI.ListSerials(serials)

    elif category == "random":
        page = helper.getPageContent(OPTIONS.host)
        serial = helper.getRandom(page)
        details(serial)
    
    elif category == "all":
        if letter:
            page = helper.getPageContent(OPTIONS.host)
            serial = helper.parseByLetter(page, letter)
        GUI.AlphabeticList(letter)

def details(address):
    helper = SerialHelper(OPTIONS)
    GUI = GUIConstructor(_url, _handle)

    page = helper.getPageContent(OPTIONS.host + address)
    serialInfo = helper.parseSingle(page, address)
    GUI.SerialInfoSeasons(serialInfo)

def episodes(address, season):
    helper = SerialHelper(OPTIONS)
    GUI = GUIConstructor(_url, _handle)

    page = helper.getPageContent(OPTIONS.host + address)
    season = helper.parseEpisodes(page, season, address)

    GUI.SeasonEpisodes(season)

def translates(address, poster):
    helper = SerialHelper(OPTIONS)
    GUI = GUIConstructor(_url, _handle)

    page = helper.getPageContent(OPTIONS.host + address)
    episode = helper.parseTranslates(page, address, poster)

    if len(episode.translates) and episode.translates[0].get('player') == OPTIONS.host+'/limited/':
        page = helper.getPageContent(OPTIONS.host + address, useProxy=True)
        episode = helper.parseTranslates(page, address, poster)

    GUI.EpisodeTranslates(episode)

def quality(address, title, poster):
    helper = SerialHelper(OPTIONS)
    GUI = GUIConstructor(_url, _handle)

    pid = address.split('/')[-1]

    page = helper.getPageContent(address, OPTIONS.host)
    qualityList = helper.parseHLSPlaylist(page, pid)

    subtitles = helper.parseSubtitles(page, pid)
    GUI.EpisodeQualities(qualityList, address, title, poster, subtitles)

def play(url, subtitles):
    """
    Play a video by the provided path.
    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=url)
    play_item.setSubtitles(subtitles.values())
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def router(paramstring):
    xbmc.log("ROUTER:REQ: {0}".format(paramstring), xbmc.LOGNOTICE)
    xbmc.log("ROUTER:HANDLE: {0}".format(_handle), xbmc.LOGNOTICE)
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'listing':
            letter = params['letter'] if 'letter' in params.keys() else u''
            listing(params['category'], letter)
        elif params['action'] == 'details':
            details(params['anchor'])
        elif params['action'] == 'episodes':
            episodes(params['anchor'], params['season'])
        elif params['action'] == 'translates':
            translates(params['anchor'], params['poster'])
        elif params['action'] == 'quality':
            quality(params['anchor'], params['title'], params['poster'])
        elif params['action'] == 'play':
            play(params['anchor'], json.loads(params['subtitles']))
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        main_menu()

if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    addon = xbmcaddon.Addon(OPTIONS.addonName)
    OPTIONS.host = "http://{0}".format(addon.getSetting('domain'))
    OPTIONS.useProxy = addon.getSetting('use_proxy')
    OPTIONS.proxyProtocol = addon.getSetting('protocol')
    OPTIONS.proxyUrl = addon.getSetting('proxy_url')

    router(sys.argv[2][1:])

# liz.setInfo(type='Video', infoLabels={
#     'genre': 'genre', # string (Comedy) or list of strings (["Comedy", "Animation", "Drama"])
#     'country': 'country', # string (Germany) or list of strings (["Germany", "Italy", "France"])
#     'year': 2000, # integer (2009)
#     'episode': 1, # integer (4)
#     'season': 2, # integer (1)
#     'sortepisode': 3, # integer (4)
#     'sortseason': 4, # integer (1)
#     'episodeguide': 'episodeguide', # string (Episode guide)
#     'showlink': 'showlink', # string (Battlestar Galactica) or list of strings (["Battlestar Galactica", "Caprica"])
#     'top250': 5, # integer (192)
#     'setid': 6, # integer (14)
#     'tracknumber': 7, # integer (3)
#     'rating': 8.1, # float (6.4) - range is 0..10
#     'userrating': 9, # integer (9) - range is 1..10 (0 to reset)
#     'playcount': 10, # integer (2) - number of times this item has been played
#     'overlay': 0, # integer (2) - range is 0..7. See Overlay icon types for values
#     'cast': (['Cast']), # list (["Michal C. Hall","Jennifer Carpenter"]) - if provided a list of tuples cast will be interpreted as castandrole
#     'castandrole': (['Cast', 'Role']), # list of tuples ([("Michael C. Hall","Dexter"),("Jennifer Carpenter","Debra")])
#     'director': 'director', # string (Dagur Kari) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"])
#     'mpaa': 'mpaa', # string (PG-13)
#     'plot': 'plot', # string (Long Description)
#     'plotoutline': 'plotoutline', # string (Short Description)
#     'title': 'title', # string (Big Fan)
#     'originaltitle': 'originaltitle', # string (Big Fan)
#     'sorttitle': 'sorttitle', # string (Big Fan)
#     'duration': 11, # integer (245) - duration in seconds
#     'studio': 'studio', # string (Warner Bros.) or list of strings (["Warner Bros.", "Disney", "Paramount"])
#     'tagline': 'tagline', # string (An awesome movie) - short description of movie
#     'writer': 'writer', # string (Robert D. Siegel) or list of strings (["Robert D. Siegel", "Jonathan Nolan", "J.K. Rowling"])
#     'tvshowtitle': 'tvshowtitle', # string (Heroes)
#     'premiered': 'premiered', # string (2005-03-04)
#     'status': 'status', # string (Continuing) - status of a TVshow
#     'set': 'set', # string (Batman Collection) - name of the collection
#     'setoverview': 'setoverview', # string (All Batman movies) - overview of the collection
#     'tag': 'tag', # string (cult) or list of strings (["cult", "documentary", "best movies"]) - movie tag
#     'imdbnumber': 'imdbnumber', # string (tt0110293) - IMDb code
#     'code': 'code', # string (101) - Production code
#     'aired': 'aired', # string (2008-12-07)
#     'credits': 'credits', # string (Andy Kaufman) or list of strings (["Dagur Kari", "Quentin Tarantino", "Chrstopher Nolan"]) - writing credits
#     'lastplayed': 'lastplayed', # string (Y-m-d h:m:s = 2009-04-05 23:16:04)
#     'album': 'album', # string (The Joshua Tree)
#     'artist': (['artist']), # list (['U2'])
#     'votes': 'votes', # string (12345 votes)
#     'path': 'path', # string (/home/user/movie.avi)
#     'trailer': 'trailer', # string (/home/user/trailer.avi)
#     'dateadded': 'dateadded', # string (Y-m-d h:m:s = 2009-04-05 23:16:04)
#     'mediatype': 'video', # string - "video", "movie", "tvshow", "season", "episode" or "musicvideo"
#     'dbid': 12 # integer (23) - Only add this for items which are part of the local db. You also need to set the correct 'mediatype'!
# })