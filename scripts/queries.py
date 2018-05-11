from mysql.connector.errors import Error


from scripts.db import DB
from scripts.mp import MP


class Query():

    def __init__(self, db):
        if not isinstance(db, DB):
            raise AttributeError('db attribute must be a DB object. ' + str(type(db)) + ' given instead.')
        self.db = db

    def create_tables(self):
        with self.db as db:
            try:
                # MPS contains a list of all MPs on Twitter
                db.cur.execute("CREATE TABLE mps(twitter_handle varchar(255) NOT NULL, name varchar(255) NOT NULL, party varchar(255), constituency varchar(255), PRIMARY KEY(twitter_handle))")
                db.conn.commit()
            except Error as e:
                # handles 'Table already exists' error
                print(str(e))
                if not e.errno == 1050:
                    raise e

            try:
                # Tweets contains a list of all Tweets, by topic and date
                db.cur.execute("CREATE TABLE tweets(tweet_id varchar(255) NOT NULL, added DATE NOT NULL, twitter_handle varchar(255) NOT NULL, content varchar(600) NOT NULL, url varchar(255), followers_count INT, retweet_count INT, profile_pic_link varchar(255), profile_url varchar(255), created varchar(255) NOT NULL, PRIMARY KEY (tweet_id), FOREIGN KEY (twitter_handle) REFERENCES mps(twitter_handle))")
                db.conn.commit()
            except Error as e:
                # handles 'Table already exists' error
                print(str(e))
                if not e.errno == 1050:
                    raise e

            try:
                # Topics contains of all tweets with their associated topic(s)
                table = "CREATE TABLE topics"
                fields = "tweet_id varchar(255) NOT NULL, entity varchar(255) NOT NULL, original_topic varchar(255) NOT NULL, twitter_handle varchar(255) NOT NULL, added DATE NOT NULL"
                constraints = "PRIMARY KEY (tweet_id, entity), FOREIGN KEY (twitter_handle) REFERENCES mps(twitter_handle), FOREIGN KEY (tweet_id) REFERENCES tweets(tweet_id)"
                db.cur.execute(table + "(" + fields + ", " + constraints + ")")
                db.conn.commit()
            except Error as e:
                # handles 'Table already exists' error
                print(str(e))
                if not e.errno == 1050:
                    raise e


    def insert_tweets_for_entity(self, serialized_tweets):
        with self.db as db:
            for t in serialized_tweets:
                try:
                    db.cur.execute(("INSERT INTO tweets VALUES (\"{tweet_id}\", \"{date}\", \"{entity}\", \"{twitter_handle}\", \"{content}\", \"{url}\", \"{followers_count}\", \"{retweet_count}\", \"{profile_pic_link}\", \"{profile_url}\", \"{created}\")").format(**t))
                except Error as e:
                    # TODO: fix bugs
                    print(str(e))
                    pass
                    # ignore duplicate entries, emojis, foreign key errors
                    if not e.errno == 1062 and not e.errno == 1366 and not e.errno == 1452:
                        print(t)
                        raise e
                db.conn.commit()

    def get_recent_tweets_for_entity(self, entity):
        with self.db as db:
            columns = "SELECT t.tweet_id, t.added, t.entity, t.content, t.url, t.followers_count, t.retweet_count, t.profile_pic_link, t.profile_url, t.created, m.name, m.twitter_handle"
            tweet_table = ("(SELECT * FROM tweets WHERE entity=\"{0}\" AND added=(SELECT MAX(added) FROM tweets)) t").format(entity)
            mp_table = "(SELECT name, twitter_handle from mps) m"
            join_on = "t.twitter_handle = m.twitter_handle"
            db.cur.execute(columns + " FROM " + tweet_table + " JOIN " + mp_table + " ON " + join_on)
            cols = [c[0] for c in db.cur.description]
            return list(dict(zip(cols, t)) for t in db.cur.fetchall())

    def get_recent_entities(self):
        with self.db as db:
            db.cur.execute("SELECT DISTINCT entity FROM tweets WHERE added=(SELECT MAX(added) FROM tweets)")
            return list(t[0] for t in db.cur.fetchall())

    def get_entity_size(self, entity):
        with self.db as db:
            db.cur.execute(("SELECT COUNT(*) FROM tweets WHERE entity=\"{0}\" AND added=(SELECT MAX(added) FROM tweets)").format(entity))
            return int(db.cur.fetchone()[0])

    def insert_mps(self, mps):
        with self.db as db:
            for mp in mps:
                db.cur.execute(("INSERT INTO mps VALUES (\"{0}\", \"{1}\", \"{2}\", \"{3}\")").format(mp.twitter_handle, mp.name, mp.party, mp.constituency))
                db.conn.commit()

    def get_mps(self):
        with self.db as db:
            db.cur.execute("SELECT * FROM mps")
            return [MP(*mp) for mp in db.cur.fetchall()]

    def get_mp_for_twitter_handle(self, twitter_handle):
        with self.db as db:
            db.cur.execute(("SELECT * FROM mps WHERE twitter_handle=\"{0}\"").format(twitter_handle))
            return MP(*db.cur.fetchone())
