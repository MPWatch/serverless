from json import dumps, JSONEncoder


class Tweet:
    def __init__(self, status, hashtags, entities):
        self.status = status
        self.hashtags = hashtags
        self.entities = entities

    def __repr__(self):
        return "Tweet(" + repr(self.status) + ", " + str(self.hashtags) + ", " + str(self.entities) + ")"

    def normalize_hashtags(self):
        return [(w, _remove_special_chars(w)) for w in self.hashtags]

    def normalize_entities(self):
        return [(w, _remove_special_chars(w)) for w in self.entities]

    def serialize_json(self):
        return dumps(self, cls=TweetEncoder)

    def serialize_mysql(self, entity, date):
        status_id = str(self.status.id)
        handle = str(self.status.user.screen_name)
        text = str(self.status.text).replace('"', '')
        url = str(self.status.urls[0].url) if len(self.status.urls) else None
        followers_count = int(self.status.user.followers_count)
        retweet_count = int(self.status.retweet_count) if self.status.retweet_count else 0
        image_url = str(self.status.user.profile_image_url_https) if self.status.user.profile_image_url_https else None
        profile_url = str(self.status.user.url) if self.status.user.url else None
        created = str(self.status.created_at)
        return {
            'tweet_id': status_id,
            'date': date,
            'entity': entity,
            'twitter_handle': '@' + handle,
            'content': text,
            'url': url,
            'followers_count': followers_count,
            'retweet_count': retweet_count,
            'profile_pic_link': image_url,
            'profile_url': profile_url,
            'created': created,
        }

    def serialize_dict(self):
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
