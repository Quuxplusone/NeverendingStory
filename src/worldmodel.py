
import hashlib

class Place:
    _current_num = 1
    def __init__(self, longdesc):
        self.num = hashlib.sha256(str(Place._current_num)).hexdigest()
        Place._current_num += 1
        self.longdesc = longdesc
        self.connections = []
    def __str__(self):
        raise ValueError()

class Connection:
    _current_num = 1
    def __init__(self, predecessor, how, successor):
        self.num = hashlib.sha256(str(Connection._current_num)).hexdigest()
        Connection._current_num += 1
        self.predecessor = predecessor
        self.how = how
        self.successor = successor
    def __str__(self):
        raise ValueError()

_places = {}
_connections = {}
_default_place = None

def get_place(num):
    return _places.get(num, _places[_default_place])

def create_place(predecessor, how, longdesc):
    place = Place(longdesc)
    _places[place.num] = place
    connection = Connection(predecessor, how, place)
    _connections[connection.num] = connection
    if predecessor is not None:
        predecessor.connections.append(connection)
    return place.num

_default_place = create_place(None, 'Start playing', 'You are standing at the end of a road before a small brick building.')
