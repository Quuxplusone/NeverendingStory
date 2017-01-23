import logging
import uuid

from . import backend

_places = {}
_connections = {}

def get_random_num():
    return uuid.uuid4().hex[:16]

def get_root_num():
    return 'home'

class Place:
    def __init__(self, num, longdesc):
        if num is None:
            num = get_random_num()
        self.num = num
        self.longdesc = longdesc
    def __str__(self):
        raise ValueError()
    def get_connections(self):
        global _connections
        return [c for c in _connections.values() if c.predecessor_num == self.num]

class Connection:
    def __init__(self, num, predecessor_num, how, successor_num):
        if num is None:
            num = get_random_num()
        self.num = num
        self.predecessor_num = predecessor_num
        self.how = how
        self.successor_num = successor_num
    def __str__(self):
        raise ValueError()

def init_data():
    with backend.cursor() as c:
        c.execute('CREATE TABLE places (num TEXT PRIMARY KEY, longdesc TEXT)')
        c.execute('CREATE TABLE connections (num TEXT PRIMARY KEY, how TEXT, predecessor_num TEXT, successor_num TEXT)')

def load_data():
    global _places, _connections
    print 'thinking about loading data...'
    if not _places:
        print 'loading data...'
        try:
            with backend.cursor() as c:
                for row in c.execute('SELECT * FROM places'):
                    _places[row[0]] = Place(row[0], row[1])
                for row in c.execute('SELECT * FROM connections'):
                    _connections[row[0]] = Connection(row[0], row[1], row[2], row[3])
        except Exception:
            logging.exception('proceeding to init_data...')
            init_data()

def store_data():
    global _places, _connections
    with backend.cursor() as c:
        for p in _places.values():
            c.execute('INSERT INTO places VALUES (?,?)', (p.num, p.longdesc))
        for p in _connections.values():
            c.execute('INSERT INTO connections VALUES (?,?,?,?)', (p.num, p.predecessor_num, p.how, p.successor_num))

def get_default_place():
    global _places
    load_data()
    if get_root_num() not in _places:
        create_place(None, 'Start playing', 'You are standing at the end of a road before a small brick building.')
    return _places[get_root_num()]

def get_place(num):
    global _places
    load_data()
    return _places.get(num)

def create_place(predecessor_num, how, longdesc):
    global _places, _connections
    place = Place(None, longdesc)
    if predecessor_num is None:
        place.num = get_root_num()
    _places[place.num] = place
    if predecessor_num is not None:
        connection = Connection(None, predecessor_num, how, place.num)
        _connections[connection.num] = connection
    store_data()
    return place.num
