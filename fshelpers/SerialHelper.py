#!/usr/bin/python
# -*- coding: utf-8 -*-

import io
import json
import random
import re
import string
import os
import urllib
import urllib2

import XbmcHelpers
import xbmc

class Serial():
    # Public fields
    title = u''
    originalTitle = u''
    poster = u''
    description = u''
    fullDescription = u''
    dateCreated = u''
    genre = u''
    link = u''
    transtates = []
    seasons = {}
    duration = 0

class Season():
    # Public fields
    number = 0
    serialTitle = u''
    link = u''
    description = u''
    episodeDuration = u''
    episodes = []

class Episode():
    # Public fields
    season = u''
    number = u''
    title = u''
    description = u''
    poster = u''
    link = u''
    translates = {}

class SerialHelper():

    _userAgent = u''
    _useProxy = False
    _proxyProtocol = ''
    _proxyUrl = u''

    def __init__(self, options):
        self._userAgent = options.userAgent
        self._useProxy = options.useProxy
        self._proxyProtocol = options.proxyProtocol
        self._proxyUrl = options.proxyUrl

    def getPageContent(self, url, referer=None, useProxy=False):
        """
        GET HTTP CONTENT
        """
        self._proxyUrl = "45.251.74.228"
        xbmc.log("URL_LOADER: {0} [REF={1};PROXY={2}={3}]".format(url, referer, useProxy, self._proxyUrl), xbmc.LOGNOTICE)
        headers = {
            'User-Agent': self._userAgent
        }
        if referer:
            headers["Referer"] = referer

        if (useProxy):
            params = {
                'u' : url
            }
            data = urllib.urlencode(params)
            request = urllib2.Request(url="http://sd32.com/browse.php", data=data, headers=headers)
        else:
            request = urllib2.Request(url=url, headers=headers)
        
        response = urllib2.urlopen(request).read()
        # xbmc.log("URL_LOADER: {0}".format(response), xbmc.LOGNOTICE)

        # request = urllib2.Request(url=url, headers=headers)

        # if (useProxy and self._useProxy):
        #     proxy = urllib2.ProxyHandler({
        #         'http': "{0}://{1}".format(self._proxyProtocol, self._proxyUrl)
        #     })
        #     opener = urllib2.build_opener(proxy)
        #     response = opener.open(request).read()
        # else:
        #     response = urllib2.urlopen(request).read()

        return response

    def parseSearchResults(self, pageContent):
        """
        PARSE SEARCH RESULTS
        """
        result = []

        resultsList = XbmcHelpers.parseDOM(pageContent, "div", attrs={"class": "item-search-serial"})

        for item in resultsList:
            serial = Serial()

            poster = XbmcHelpers.parseDOM(item, "img", ret="src")
            serial.poster = poster[0] if len(poster) else u''

            link = XbmcHelpers.parseDOM(item, "a", ret="href")
            serial.link = link[0] if len(link) else u''

            title = XbmcHelpers.parseDOM(item, "h2")
            serial.title = XbmcHelpers.stripTags(title[0]) if len(title) else u''

            origin = XbmcHelpers.parseDOM(item, "div", attrs={"class": "name-origin-search"})
            serial.originalTitle = XbmcHelpers.stripTags(origin[0]) if len(origin) else u''

            description = XbmcHelpers.parseDOM(item, "div", attrs={"class": "textailor"})
            serial.description = XbmcHelpers.stripTags(description[0]) if len(description) else u''

            result.append(serial)

        return result
    
    def parseLast(self, pageContent):
        """
        PARSE LAST ADDED EPISODES
        """
        result = []

        container = XbmcHelpers.parseDOM(pageContent, "div", attrs={"class": "data-main-episodes-slider block-new-series"})
        items = XbmcHelpers.parseDOM(container[0], "div", attrs={"class": "item"})
        for i, item in enumerate(items):
            titleNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-title"})
            imgNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-img"}, ret="style")
            linkNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-img"})
            linkNode = XbmcHelpers.parseDOM(linkNode, "a", ret="href")

            descriptionNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-description"})
            translateNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "serial-translate"})
            
            if len(titleNode) > 0:
                serial = Serial()
                
                serial.title = XbmcHelpers.stripTags(titleNode[0])
                serial.translates = XbmcHelpers.parseDOM(translateNode[0], "a")
                serial.description = XbmcHelpers.stripTags(descriptionNode[0])
                serial.poster = imgNode[0].replace("');", "").replace("background-image: url('", "")
                serial.link = linkNode[0]
                
                result.append(serial)

        return result

    def parsePopular(self, pageContent):
        """
        PARSE POPULAR SERIALS
        """
        result = []

        container = XbmcHelpers.parseDOM(pageContent, "div", attrs={"id": "popularTab"})
        items = XbmcHelpers.parseDOM(container[0], "div", attrs={"class": "item"})
        for i, item in enumerate(items):
            titleNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-title"})
            linkNode = XbmcHelpers.parseDOM(titleNode, "a", ret="href")
            genreNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-genre"})
            imgNode = XbmcHelpers.parseDOM(item, "img", ret="src")
            
            if len(titleNode) > 0:
                serial = Serial()
                
                serial.title = XbmcHelpers.stripTags(titleNode[0])
                serial.genre = XbmcHelpers.stripTags(genreNode[0]) if len(genreNode) else ""
                serial.poster = imgNode[0]
                serial.link = linkNode[0]
                
                result.append(serial)

        return result

    def parseNew(self, pageContent):
        """
        PARSE NEW SERIALS
        """
        result = []

        container = XbmcHelpers.parseDOM(pageContent, "div", attrs={"id": "newsTab"})
        items = XbmcHelpers.parseDOM(container[0], "div", attrs={"class": "item"})
        for i, item in enumerate(items):
            titleNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-title"})
            linkNode = XbmcHelpers.parseDOM(titleNode, "a", ret="href")
            genreNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-genre"})
            imgNode = XbmcHelpers.parseDOM(item, "img", ret="src")
            if len(titleNode) > 0:
                serial = Serial()

                serial.title = XbmcHelpers.stripTags(titleNode[0])
                serial.genre = XbmcHelpers.stripTags(genreNode[0]) if len(genreNode) else ""
                serial.poster = imgNode[0]
                serial.link = linkNode[0]

                result.append(serial)

        return result

    def getRandom(self, pageContent):
        container = XbmcHelpers.parseDOM(pageContent, "div", attrs={"id": "alphabet-list"})
        items = XbmcHelpers.parseDOM(container[0], "li", attrs={"class": "literal__item not-loaded"})
        itemsList = []
        for i, item in enumerate(items):
            link = XbmcHelpers.parseDOM(item, "a", ret="href")
            itemsList.append(link[0])

        return random.choice(itemsList)

    def parseByLetter(self, pageContent, letter):
        result = []
        chars = list(u"#АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
        index = 0

        for i, char in enumerate(chars):
            if (letter.decode('utf-8') == char):
                index = i
                break

        container = XbmcHelpers.parseDOM(pageContent, "div", attrs={"id": "alphabet-list"})
        subcontainer = XbmcHelpers.parseDOM(container[0], "div", attrs={"data-id": str(index)})
        items = XbmcHelpers.parseDOM(subcontainer[0], "li", attrs={"class": "literal__item not-loaded"})

        itemsList = []
        for i, item in enumerate(items):
            link = XbmcHelpers.parseDOM(item, "a", ret="href")
            itemsList.append(link[0])

        return result

    def parseSingle(self, pageContent, serialUrl):
        serial = Serial()

        # TITLE
        titleNode = XbmcHelpers.parseDOM(pageContent, "h1", attrs={"class": "page-title"})
        serial.title = XbmcHelpers.stripTags(titleNode[0])

        infoContainer = XbmcHelpers.parseDOM(pageContent, "div", attrs={"id": "o-seriale"})

        # POSTER
        posterNode = XbmcHelpers.parseDOM(infoContainer[0], "div", attrs={"class": "field-poster"})
        serial.poster = XbmcHelpers.parseDOM(posterNode[0], "img", ret="src")[0]

        # DESCRIPTION
        descriptionNode = XbmcHelpers.parseDOM(infoContainer, "div", attrs={"itemprop": "description"})
        serial.description = XbmcHelpers.stripTags(descriptionNode[0])

        infoList = XbmcHelpers.parseDOM(infoContainer, "ul", attrs={"class": "info-list"})
        listItems = XbmcHelpers.parseDOM(infoList, "li")
        for row in listItems:
            rowTitle = XbmcHelpers.parseDOM(row, "div", attrs={"class": "field-label"})
            rowText = XbmcHelpers.parseDOM(row, "div", attrs={"class": "field-text"})
            serial.fullDescription += u"{0} {1}\n".format(XbmcHelpers.stripTags(rowTitle[0]), XbmcHelpers.stripTags(rowText[0]))
            if rowTitle[0] == u"Актёры:":
                break

        serial.fullDescription += u"\n" + serial.description

        # DURATON
        durationRow = listItems[-1]
        rowTitle = XbmcHelpers.parseDOM(durationRow, "div", attrs={"class": "field-label"})
        rowText = XbmcHelpers.parseDOM(durationRow, "div", attrs={"class": "field-text"})
        if rowTitle[0] == u"Длительность:":
            serial.duration = int(XbmcHelpers.stripTags(rowText[0]).replace(u' мин.', u'')) * 60


        # DATE CREATED
        dateCreatedNode = XbmcHelpers.parseDOM(infoContainer, "meta", attrs={"itemprop": "dateCreated"}, ret="content")
        serial.dateCreated = dateCreatedNode[0]

        # GENRES
        genreNode = XbmcHelpers.parseDOM(infoContainer, "div", attrs={"itemprop": "genre"})
        serial.genre = XbmcHelpers.stripTags(genreNode[0])

        # ORIGINAL TITLE
        originNode = XbmcHelpers.parseDOM(infoContainer, "div", attrs={"itemprop": "alternativeHeadline"})
        serial.originalTitle = XbmcHelpers.stripTags(originNode[0])

        # SEASONS
        seasonsNav = XbmcHelpers.parseDOM(pageContent, "div", attrs={"class": "serial-page-nav"})
        if len(seasonsNav) > 0:
            links = numbers = XbmcHelpers.parseDOM(seasonsNav[0], "li")
            for link in links:
                href = XbmcHelpers.parseDOM(link, "a", ret="href")
                title = XbmcHelpers.stripTags(link)
                serial.seasons[int(title)] = href[0]
        else:
            serial.seasons[1] = serialUrl

        # LINK
        serial.link = serialUrl

        return serial
    
    def parseEpisodes(self, pageContent, seasonNumber, seasonUrl):
        season = Season()
        season.number = seasonNumber

        # SERIAL TITLE
        titleNode = XbmcHelpers.parseDOM(pageContent, "h1", attrs={"class": "page-title"})
        season.serialTitle = XbmcHelpers.stripTags(titleNode[0])

        infoContainer = XbmcHelpers.parseDOM(pageContent, "div", attrs={"id": "o-seriale"})

        # DESCRIPTION
        descriptionNode = XbmcHelpers.parseDOM(infoContainer, "div", attrs={"itemprop": "description"})
        if len(descriptionNode) > 0:
            season.description = XbmcHelpers.stripTags(descriptionNode[0])

        # DURATON
        infoList = XbmcHelpers.parseDOM(infoContainer, "ul", attrs={"class": "info-list"})
        listItems = XbmcHelpers.parseDOM(infoList, "li")
        durationRow = listItems[len(listItems) - 1]
        rowTitle = XbmcHelpers.parseDOM(durationRow, "div", attrs={"class": "field-label"})
        rowText = XbmcHelpers.parseDOM(durationRow, "div", attrs={"class": "field-text"})
        if rowTitle[0] == u"Длительность:":
            season.episodeDuration = int(XbmcHelpers.stripTags(rowText[0]).replace(u' мин.', u'')) * 60
        
        season.link = seasonUrl

        itemsList = XbmcHelpers.parseDOM(pageContent, "div", attrs={"class": "item-serial"})

        for item in itemsList:
            episode = Episode()

            # POSTER
            imgNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-img"}, ret="style")
            episode.poster = imgNode[0].replace("');", "").replace("background-image: url('", "")

            # EPISODE TITLE
            titleNode = XbmcHelpers.parseDOM(item, "div", attrs={"class": "field-description"})
            episode.title = XbmcHelpers.stripTags(titleNode[0])

            # EPISODE LINK
            linkNode = XbmcHelpers.parseDOM(titleNode, "a", ret="href")
            episode.link = linkNode[0]

            season.episodes.append(episode)

        season.episodes = reversed(season.episodes)

        return season

    def parseTranslates(self, pageContent, episodeUrl, episodePoster):
        episode = Episode()

        body = XbmcHelpers.parseDOM(pageContent, "body")

        episode.link = episodeUrl
        episode.poster = episodePoster

        # EPISODE TITLE
        titleNode = XbmcHelpers.parseDOM(body, "h1", attrs={"class": "page-title"})
        episode.title = XbmcHelpers.stripTags(titleNode[0])

        # EPISODE DESCRIPTION
        descriptionNode = XbmcHelpers.parseDOM(body, "div", attrs={"itemprop": "description"})
        if len(descriptionNode) > 0:
            episode.description = XbmcHelpers.stripTags(descriptionNode[0])
        
        script = XbmcHelpers.parseDOM(body[0], "script", attrs={"data-cfasync": "false"})
        script = XbmcHelpers.stripTags(script[1])
        json_data = script.replace(u'window.playerData = \'', u'').replace(u'\';', u'').replace(u'\/', u'/').strip()

        episode.translates = json.loads(json_data)
        xbmc.log("TRANS: {0}".format(json_data.encode('utf-8')), xbmc.LOGNOTICE)

        return episode

    def parseHLSPlaylist(self, pageContent, pid):
        result = {}

        player = XbmcHelpers.parseDOM(pageContent, "div", attrs={"data-id": pid}, ret="data-config")
        player = json.loads(player[0])

        # READ PLAYLIST WITH QUALITIES
        plContent = self.getPageContent(player.get("hls"))
        plContent = plContent.split("\n")
        isData = False
        dataName = u''
        dataLink = u''
        for row in plContent:
            if isData:
                result[dataName] = player.get("hls").replace('index.m3u8', '') + row.replace('./', '')
                isData = False
            else:
                m = re.search('#EXT-X-STREAM-INF:RESOLUTION=([0-9]{3,4}x[0-9]{3,4})', row)
                if m:
                    dataName = m.group(1)
                    isData = True
                else:
                    dataName = u''

        if len(result) == 0:
            result["Native"] = player.get("hls")
            
        return result

    def parseSubtitles(self, pageContent, pid):
        result = {}

        player = XbmcHelpers.parseDOM(pageContent, "div", attrs={"data-id": pid}, ret="data-original_subtitle")
        if (len(player) > 0 and player[0] != u''):
            vttFile = self.getPageContent(player[0])
            srtFile = self.vtt2srt(vttFile)
            fName = 'special://home/temp/{0}.Original.srt'.format(pid)
            self.fwrite(fName, srtFile)

            result[u"original"] = fName

        player = XbmcHelpers.parseDOM(pageContent, "div", attrs={"data-id": pid}, ret="data-ru_subtitle")
        if (len(player) > 0 and player[0] != u''):
            vttFile = self.getPageContent(player[0])
            srtFile = self.vtt2srt(vttFile)
            fName = 'special://home/temp/{0}.Russian.srt'.format(pid)
            self.fwrite(fName, srtFile)

            result[u"ru"] = fName

        player = XbmcHelpers.parseDOM(pageContent, "div", attrs={"data-id": pid}, ret="data-en_subtitle")
        if (len(player) > 0 and player[0] != u''):
            vttFile = self.getPageContent(player[0])
            srtFile = self.vtt2srt(vttFile)
            fName = 'special://home/temp/{0}.English.srt'.format(pid)
            self.fwrite(fName, srtFile)

            result[u"en"] = fName

        return result

    def vtt2srt(self, data):
        result = u''

        stepper = 1
        for string in data.split("\n"):
            if string == 'WEBVTT':
                continue
            elif string == '':
                result = (u"{0}{1}\n" if stepper == 1 else u"{0}\n{1}\n").format(result, stepper)
                stepper += 1
            else:
                if '-->' in string:
                    string = string.replace(".", ",")
                    
                    sString = string.split(' --> ')
                    cor = False
                    if len(sString[0]) == 9:
                        sString[0] = "00:{0}".format(sString[0])
                        cor = True
                    if len(sString[1]) == 9:
                        sString[1] = "00:{0}".format(sString[1])
                        cor = True
                    if cor:
                        string = "{0} --> {1}".format(sString[0], sString[1])
                result = u"{0}{1}\n".format(result, string.decode('utf-8'))
        
        return result.encode('utf-8')

    def fwrite(self, path, data):
        f = open(xbmc.translatePath(path), 'w')
        f.write(data)
        f.close()