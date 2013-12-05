#!/usr/bin/env python
# youtube-dl-user
#
# Utility to download Youtube user's uploaded videos as MP3s.
#
# @author imclab <info at theimclab dot com>
# @license LGPL version 2 or greater <http://www.gnu.org/licenses/lgpl.html>

import sys
import urllib
import httplib
import json
import os
import shutil
import tempfile
import glob


class PlaylistDownloader:
    targetDir = ''
    totalVideos = 0
    downloaded = 0

    def setTarget(self, target):
        self.targetDir = os.path.realpath(target) + '/';
        return self.targetDir;

    def download(self, playlistId):
        print 'Getting playlist information ... '
        data = self.fetchInfo(playlistId)
        self.totalVideos = int(data['feed']['openSearch$totalResults']['$t'])
        print 'Total videos to download: ' + str(self.totalVideos)

        playlistDir = self.createPath(self.targetDir, data['feed']['title']['$t']);
        os.chdir(self.setTarget(playlistDir))

        self.downloaded = 1;
        while(self.downloaded <= self.totalVideos):
            data = self.fetchInfo(playlistId, self.downloaded, 50)
            self.downloadEntires(data['feed']['entry'])

    def downloadEntires(self, entries):
        for entry in entries:
            group = entry['media$group'];
            if self.downloadEntry(group['yt$videoid']['$t'], group['media$title']['$t']):
                self.downloaded = self.downloaded + 1
            print

    def downloadEntry(self, ytId, ytTitle):
        print ytId + '(' + str(self.downloaded).zfill(3) + '):', ytTitle, '...'

        existing = glob.glob('*' + ytId + '.*');
        filtered = [x for x in existing if not x.endswith('part')]
        if filtered.__len__() > 0:
            print 'alreary exists, skipping...'
            return True

        try:
            #os.system('youtube-dl -t --audio-format=best http://www.youtube.com/watch?v=' + ytId)
            os.system('youtube-dl -t --audio-format=mp3 http://www.youtube.com/watch?v=' + ytId)
            return True

        except KeyboardInterrupt:
            sys.exit(1)

        except Exception as e:
            print 'failed: ', e.strerror
            return False

    def fetchInfo(self, playlistId, start = 1, limit = 0):
        connection = httplib.HTTPConnection('gdata.youtube.com')
        connection.request('GET', '/feeds/api/users/' + str(playlistId)+'/uploads/' + '/?' + urllib.urlencode({
                'alt' : 'json',
                'max-results' : limit,
                'start-index' : start,
                'v' : 2
            }))

        response = connection.getresponse()
        if response.status != 200:
            print 'Error: Not a valid/public user.'
            sys.exit(1)

        data = response.read()
        data = json.loads(data)
        return data

    def createPath(self, path, title):
        title = title.replace('/', '')
        number = ''

        if os.path.exists(path + title) == True and os.path.isdir(path + title) == False:
            while(os.path.exists(path + title + str(number)) == True and os.path.isdir(path + title + str(number)) == False):
                if number == '':
                    number = 0

                number = number + 1

        if os.path.exists(path + title + str(number)) == False:
            os.mkdir(path + title + str(number))

        return path + title + str(number)



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: youtube-dl-playlist PLAYLIST_ID [DESTINATION_PATH]'
        sys.exit(1)
    else:
        if sys.argv[1][0] == 'P' and sys.argv[1][1] == 'L':
            PLAYLIST_ID = sys.argv[1][2:]
        else:
            PLAYLIST_ID = sys.argv[1]
    downloader = PlaylistDownloader()
    if len(sys.argv) == 3:
        downloader.setTarget(sys.argv[2] + '/')
    else:
        downloader.setTarget('./')
    downloader.download(PLAYLIST_ID);
