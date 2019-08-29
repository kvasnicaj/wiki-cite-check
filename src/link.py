from collections import namedtuple

import requests
from bs4 import BeautifulSoup

from src.models import LinksLog, db

Result = namedtuple('Result',
                    ['sign', 'status_code', 'link', 'color'])


class Link():
    # setting the boundary when the link is considered dead
    live_wall = 400
    colors = ('btn-success', 'btn-danger', 'btn-primary')

    def __init__(self, link):
        self.link = link

    def statusCode(self):
        '''
        First try is just a get head,
        if get error status code than try double checked with full page.
        Returns acquired status code or false.'''
        try:
            r = requests.head(self.link, allow_redirects=True)
            return r.status_code
        except Exception:
            return False

    def log(self, result):
        ''' save result to database '''
        try:
            status = int(result.status_code)
        except ValueError:
            status = 0

        db.session.add(LinksLog(url=result.link,
                                status=status,
                                wal=result.sign))
        db.session.commit()

    def isLive(self):
        ''' based on code returns dictionary with statuses and link,
        if the page is not live try Webarchiv.
        TODO distinguishing between a page that is not in the archive
             and page in the archive but not available online
        '''
        status_code = self.statusCode()

        # failed to get status from page
        if status_code is False:
            result = Result('E', 0, self.link, self.colors[1])
        # failed to get status from page
        elif status_code < self.live_wall:
            result = Result('L', status_code, self.link, self.colors[0])
        # page is not available in the archive
        elif self.Webarchiv(self.link).checkAvailability() is None:
            result = Result('E', status_code, self.link, self.colors[1])
        # page is available in the archive
        else:
            result = Result('W', status_code, self.link, self.colors[2])

        self.log(result)
        return result

    class Webarchiv():
        ''' inner class for accessing web archive'''

        def __init__(self, url):
            self.walink = f'https://wayback.webarchiv.cz/wayback/*/{url}'

        def checkAvailability(self):
            ''' if is archived version of page available returns link
            else return None'''
            try:
                r = requests.get(self.walink)
                soup = BeautifulSoup(r.content, 'html.parser')
                wbmeta = soup.find(id='wbMeta')
            except Exception:
                return None

            if wbmeta is None:
                return None
            else:
                return self.walink
