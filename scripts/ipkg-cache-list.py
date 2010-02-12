#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@itaapy.com>
# Copyright (C) 2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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

"""Usage:
ipkg-cache-list.py [--cache-dir dir]

Lists packages in the cache.
"""

# Import from the Standard Library
from optparse import OptionParser
from os.path import join
from tempfile import gettempdir

# Import from itools
from itools import __version__
from itools.pkg import parse_package_name, Bundle
from itools.pkg import ArchiveNotSupported, EXTENSIONS
from itools.vfs import vfs


TMP_DIR = '%s/Packages' % gettempdir()

if __name__ == '__main__':
    # command line parsing
    usage = '%prog [--cache-dir dir]'
    version = 'itools %s' % __version__
    description = ("List packages from the cache dir")
    parser = OptionParser(usage, version=version, description=description)

    parser.add_option("-c", "--cache-dir", dest="cache_dir", default=TMP_DIR,
                      help="")

    options, args = parser.parse_args()

    CACHE_DIR = options.cache_dir
    if not vfs.exists(CACHE_DIR):
        vfs.make_folder(CACHE_DIR)

    cache_dir = vfs.open(CACHE_DIR)

    print "Packages in cache %s" % CACHE_DIR
    for filename in cache_dir.get_names('.'):
        dist = parse_package_name(filename)
        if dist['extension'] in EXTENSIONS:
            dist_loc = join(CACHE_DIR, dist['file'])

            try:
                dist = Bundle(dist_loc)
            except ArchiveNotSupported:
                continue

            name = dist.get_metadata('Name')
            version = dist.get_metadata('Version')
            if name and version:
                print "* %-20.20s Version: %-25.25s" % (name, version)
