#!/usr/bin/python
# -*- coding: utf-8 -*-

import XbmcHelpers
import xbmc
import xbmcplugin
import xbmcgui

import json
import os
import string
import urllib

class GUIConstructor():

    anchor = ""
    handler = -1

    MAINMENU = [
        {
            'label': u'Поиск',
            'action': 'listing',
            'category': 'search'
        },
        {
            'label': u'Новые серии',
            'action': 'listing',
            'category': 'last'
        },
        {
            'label': u'Популярное',
            'action': 'listing',
            'category': 'popular'
        },
        {
            'label': u'Новинки',
            'action': 'listing',
            'category': 'new'
        },
        {
            'label': u'Случайный сериал',
            'action': 'listing',
            'category': 'random'
        },
        {
            'label': u'Все',
            'action': 'listing',
            'category': 'all'
        },
    ]

    def __init__(self, anchor, handler):
        self.anchor = anchor
        self.handler = handler

    def getActionLink(self, **kwargs):
        """
        Create a URL for calling the plugin recursively from the given set of keyword arguments.
            :param kwargs: "argument=value" pairs
            :type kwargs: dict
            :return: plugin call URL
            :rtype: str
        """
        for key in kwargs:
            if (isinstance(kwargs[key], str) or isinstance(kwargs[key], unicode)):
                kwargs[key] = kwargs[key].encode('utf-8')

        return '{0}?{1}'.format(self.anchor, urllib.urlencode(kwargs))
    
    def MainMenu(self, rootPath):
        """
        MAIN MENU
        """
        xbmcplugin.setPluginCategory(self.handler, u'FanSerials')
        fanArt = os.path.join(rootPath, "fanart.jpg")

        for menuItem in self.MAINMENU:
            list_item = xbmcgui.ListItem(label=menuItem['label'])
            list_item.setArt({'fanart': fanArt})
            url = self.getActionLink(action=menuItem['action'], category=menuItem['category'])
            xbmcplugin.addDirectoryItem(self.handler, url, list_item, True)

        # xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.setContent(self.handler, 'videos')
        xbmcplugin.endOfDirectory(self.handler)

    def SearchResults(self, serials):
        """
        SEARCH RESULTS
        """
        xbmcplugin.setPluginCategory(self.handler, u'Поиск')

        for item in serials:
            list_item = xbmcgui.ListItem(label=item.title)
            url = self.getActionLink(action='details', anchor=item.link)
            list_item.setArt({'thumb': item.poster, 'icon': item.poster, 'fanart': item.poster})
            list_item.setInfo(type='Video', infoLabels={
                'genre': item.originalTitle,
                'plot': item.description,
                'title': item.title,
                'originaltitle': item.originalTitle,
                'tvshowtitle': item.originalTitle,
                'mediatype': 'movie'
            })
            xbmcplugin.addDirectoryItem(self.handler, url, list_item, True)

        xbmcplugin.setContent(self.handler, 'movies')
        xbmcplugin.endOfDirectory(self.handler)

    def NewEpisodes(self, serials):
        """
        NEW EPISODES
        """
        xbmcplugin.setPluginCategory(self.handler, u'Новые эпизоды')

        for item in serials:
            list_item = xbmcgui.ListItem(label=item.title)
            url = self.getActionLink(action='translates', anchor=item.link, poster=item.poster)
            list_item.setArt({'thumb': item.poster, 'icon': item.poster, 'fanart': item.poster})
            list_item.setInfo(type='Video', infoLabels={
                'title': item.title,
                'plot': ", ".join(item.translates), 
                'tvshowtitle': item.description,
                'mediatype': 'episode'
            })
            xbmcplugin.addDirectoryItem(self.handler, url, list_item, True)

        xbmcplugin.setContent(self.handler, 'episodes')
        xbmcplugin.endOfDirectory(self.handler)

    def ListSerials(self, serials):
        """
        LIST SERIALS
        """
        xbmcplugin.setPluginCategory(self.handler, u'Сериалы')

        for item in serials:
            list_item = xbmcgui.ListItem(label=item.title)
            url = self.getActionLink(action='details', anchor=item.link)
            list_item.setArt({'thumb': item.poster, 'icon': item.poster, 'fanart': item.poster})
            list_item.setInfo(type='Video', infoLabels={
                'title': item.title,
                'genre': item.genre, 
                'mediatype': 'movie'
            })
            xbmcplugin.addDirectoryItem(self.handler, url, list_item, True)

        xbmcplugin.setContent(self.handler, 'movies')
        xbmcplugin.endOfDirectory(self.handler)

    def AlphabeticList(self, letter):
        """
        ALPHABETIC LIST
        """
        xbmcplugin.setPluginCategory(self.handler, u'Алфавитный список')

        chars = list(u"#АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
        for char in chars:
            list_item = xbmcgui.ListItem(label=char)
            url = self.getActionLink(action='listing', category="all", letter=char)
            xbmcplugin.addDirectoryItem(self.handler, url, list_item, True)

        xbmcplugin.setContent(self.handler, 'videos')
        xbmcplugin.endOfDirectory(self.handler)

    def SerialInfoSeasons(self, serial):
        """
        SERIAL INFO + SEASONS LIST
        """
        xbmcplugin.setPluginCategory(self.handler, serial.link)

        for item in serial.seasons:
            list_item = xbmcgui.ListItem(label=u"{0} сезон".format(item))
            url = self.getActionLink(action='episodes', anchor=serial.seasons[item], season=item)
            list_item.setArt({'thumb': serial.poster, 'icon': serial.poster, 'fanart': serial.poster})
            list_item.setInfo(type='Video', infoLabels={
                'title': u"{0} сезон".format(item),
                'plot': serial.fullDescription, 
                'tvshowtitle': u"{0} / {1}".format(serial.title, serial.originalTitle),
                'duration': serial.duration,
                'mediatype': 'episode'
            })

            xbmcplugin.addDirectoryItem(self.handler, url, list_item, True)

        xbmcplugin.setContent(self.handler, 'episodes')
        xbmcplugin.endOfDirectory(self.handler)

    def SeasonEpisodes(self, season):
        """
        EPISODES FOR SEASON
        """
        xbmcplugin.setPluginCategory(self.handler, season.link + '/s-' + season.number)

        for episode in season.episodes:
            list_item = xbmcgui.ListItem(label=episode.title)
            url = self.getActionLink(action='translates', anchor=episode.link, poster=episode.poster)
            list_item.setArt({'thumb': episode.poster, 'icon': episode.poster, 'fanart': episode.poster})
            list_item.setInfo(type='Video', infoLabels={
                'title': episode.title,
                'plot': season.description, 
                'tvshowtitle': season.serialTitle,
                'duration': season.episodeDuration,
                'mediatype': 'episode'
            })

            xbmcplugin.addDirectoryItem(self.handler, url, list_item, True)

        xbmcplugin.setContent(self.handler, 'episodes')
        xbmcplugin.endOfDirectory(self.handler)

    def EpisodeTranslates(self, episode):
        """
        TRANSLATES FOR EPISODE
        """
        xbmcplugin.setPluginCategory(self.handler, episode.link + '/translates')

        for translate in episode.translates:
            list_item = xbmcgui.ListItem(label=translate.get('name'))
            url = self.getActionLink(action='quality', anchor=translate.get('player'), title=episode.title, poster=episode.poster)
            list_item.setArt({'thumb': episode.poster, 'icon': episode.poster, 'fanart': episode.poster})
            list_item.setInfo(type='Video', infoLabels={
                'title': translate.get('name'),
                'plot': episode.description, 
                'tvshowtitle': episode.title,
                'mediatype': 'episode'
            })

            xbmcplugin.addDirectoryItem(self.handler, url, list_item, True)

        xbmcplugin.setContent(self.handler, 'episodes')
        xbmcplugin.endOfDirectory(self.handler)
    
    def EpisodeQualities(self, qualitiesList, episodeLink, episodeTitle, episodePoster, subtitles):
        """
        LIST OF THE QUALITIES FOR EPISODE
        """
        xbmcplugin.setPluginCategory(self.handler, episodeLink + '/qualities')

        for key in qualitiesList:
            list_item = xbmcgui.ListItem(label=key)
            url = self.getActionLink(action='play', anchor=qualitiesList[key], subtitles=json.dumps(subtitles))
            list_item.setArt({'thumb': episodePoster, 'icon': episodePoster, 'fanart': episodePoster})
            list_item.setInfo(type='Video', infoLabels={
                'title': key,
                'tvshowtitle': episodeTitle,
                'mediatype': 'video'
            })
            list_item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self.handler, url, list_item, False)

        xbmcplugin.setContent(self.handler, 'episodes')
        xbmcplugin.endOfDirectory(self.handler)
