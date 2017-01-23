#!/usr/bin/env python

import bottle
import cgi
import hashlib
import logging
import os

from . import backend
from . import worldmodel

def get_visit_css():
    return '''
<style>
input:invalid { border: 1px solid red; }
</style>
'''

def get_visit_javascript():
    return '''
<script>
(function(){
    var form = document.getElementById("form");
    var how = document.getElementById("how");
    var longdesc = document.getElementById("longdesc");
    var longdesc_div = document.getElementById("longdesc_div");
    how.addEventListener('keyup', function (e) {
        if (how.value !== '') {
            how.setAttribute('pattern', '...*');
            longdesc_div.removeAttribute('hidden');
            return false;
        }
    });
})();
</script>
'''

def get_how_input_element(placeholder_text):
    return '<input type="text" name="how" id="how" pattern=".*" placeholder="%s" autocomplete="off" required></input>' % cgi.escape(placeholder_text)

def get_longdesc_input_element(placeholder_text):
    return '<textarea name="longdesc" id="longdesc" cols="75" rows="20" pattern="...*" placeholder="%s" autocomplete="off" required></textarea>' % cgi.escape(placeholder_text)

@bottle.error(404)
def error404(error):
    return 'Nothing here, sorry'

@bottle.get('/robots.txt')
def robots_txt():
    bottle.response.content_type = 'text/plain'
    return 'User-agent: *\nDisallow: /\n'

@bottle.get('/')
@bottle.get('/visit/<num>')
def visit(num=None):
    place = worldmodel.get_place(num)
    if place is None:
        bottle.redirect('/visit/%s' % worldmodel.get_default_place().num, 302)
    result = '<html>'
    result += '<head>'
    result += '<title>The Neverending Story</title>'
    result += get_visit_css()
    result += '</head>'
    result += '<body>'
    result += '<h2>The Neverending Story</h2>'
    result += cgi.escape(place.longdesc)
    result += '<hr>'
    result += '<form id="form" action="/create/%s" method="post">' % num
    connections = place.get_connections()
    if connections:
        result += '<ul>'
        for connection in connections:
            result += '<li><a href="/visit/%s">%s</a></li>' % (connection.successor_num, cgi.escape(connection.how))
        if len(connections) < 7:
            result += '<li>%s</li>' % get_how_input_element('Take a different action to continue the story')
        result += '</ul>'
    else:
        result += '<p> The story ends here, unless you choose to continue it yourself.</p>'
        result += get_how_input_element('Take an action to continue the story')
    result += '<div id="longdesc_div" hidden>'
    result += get_longdesc_input_element('What happens next?')
    result += '<br><input type="submit" value="Create!"></input>'
    result += '</div>'
    result += '</form>'
    result += get_visit_javascript()
    result += '</body></html>'
    return result

@bottle.get('/create/<predecessor_num>')
@bottle.post('/create/<predecessor_num>')
def create(predecessor_num):
    predecessor = worldmodel.get_place(predecessor_num)
    if predecessor is None:
        bottle.redirect('/', 302)
    try:
        how = bottle.request.forms['how'][:100]
        longdesc = bottle.request.forms['longdesc'][:10000]
    except KeyError:
        logging.warning('Missing some form input', exc_info=True)
        bottle.redirect('/visit/%s' % predecessor_num, 302)
    successor_num = worldmodel.create_place(predecessor_num, how, longdesc)
    bottle.redirect('/visit/%s' % successor_num, 302)

@bottle.get('/admin/dump')
def get_dump():
    bottle.response.content_type = 'text/plain'
    return worldmodel.dumps()

@bottle.get('/admin/load')
def get_load():
    result = '<html>'
    result += '<head><title>The Neverending Story (admin)</title></head>'
    result += '<body>'
    result += '<form id="form" action="/admin/load" method="post">'
    result += '<textarea name="data" cols="75" rows="20" autocomplete="off" required></textarea>'
    result += '<br><textarea name="password" cols="75" rows="1" autocomplete="off" required></textarea>'
    result += '<br><input type="submit" value="Load the database!"></input>'
    result += '</form>'
    result += '</body></html>'
    return result

@bottle.post('/admin/load')
def post_load():
    try:
        data = bottle.request.forms['data']
        password = bottle.request.forms['password']
    except KeyError:
        bottle.redirect('/', 302)
    if hashlib.sha256(password.strip()).hexdigest() != '0ab76faa9835d7770467904cd14796c59f579eb1015f34aee505dddad8aa3b32':
        return bottle.HTTPError(403, 'Forbidden')
    bottle.response.content_type = 'text/plain'
    if data.strip() == 'RESET':
        worldmodel.reset()
        return 'Successfully reset!'
    else:
        worldmodel.loads(data)
        return 'Successfully loaded!'

if __name__ == '__main__':
    backend.init()
    bottle.run(host='0.0.0.0', port=os.environ.get('PORT', 8080))
