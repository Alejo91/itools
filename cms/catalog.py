# -*- coding: UTF-8 -*-
# Copyright (C) 2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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

# FIXME No thread-safe
to_unindex = set()
to_index = set()


def get_to_unindex():
    return to_unindex


def get_to_index():
    return to_index


def schedule_to_index(handler):
    to_index.add(handler)


def schedule_to_unindex(handler):
    to_unindex.add(handler.abspath)


def schedule_to_reindex(handler):
    to_unindex.add(handler.abspath)
    to_index.add(handler)
