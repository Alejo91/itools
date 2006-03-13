# -*- coding: ISO-8859-1 -*-
# Copyright (C) 2003-2004 Juan David Ib��ez Palomar <jdavid@itaapy.com>
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
import unittest
from unittest import TestCase

# Import from itools
from itools.resources import memory
import itools.xml import XML



class XMLTestCase(TestCase):

    def test_identity(self):
        """
        Tests wether the input and the output match.
        """
        data = '<html>\n' \
               '<head></head>\n' \
               '<body>\n' \
               ' this is a <span style="color: red">test</span>\n' \
               '</body>\n' \
               '</html>'
        resource = memory.File(data)
        h1 = XML.Document(resource)
        h2 = XML.Document(resource)

        self.assertEqual(h1, h2)



if __name__ == '__main__':
    unittest.main()
