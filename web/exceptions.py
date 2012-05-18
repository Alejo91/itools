# -*- coding: UTF-8 -*-
# Copyright (C) 2009-2010 J. David Ibáñez <jdavid.ibp@gmail.com>
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

# Import from itools
from itools.core import is_thingy
from itools.gettext import MSG
from messages import ERROR



class FormError(StandardError):
    """Raised when a form is invalid (missing or invalid fields).
    """

    def __init__(self, message=None, missing=False, invalid=False):
        self.msg = message
        self.missing = missing
        self.invalid = invalid


    def get_message(self):
        # Custom message
        value = self.msg
        if value is not None:
            if is_thingy(value, MSG):
                return value
            return ERROR(value)
        # Default message
        msg = u'There are errors... XXX'
        return ERROR(msg)


    def __str__(self):
        return self.get_message().gettext()



