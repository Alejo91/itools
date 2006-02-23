# -*- coding: ISO-8859-1 -*-
# Copyright (C) 2003-2005 Juan David Ib��ez Palomar <jdavid@itaapy.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Import from the Standard Library
from datetime import datetime
from urllib import urlopen
import time

# Import from itools
import base
from itools import uri



class Resource(base.Resource):
    pass



class File(Resource, base.File):

    _file = None

    def open(self):
        self._file = urlopen(str(self.uri))


    def close(self):
        self._file.close()
        self._file = None


    def is_open(self):
        return self._file is not None


    def read(self, size=None):
        return self._file.read(size)


    def get_mimetype(self):
        return urlopen(str(self.uri)).info().gettype()


    def get_mtime(self):
        mtime = urlopen(str(self.uri)).info().getdate('Last-Modified')
        mtime = datetime.fromtimestamp(time.mktime(mtime))
        return mtime



def get_resource(netpath):
    return File(netpath)
