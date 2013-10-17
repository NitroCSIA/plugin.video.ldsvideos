import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
#import StorageServer
import sys
import xbmc
try:
        import json
except:
        import simplejson as json
from addon import *

class MormonChannel(Plugin):
    def __init__(self,plugin):
        self.languageID = '1'
        self.api = 'http://tech.lds.org/mc/api/'
        self.icon = plugin.mcicon 
        self.fanart = plugin.mcfanart

    def broker(self,params):
        try: submode = int(params['submode'])
        except: submode = None
        if not submode:
            self.get_main_menu()
        elif submode == 1:
            self.get_channels_list()
        elif submode == 2:
            self.get_featured_list()
        elif submode == 3:
            self.get_stations_list()
        elif submode == 4:
            self.get_series_list()
        elif submode == 5:
            customID = params['customID']
            self.get_topics_list(customID)
        elif submode == 6:
            seriesID = params['seriesID']
            self.get_episodes_list(seriesID)
        elif submode == 7:
            topicID = params['topicID']
            self.get_items_list(topicID)
        elif submode == 8:
            self.get_stations_list()
        elif submode == 9:
            self.get_conferences_list()
        elif submode == 10:
            conferenceID = params['conferenceID']
            self.get_sessions_list(conferenceID)
        elif submode == 11:
            sessionID = params['sessionID']
            self.get_talks_list(sessionID)
        elif submode == 12:
            self.get_magazines_list()
        elif submode == 13:
            magazineID = params['magazineID']
            self.get_issues_list(magazineID)
        elif submode == 14:
            issueID = params['issueID']
            self.get_articles_list(issueID)
        elif submode == 15:
            self.get_scriptures_list()
        elif submode == 16:
            scriptureID = params['scriptureID']
            self.get_books_list(scriptureID)
        elif submode == 17:
            bookID = params['bookID']
            self.get_chapters_list(bookID)

    def get_main_menu(self):
        self.add_dir(self.icon,{'Title':'Featured','Plot':'Watch the featured videos from the Mormon Channel'},{'name':'Featured',
            'mode':14,'submode':2},self.fanart)
        self.add_dir(self.icon,{'Title':'Series','Plot':'List available series from the Mormon Channel'},{'name':'Series',
            'mode':14,'submode':4},self.fanart)
        self.get_channels_list()
        self.add_dir(self.icon,{'Title':'Radio','Plot':'Listen to live radio channels provided by the Mormon Channel'},
            {'name':'Radio','mode':14,'submode':8},self.fanart)
        self.add_dir(self.icon,{'Title':'General Conference','Plot':'Watch LDS General Conferences'},{'name':'General Conference','mode':14,'submode':9},self.fanart)
        self.add_dir(self.icon,{'Title':'Magazines','Plot':'Listen to LDS magazine articles'},{'name':'Magazine','mode':14,'submode':12},self.fanart)
        self.add_dir(self.icon,{'Title':'Scriptures','Plot':'Listen to LDS Standard Works'},{'name':'Scriptures','mode':14,'submode':15},self.fanart)
        

    def create_media_links(self,itemsList):
        for i in itemsList:
            id = i['ID']
            name = i['Title'].encode('utf8')
            desc = i['Summary'].encode('utf8')
            title = name
            thumb = self.icon
            for image in i['Images']:
                thumb = image['URL']
            medias = {}
            for media in i['Media']:
                medias[media['MediaContainer']] = media['URL']
            if medias == {}:
                return
            try:
                self.add_link(thumb,{'Title':title,'Plot':desc},{'name':name,'mode':5,'url':medias['MP4']},thumb)
            except:
                try:
                    self.add_link(thumb,{'Title':title,'Plot':desc},{'name':name,'mode':5,'url':self.get_youtube_link(medias['YouTube'])},thumb) # open youtube
                except:
                    self.add_link(thumb,{'Title':title,'Plot':desc},{'name':name,'mode':5,'url':medias.values()[0]},thumb)

    def create_folder_links(self,itemsList,submode,idparam):
        for i in itemsList:
            id = i['ID']
            name = i['Title'].encode('utf8')
            desc = i['Summary'].encode('utf8') if 'Summary' in i.keys() else ''
            thumb = self.icon
            if 'Images' in i.keys():
                for image in i['Images']:
                    thumb = image['URL']
            self.add_dir(thumb,{'Title':name,'Plot':desc},{'name':name,'mode':14,'submode':submode,idparam:id},thumb)

    def get_language_list(self):
        url = self.api + 'language/list'

    def get_channels_list(self):
        data = json.loads(make_request(self.api + 'channel/list?LanguageID=' + self.languageID))
        if not data['api_success']:return
        for channel in data['Channels']:
            id = channel['ID']
            name = channel['Title'].encode('utf8')
            summary = channel['Summary'].encode('utf8')
            contentType = channel['ContentType']
            customID = channel['CustomID']
            if customID:
                self.add_dir(self.icon,{'Title':name,'Plot':summary},{'name':name,'mode':14,'submode':5,'customID':customID},self.fanart)

    def get_featured_list(self):
        data = json.loads(make_request(self.api + 'feature/list?LanguageID=' + self.languageID))
        if not data['api_success']: return
        self.create_media_links(data['Features'])

    def get_stations_list(self):
        data = json.loads(make_request(self.api + 'station/list?LanguageID=' + self.languageID))
        if not data['api_success']: return
        #self.create_media_links(data['Stations'])
        for i in data['Stations']:
            data = make_request(i['CurrentlyPlayingURL'])
            soup = BeautifulSoup(data)
            name = i['Title'].encode('utf8')
            try:
                title = soup.audio.title.getText().encode('utf8')
                name = "%s - %s" % (i['Title'].encode('utf8'),title)
            except:
                title = name
            try:
                desc = soup.audio.comment1.getText().encode('utf8')
            except:
                desc = "Radio station"
            try:
                thumb = soup.audio.metadata_id.getText()
            except:
                thumb = None
            if not thumb or thumb[-4:] != '.jpg':
                try:
                    thumb = i['Images'][0]['URL']
                except:
                    thumb = self.icon
            self.add_link(thumb,{'Title':title,'Plot':desc},{'name':name,'mode':5,'url':i['Media'][0]['URL']},thumb)

    def get_series_list(self):
        data = json.loads(make_request(self.api + 'series/list?LanguageID=' + self.languageID))
        if not data['api_success']: return
        self.create_folder_links(data['Series'],6,'seriesID')

    def get_topics_list(self,customID):
        data = json.loads(make_request(self.api + 'channel/topiclist?CustomID=' + customID))
        if not data['api_success']: return
        self.create_folder_links(data['Topics'],7,'topicID')

    def get_episodes_list(self,seriesID):
        data = json.loads(make_request(self.api + 'series/episodelist?SeriesID=' + seriesID))
        if not data['api_success']: return
        show = data['Series']['Title'].encode('utf8')
        self.create_media_links(data['Episodes'])

    def get_items_list(self,topicID):
        data = json.loads(make_request(self.api + 'channel/topicitemslist?TopicID=' + topicID))
        if not data['api_success']: return
        self.create_media_links(data['Items'])

    def get_conferences_list(self):
        data = json.loads(make_request(self.api + 'conference/list?LanguageID=' + self.languageID))
        if not data['api_success']: return
        for i in data['Conferences']:
            id = i['ID']
            name = i['ShortTitle']
            title = i['Title']
            year = i['Year']
            thumb = self.icon
            for image in i['Images']:
                thumb = image['URL']
            self.add_dir(thumb,{'Title':title,'Year':year},{'name':name,'mode':14,'submode':10,'conferenceID':id},thumb)

    def get_sessions_list(self,conferenceID):
        data = json.loads(make_request(self.api + 'conference/sessionlist?ConferenceID=' + conferenceID))
        if not data['api_success']: return
        self.create_folder_links(data['Sessions'],11,'sessionID')

    def get_talks_list(self,sessionID):
        data = json.loads(make_request(self.api + 'conference/talklist?SessionID=' + sessionID))
        if not data['api_success']: return
        for i in data['Talks']:
            id = i['ID']
            title = i['Title'].encode('utf8')
            desc = i['Summary'].encode('utf8')
            thumb = self.icon
            for image in i['Images']:
                thumb = image['URL']
            try:
                name = "%s - %s" % (i['Persons'][0]['Name'].encode('utf8'),title) if i['Persons'][0]['Name'].encode('utf8') != title else title
            except:
                name = title
            medias = {}
            for media in i['Media']:
                medias[media['MediaContainer']] = media['URL']
            if medias == {}:
                return
            try:
                self.add_link(thumb,{'Title':title,'Plot':desc},{'name':name,'mode':5,'url':medias['MP4']},thumb)
            except:
                try:
                    self.add_link(thumb,{'Title':title,'Plot':desc},{'name':name,'mode':5,'url':self.get_youtube_link(medias['YouTube'])},thumb) # open youtube
                except:
                    self.add_link(thumb,{'Title':title,'Plot':desc},{'name':name,'mode':5,'url':medias.values()[0]},thumb)

    def get_magazines_list(self):
        data = json.loads(make_request(self.api + 'magazine/list?LanguageID=' + self.languageID))
        if not data['api_success']: return
        self.create_folder_links(data['Magazines'],13,'magazineID')

    def get_issues_list(self,magazineID):
        data = json.loads(make_request(self.api + 'magazine/issuelist?MagazineID=' + magazineID))
        if not data['api_success']: return
        self.create_folder_links(data['Issues'],14,'issueID')

    def get_articles_list(self,issueID):
        data = json.loads(make_request(self.api + 'magazine/articlelist?IssueID=' + issueID))
        if not data['api_success']: return
        self.create_media_links(data['Articles'])

    def get_scriptures_list(self):
        data = json.loads(make_request(self.api + 'scripture/list?LanguageID=' + self.languageID))
        if not data['api_success']: return
        self.create_folder_links(data['Scriptures'],16,'scriptureID')

    def get_books_list(self,scriptureID):
        data = json.loads(make_request(self.api + 'scripture/booklist?ScriptureID=' + scriptureID))
        if not data['api_success']: return
        self.create_folder_links(data['Books'],17,'bookID')

    def get_chapters_list(self,bookID):
        data = json.loads(make_request(self.api + 'scripture/chapterlist?BookID=' + bookID))
        if not data['api_success']: return
        self.create_media_links(data['Chapters'])
