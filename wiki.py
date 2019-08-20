from collections import namedtuple

import wikipedia

Description = namedtuple('Description', ['title', 'url', 'summary'])


class Wiki():
    def __init__(self, name, lang='cs'):
        # set lang of wikipedia
        self.lang = lang
        wikipedia.set_lang(lang)

        # if the user enters the entire link, separate the name
        if 'wikipedia.org/' in name:
            name = name.split('/')[-1]

        try:
            self.wikipage = wikipedia.WikipediaPage(name)
        except wikipedia.exceptions.PageError:
            self.wikipage = None
        except wikipedia.exceptions.DisambiguationError as e:
            self.wikipage = wikipedia.WikipediaPage(e.options[0])

    def getDescription(self):
        ''' return namedtuple with title, url and summary '''
        return Description(self.wikipage.title, self.wikipage.url,
                           self.wikipage.summary)

    def linksGenerator(self):
        ''' creates generator for list of URLs of external links on a page
            returns None if page has none
        '''
        try:
            for link in self.wikipage.references:
                yield link
        except KeyError:
            return None
