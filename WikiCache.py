class WikiCache(object):
    def __init__(self):
        self.cache = {}
    def __contains__(self, key):
        return key in self.cache
    def __getitem__(self, key):
        return self.cache[key]

