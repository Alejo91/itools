# -*- coding: UTF-8 -*-
# Copyright (C) 2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2008 Gautier Hayoun <gautier.hayoun@itaapy.com>
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

# Import from isetup
from repository import parse_package_name, is_distable, download, Repository,\
        RepositoryNotSupported, EXTENSIONS
from distribution import Dist, ArchiveNotSupported

from metadata import list_eggs_info, egg_info

__all__ = [
    # Metadata functions
    'list_eggs_info',
    'egg_info',
    # Repositories functions and classses
    'parse_package_name',
    'is_distable',
    'download',
    'Repository',
    # Distribution class
    'Dist',
    # Exceptions
    'RepositoryNotSupported',
    'ArchiveNotSupported'
    # List of supported extensions
    'EXTENSIONS',
    ]

