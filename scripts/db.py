import mysql.connector as connector


class DB():
    """
    implements a Context Manager for a MySQL database connection.
    """

    def __init__(self, db, username, password, host):
        self.db = db
        self.username = username
        self.password = password
        self.host = host
        self.conn = None
        self.cur = None

    def check_credentials(self):
        connection = connector.connect(user=self.username, password=self.password, host=self.host, database=self.db, use_unicode=True)
        status = connection.is_connected()
        if status:
            connection.close()
        return status

    def __enter__(self):
        # open connection, get cursor
        self.conn = connector.connect(user=self.username, password=self.password, host=self.host, database=self.db)
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, *args):
        # print errors if any arise while context is active
        if any(args):
            print(args)
        # close cursor, close connection (connection will be released to pool)
        self.cur.close()
        self.conn.close()
        self.cur = None
        self.conn = None

    def __repr__(self):
        return 'DB(database=' + self.db + ', username=' + self.username + ', host=' + self.host + ')'
