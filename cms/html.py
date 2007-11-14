# -*- coding: UTF-8 -*-
# Copyright (C) 2006-2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2006-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2007 Nicolas Deram <nicolas@itaapy.com>
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
from datetime import datetime
from HTMLParser import HTMLParseError

# Import from itools
from itools.uri import Path
from itools.datatypes import DateTime
from itools.xml import TEXT, START_ELEMENT
from itools.xhtml import Document as XHTMLDocument
from itools.stl import stl
from itools.xhtml import sanitize_stream
from itools.html import Parser as HTMLParser

# Import from ikaaro
from messages import *
from text import Text
from registry import register_object_class


class XMLFile(Text):

    class_id = 'text/xml'



class EpozEditable(object):
    """A mixin class for handlers implementing HTML editing.
    """
    #######################################################################
    # Edit / Inline / source
    def get_epoz_document(self):
        # Implement it in your editable handler
        raise NotImplementedError


    def get_epoz_data(self):
        document = self.get_epoz_document()
        body = document.get_body()
        if body is None:
            return None
        return body.get_content_elements()


    #######################################################################
    # Edit / Inline / edit form
    edit_form__access__ = 'is_allowed_to_edit'
    edit_form__label__ = u'Edit'
    edit_form__sublabel__ = u'Inline'
    def edit_form(self, context):
        """WYSIWYG editor for HTML documents."""
        data = self.get_epoz_data()
        # If the document has not a body (e.g. a frameset), edit as plain text
        if data is None:
            return Text.edit_form(self, context)

        # Edit with a rich text editor
        namespace = {}
        namespace['timestamp'] = DateTime.encode(datetime.now())
        namespace['rte'] = self.get_rte(context, 'data', data)

        handler = self.get_object('/ui/html/edit.xml')
        return stl(handler, namespace)


    #######################################################################
    # Edit / Inline / edit
    edit__access__ = 'is_allowed_to_edit'
    def edit(self, context, sanitize=False):
        timestamp = context.get_form_value('timestamp', type=DateTime)
        if timestamp is None:
            return context.come_back(MSG_EDIT_CONFLICT)
        document = self.get_epoz_document()
        if document.timestamp is not None and timestamp < document.timestamp:
            return context.come_back(MSG_EDIT_CONFLICT)

        # Sanitize
        new_body = context.get_form_value('data')
        try:
            new_body = HTMLParser(new_body)
        except HTMLParseError:
            return context.come_back(u'Invalid HTML code.')
        if sanitize:
            new_body = sanitize_stream(new_body)
        # "get_epoz_document" is to set in your editable handler
        old_body = document.get_body()
        events = (document.events[:old_body.start+1] + new_body
                  + document.events[old_body.end:])
        # Save the changes
        document.set_changed()
        document.events = events

        return context.come_back(MSG_CHANGES_SAVED)



class XHTMLFile(EpozEditable, Text):

    class_id = 'application/xhtml+xml'
    class_title = u'Web Page'
    class_description = u'Create and publish a Web Page.'
    class_icon16 = 'images/HTML16.png'
    class_icon48 = 'images/HTML48.png'
    class_views = [['view'],
                   ['edit_form', 'externaledit', 'upload_form'],
                   ['edit_metadata_form'],
                   ['state_form'],
                   ['history_form']]
    class_handler = XHTMLDocument


    GET__mtime__ = None
    def GET(self, context):
        method = self.get_firstview()
        # Check access
        if method is None:
            raise Forbidden
        # Redirect
        return context.uri.resolve2(';%s' % method)


    #######################################################################
    # API
    #######################################################################
    def is_empty(self):
        """Test if XML doc is empty"""
        body = self.get_body()
        if body is None:
            return True
        for type, value, line in body.events:
            if type == TEXT:
                if value.replace('&nbsp;', '').strip():
                    return False
            elif type == START_ELEMENT:
                tag_uri, tag_name, attributes = value
                if tag_name == 'img':
                    return False
        return True


    #######################################################################
    # User interface
    #######################################################################

    #######################################################################
    # View
    view__access__ = 'is_allowed_to_view'
    view__label__ = u'View'
    view__title__ = u'View'
    def view(self, context):
        namespace = {}
        body = self.handler.get_body()
        if body is None:
            namespace['text'] = None
        else:
            namespace['text'] = body.get_content_elements()

        handler = self.get_object('/ui/html/view.xml')
        return stl(handler, namespace)


    #######################################################################
    # Edit / Inline
    def get_epoz_document(self):
        return self.handler



class HTMLFile(XHTMLFile):

    class_id = 'text/html'



###########################################################################
# Register
###########################################################################
register_object_class(XMLFile)
register_object_class(XMLFile, format='application/xml')
register_object_class(XHTMLFile)
register_object_class(HTMLFile)
