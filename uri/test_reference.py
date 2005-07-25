# -*- coding: ISO-8859-1 -*-
# Copyright (C) 2004-2005 Juan David Ib��ez Palomar <jdavid@itaapy.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA


# Import from the Standard Library
import unittest

# Import from itools
from __init__ import get_reference
from generic import Reference
from mailto import Mailto


class ReferenceTestCase(unittest.TestCase):

    def test_mailto(self):
        """Test if mailto references are detected."""
        ref = get_reference('mailto:jdavid@itaapy.com')
        self.assert_(isinstance(ref, Mailto))


    def test_http(self):
        """http references are generic."""
        ref = get_reference('http://ikaaro.org')
        self.assert_(isinstance(ref, Reference))


    def test_ftp(self):
        """references with unknow scheme are generic."""
        ref = get_reference('http://ikaaro.org')
        self.assert_(isinstance(ref, Reference))

    
    def test_no_scheme(self):
        """references with no scheme are generic."""
        ref = get_reference('logo.png')
        self.assert_(isinstance(ref, Reference))



if __name__ == '__main__':
    unittest.main()
