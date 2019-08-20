from collections import namedtuple

import requests
from bs4 import BeautifulSoup

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

    def isLive(self):
        ''' based on code returns dictionary with statuses and link,
        if the page is not live try Webarchiv.
        TODO distinguishing between a page that is not in the archive
             and not just available online
        '''
        status_code = self.statusCode()

        # failed to get status from page
        if status_code is False:
            return Result('E', 'Nepodařilo se připojit ke stránce',
                          self.link, self.colors[1])

        # page si live
        if status_code < self.live_wall:
            return Result('L', status_code, self.link, self.colors[0])

        # page is not available in the archive
        if self.Webarchiv(self.link).checkAvailability() is None:
            return Result('E', status_code, self.link, self.colors[1])
        else:
            return Result('W', status_code, self.link, self.colors[2])

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
