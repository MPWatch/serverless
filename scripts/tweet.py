from json import dumps, JSONEncoder


class Tweet:
    """
    Tweet is a mediating class between the database and scripts.
    All attributes are primitives or collections of primitives.
    """

    def __init__(self, status, entities):
        self.status_id = str(status.id)
        self.handle = str(status.user.screen_name)
        self.hashtags = [h.text for h in status.hashtags if status.hashtags]
        self.text = str(status.text).replace('"', '')
        self.url = str(status.urls[0].url) if len(status.urls) else None
        self.followers_count = int(status.user.followers_count)
        self.retweet_count = int(status.retweet_count) if status.retweet_count else 0
        self.image_url = str(status.user.profile_image_url_https) if status.user.profile_image_url_https else None
        self.profile_url = str(status.user.url) if status.user.url else None
        # TODO: convert to date
        self.created = str(status.created_at)
        self.entities = entities

    def __repr__(self):
        return "Tweet(" + repr(self.status_id) + ")"

    def normalize_hashtags(self):
        return [(w, _remove_special_chars(w)) for w in self.hashtags]

    def normalize_entities(self):
        return [(w, _remove_special_chars(w)) for w in self.entities]

    def serialize_json(self):
        return dumps(self, cls=TweetEncoder)

    def serialize_mysql(self, date):
        """
        date: must be datetime object
        """
        return {
            'tweet_id': self.status_id,
            'date': date,
            'twitter_handle': '@' + self.handle,
            'content': self.text,
            'url': self.url,
            'followers_count': self.followers_count,
            'retweet_count': self.retweet_count,
            'profile_pic_link': self.image_url,
            'profile_url': self.profile_url,
            'created': self.created,
        }

    def serialize_dict(self):
        # TODO: not in use. fix.
        """
        Serializes dictionary for AWS DynamoDB specs.
        Keys with empty values are not included in the serialization.
        """
        def serialize_user(u):
            user_dict = dict()
            user_dict['created_at'] = u.created_at
            user_dict['description'] = u.description
            user_dict['followers_count'] = u.followers_count
            user_dict['friends_count'] = u.friends_count
            user_dict['id'] = u.id
            user_dict['language'] = u.lang
            user_dict['location'] = u.location
            user_dict['name'] = u.name
            user_dict['profile_background_color'] = u.profile_background_color
            user_dict['image_url'] = u.profile_image_url_https
            user_dict['handle'] = u.screen_name
            user_dict['statuses_count'] = u.statuses_count
            user_dict['url'] = u.url
            user_dict['verified'] = u.verified
            return {k: v for k, v in user_dict.items() if v}

        d = dict()
        s = self.status

        if s:
            d['created_at'] = s.created_at
            d['favorite_count'] = s.favorite_count
            d['id'] = s.id
            d['language'] = s.lang
            d['retweet_count'] = s.retweet_count
            d['source'] = s.source
            d['text'] = s.text
            d['truncated'] = s.truncated
            d['urls'] = [u.url for u in s.urls]
            d['mentions'] = [serialize_user(u) for u in s.user_mentions]

            u = self.status.user
            d['user'] = serialize_user(u)

        d['hashtags'] = self.hashtags
        d['entities'] = self.entities

        return {k: v for k, v in d.items() if v}


class TweetEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Tweet):
            return obj.serialize_dict()

def _remove_special_chars(word):
    return (''.join(e for e in word if e.isalnum())).lower()
