# -*- coding: UTF-8 -*-
# Copyright (C) 2006-2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2006-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
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
import cgi

# Import from itools
from itools.stl import stl
from itools import rest

# Import from itools.cms
from base import DBObject
from utils import get_parameters
from file import File
from messages import *
from registry import register_object_class


class Text(File):

    class_id = 'text'
    class_title = u'Plain Text'
    class_description = u'Keep your notes with plain text files.'
    class_icon16 = 'images/Text16.png'
    class_icon48 = 'images/Text48.png'
    class_views = [['view', 'view_rest'],
                   ['edit_form', 'externaledit', 'upload_form'],
                   ['edit_metadata_form'],
                   ['state_form'],
                   ['history_form']]


    # Download
    def get_content_type(self):
        return '%s; charset=UTF-8' % File.get_content_type(self)


    #######################################################################
    # User interface
    #######################################################################

    @classmethod
    def new_instance_form(cls, context):
        return DBObject.new_instance_form.im_func(cls, context)


    @classmethod
    def new_instance(cls, container, context):
        return DBObject.new_instance.im_func(cls, container, context)


    #######################################################################
    # View
    view__access__ = 'is_allowed_to_view'
    view__label__ = u'View'
    view__sublabel__ = u'Plain Text'
    def view(self, context):
        namespace = {}
        namespace['text'] = self.handler.to_str()

        handler = self.get_object('/ui/text/view.xml')
        return stl(handler, namespace)


    view_rest__access__ = 'is_allowed_to_view'
    view_rest__sublabel__ = u"As reStructuredText"
    def view_rest(self, context):
        data = self.data.encode('utf-8')
        return rest.to_html_events(data)


    view_xml__access__ = 'is_allowed_to_view'
    view_xml__sublabel__ = u"As reStructuredText"
    def view_xml(self, context):
        namespace = {}
        data = self.data.encode('utf-8')
        namespace['text'] = rest.to_str(data, format='xml')

        handler = self.get_object('/ui/text/view.xml')
        return stl(handler, namespace)


    #######################################################################
    # Edit / Inline
    edit_form__access__ = 'is_allowed_to_edit'
    edit_form__label__ = u'Edit'
    edit_form__sublabel__ = u'Inline'
    def edit_form(self, context):
        namespace = {}
        namespace['data'] = self.handler.to_str()

        handler = self.get_object('/ui/text/edit.xml')
        return stl(handler, namespace)


    edit__access__ = 'is_allowed_to_edit'
    def edit(self, context):
        data = context.get_form_value('data')
        self.handler.load_state_from_string(data)

        return context.come_back(MSG_CHANGES_SAVED)


    #######################################################################
    # Edit / External
    def externaledit(self, context):
        namespace = {}
        # XXX This list should be built from a txt file with all the encodings,
        # or better, from a Python module that tells us which encodings Python
        # supports.
        namespace['encodings'] = [{'value': 'utf-8', 'title': 'UTF-8',
                                   'is_selected': True},
                                  {'value': 'iso-8859-1',
                                   'title': 'ISO-8859-1',
                                   'is_selected': False}]

        handler = self.get_object('/ui/text/externaledit.xml')
        return stl(handler, namespace)


register_object_class(Text)



class PO(Text):

    class_id = 'text/x-po'
    class_title = u'Message Catalog'


    #######################################################################
    # User interface
    #######################################################################


    #######################################################################
    # Edit
    edit_form__access__ = 'is_allowed_to_edit'
    edit_form__label__ = u'Edit'
    edit_form__sublabel__ = u'Inline'
    def edit_form(self, context):
        namespace = {}

        # Get the messages, all but the header
        msgids = [ x for x in self.get_msgids() if x.strip() ]

        # Set total
        total = len(msgids)
        namespace['messages_total'] = str(total)

        # Set the index
        parameters = get_parameters('messages', index='1')
        index = parameters['index']
        namespace['messages_index'] = index
        index = int(index)

        # Set first, last, previous and next
        uri = context.uri
        namespace['messages_first'] = uri.replace(messages_index=1)
        namespace['messages_last'] = uri.replace(messages_index=total)
        previous = max(index - 1, 1)
        namespace['messages_previous'] = uri.replace(messages_index=previous)
        next = min(index + 1, total)
        namespace['messages_next'] = uri.replace(messages_index=next)

        # Set msgid and msgstr
        if msgids:
            msgids.sort()
            msgid = msgids[index-1]
            namespace['msgid'] = cgi.escape(msgid)
            msgstr = self.get_msgstr(msgid)
            msgstr = cgi.escape(msgstr)
            namespace['msgstr'] = msgstr
        else:
            namespace['msgid'] = None

        handler = self.get_object('/ui/PO_edit.xml')
        return stl(handler, namespace)


    edit__access__ = 'is_allowed_to_edit'
    def edit(self, context):
        msgid = context.get_form_value('msgid')
        msgstr = context.get_form_value('msgstr')
        messages_index = context.get_form_value('messages_index')

        self.set_changed()
        msgid = msgid.replace('\r', '')
        msgstr = msgstr.replace('\r', '')
##        self.set_message(msgid, msgstr)
        self._messages[msgid].msgstr = msgstr

        return context.come_back(MSG_CHANGES_SAVED)


register_object_class(PO)



class CSS(Text):

    class_mimetypes = ['text/css']
    class_extension = 'css'
    class_id = 'text/css'
    class_title = 'CSS'
    class_icon48 = 'images/CSS48.png'


register_object_class(CSS)



class Python(Text):

    class_id = 'text/x-python'
    class_icon48 = 'images/Python48.png'


register_object_class(Python)
