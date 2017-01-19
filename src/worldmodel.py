import os
import pickle
import time
import uuid

_places = {}
_connections = {}
_default_place_num = None
_last_load_time = 0  # far in the past

def get_random_num():
    return uuid.uuid4().hex[:16]

def get_root_num():
    return 'home'

class Place:
    def __init__(self, longdesc):
        self.num = get_random_num()
        self.longdesc = longdesc
    def __str__(self):
        raise ValueError()
    def get_connections(self):
        global _connections
        return [c for c in _connections.values() if c.predecessor_num == self.num]

class Connection:
    def __init__(self, predecessor_num, how, successor_num):
        self.num = get_random_num()
        self.predecessor_num = predecessor_num
        self.how = how
        self.successor_num = successor_num
    def __str__(self):
        raise ValueError()

def load_data():
    global _last_load_time
    global _default_place_num, _places, _connections
    print 'thinking about loading data...'
    if time.time() > _last_load_time + 5:
        print 'loading data...'
        try:
            this_dir = os.path.abspath(os.path.dirname(__file__))
            with open(os.path.join(this_dir, 'data.pickle'), 'r') as f:
                data = pickle.load(f)
        except Exception:
            data = (None, {}, {})
        (_default_place_num, _places, _connections) = data
        _last_load_time = time.time()

def store_data():
    global _last_load_time
    global _default_place_num, _places, _connections
    this_dir = os.path.abspath(os.path.dirname(__file__))
    data = (_default_place_num, _places, _connections)
    with open(os.path.join(this_dir, 'data.pickle'), 'w') as f:
        pickle.dump(data, f)
    _last_load_time = time.time()

def get_default_place():
    global _default_place_num, _places, _connections
    load_data()
    if _default_place_num is None:
        _default_place_num = create_place(None, 'Start playing', 'You are standing at the end of a road before a small brick building.')
    return _places.get(_default_place_num)

def get_place(num):
    global _default_place_num, _places, _connections
    load_data()
    return _places.get(num)

def create_place(predecessor_num, how, longdesc):
    global _default_place_num, _places, _connections
    place = Place(longdesc)
    if predecessor_num is None:
        place.num = get_root_num()
    _places[place.num] = place
    if predecessor_num is not None:
        connection = Connection(predecessor_num, how, place.num)
        _connections[connection.num] = connection
    store_data()
    return place.num
