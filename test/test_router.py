# -*- coding: UTF-8 -*-
# Copyright (C) 2017 Alexandre Bonny <alexandre.bonny@protonmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from unittest import TestCase, main

# Import from itools
from itools.core import get_abspath
from itools.web import BaseView, WebServer, DispatchRouter, Context
from itools.web import StaticRouter


class View(BaseView):

    def GET(self, kw):
        return 'Welcome ' + kw.get('name')



class Root(object):

    context_cls = Context

    def before_traverse(self, context):
        pass

SERVER = None

class RouterTestCase(TestCase):

    def setUp(self):
        global SERVER
        # Init context
        self.context = Context(root=Root())
        if SERVER is None:
            SERVER = WebServer(root=Root())
            SERVER.listen('127.0.0.1', 8080)


    def test_dispatch_router(self):
        global SERVER
        self.rest_router = DispatchRouter()
        self.rest_router.add_route('/rest/welcome/{name}', View)
        SERVER.set_router('/rest', self.rest_router)
        response = SERVER.do_request(method='GET',
                                     path='/rest/welcome/test',
                                     context=self.context(router=self.rest_router))
        assert response.get('status') == 200
        assert response.get('entity') == 'Welcome test'


    def test_static_router(self):
        global SERVER
        self.static_router = StaticRouter(local_path=get_abspath('tests/'))
        SERVER.set_router('/static', self.static_router)
        # Launch server
        response = SERVER.do_request(method='GET',
                                     path='/static/hello.txt',
                                     context=self.context(router=self.static_router, mount_path='/static'))
        assert response.get('status') == 200
        assert response.get('entity') == 'hello world'



if __name__ == '__main__':
    main()
