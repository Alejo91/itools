# -*- coding: ISO-8859-1 -*-
# Copyright (C) 2005 Juan David Ib��ez Palomar <jdavid@itaapy.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# Import from itools
from itools.handlers.File import File
from itools.web import headers


class Message(File):
    """
    Base class, for HTTP request and responses.
    """

    #########################################################################
    # API
    #########################################################################
    def set_header(self, name, value):
        name = name.lower()
        if isinstance(value, str):
            type = headers.get_type(name)
            value = type.decode(value)
        self.state.headers[name] = value


    def has_header(self, name):
        name = name.lower()
        return name in self.state.headers


    def get_header(self, name):
        name = name.lower()
        return self.state.headers[name]
