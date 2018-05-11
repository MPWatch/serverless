class MP():
    def __init__(self, twitter_handle, name, party, constituency):
        self.name = name
        self.party = party
        self.twitter_handle = twitter_handle
        self.constituency = constituency

    def __repr__(self):
        return "MP({0}, {1}, {2}, {3})".format(self.name, self.twitter_handle, self.party, self.constituency)

    def to_json(self):
        return self.__dict__

