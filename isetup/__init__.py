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

# Import from the Standard Library
from mimetypes import add_type

# Import from isetup
from commands import DEFAULT_REPOSITORY, iregister, iupload
from distribution import Dist, ArchiveNotSupported
from handlers import SetupConf
from metadata import PKGINFOFile
from packages import get_installed_info, packages_infos
from repository import parse_package_name, download, EXTENSIONS


__all__ = [
    'ArchiveNotSupported',
    'DEFAULT_REPOSITORY',
    'Dist',
    'download',
    'EXTENSIONS',
    'get_installed_info',
    'iregister',
    'iupload',
    'packages_infos',
    'parse_package_name',
    'PKGINFOFile',
    'SetupConf',
    ]

add_type('text/x-egg-info', '.egg-info')
