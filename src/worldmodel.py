import uuid

def get_random_num():
    return uuid.uuid4().hex[:16]

class Place:
    def __init__(self, longdesc):
        self.num = get_random_num()
        self.longdesc = longdesc
        self.connections = []
    def __str__(self):
        raise ValueError()

class Connection:
    def __init__(self, predecessor, how, successor):
        self.num = get_random_num()
        self.predecessor = predecessor
        self.how = how
        self.successor = successor
    def __str__(self):
        raise ValueError()

_places = {}
_connections = {}
_default_place = None

def get_default_place():
    return _places.get(_default_place)

def get_place(num):
    return _places.get(num)

def create_place(predecessor, how, longdesc):
    place = Place(longdesc)
    _places[place.num] = place
    connection = Connection(predecessor, how, place)
    _connections[connection.num] = connection
    if predecessor is not None:
        predecessor.connections.append(connection)
    return place.num

_default_place = create_place(None, 'Start playing', 'You are standing at the end of a road before a small brick building.')
