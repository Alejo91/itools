# -*- coding: UTF-8 -*-
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
from datetime import datetime
import mimetypes
from random import random
from time import time

# Import from itools
from itools.datatypes import (DateTime, QName, String, Unicode,
                              XML as XMLDataType)
from itools.schemas import get_schema_by_uri, get_schema, get_datatype
from itools.handlers import File, Text, register_handler_class
from itools.xml import XMLNamespace, Parser, START_ELEMENT, END_ELEMENT, TEXT
from itools.web import get_context
from metadata import Record



class Lock(Text):

    class_mimetypes = ['text/x-lock']
    class_extension = 'lock'

    __slots__ = ['database', 'uri', 'timestamp', 'dirty',
                 'username', 'lock_timestamp', 'key']


    def new(self, username=None, **kw):
        self.username = username
        self.lock_timestamp = datetime.now()
        self.key = '%s-%s-00105A989226:%.03f' % (random(), random(), time())


    def _load_state_from_file(self, file):
        username, timestamp, key = file.read().strip().split('\n')
        self.username = username
        # XXX backwards compatibility: remove microseconds first
        timestamp = timestamp.split('.')[0]
        self.lock_timestamp = DateTime.decode(timestamp)
        self.key = key


    def to_str(self):
        timestamp = DateTime.encode(self.lock_timestamp)
        return '%s\n%s\n%s' % (self.username, timestamp, self.key)



class Metadata(File):

    class_mimetypes = ['text/x-metadata']
    class_extension = 'metadata'

    __slots__ = ['database', 'uri', 'timestamp', 'dirty', 'properties']


    def new(self, handler_class=None, format=None, **kw):
        # Add format and version
        kw['format'] = format or handler_class.class_id
        kw['version'] = handler_class.class_version

        # Initialize
        properties = {}
        # Load
        for name, value in kw.items():
            if value is None:
                continue
            # The property
            key = QName.decode(name)
            properties[key] = value

        # Set state
        self.properties = properties


    def _load_state_from_file(self, file):
        p_key = None
        datatype = None
        p_language = None
        p_value = ''
        stack = []
        for event, value, line_number in Parser(file.read()):
            if event == START_ELEMENT:
                namespace_uri, local_name, attributes = value
                if local_name == 'metadata':
                    stack.append({})
                else:
                    # Get the property type
                    schema = get_schema_by_uri(namespace_uri)
                    datatype = schema.get_datatype(local_name)
                    # Build the property key
                    p_key = (schema.class_prefix, local_name)

                    if datatype is Record:
                        stack.append({})
                    else:
                        p_value = ''

                    # xml:lang
                    attr_key = (XMLNamespace.class_uri, 'lang')
                    p_language = attributes.get(attr_key)
            elif event == END_ELEMENT:
                namespace_uri, local_name = value
                # Get the property type
                schema = get_schema_by_uri(namespace_uri)
                datatype = schema.get_datatype(local_name)
                p_default = datatype.default
                # Build the property key
                p_key = (schema.class_prefix, local_name)

                if local_name == 'metadata':
                    self.properties = stack.pop()
                else:
                    # Decode value
                    if datatype is Record:
                        p_value = stack.pop()
                    elif datatype is Unicode:
                        p_value = datatype.decode(p_value, 'UTF-8')
                    else:
                        p_value = datatype.decode(p_value)
                    # Set property
                    if isinstance(p_default, list):
                        stack[-1].setdefault(p_key, []).append(p_value)
                    elif p_language is None:
                        stack[-1][p_key] = p_value
                    else:
                        stack[-1].setdefault(p_key, {})
                        stack[-1][p_key][p_language] = p_value
                    # Reset variables
                    datatype = None
                    p_language = None
                    p_value = ''
            elif event == TEXT:
                if p_key is not None:
                    p_value += value


    def to_str(self):
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']

        # Insert open root element with the required namespace declarations
        prefixes = set()
        for key, value in self.properties.items():
            prefix, local_name = key
            if prefix is not None:
                prefixes.add(prefix)

            # Get the type
            datatype = get_datatype(key)
            # Get the qualified name
            if prefix is None:
                qname = local_name
            else:
                qname = '%s:%s' % key

            if isinstance(value, dict):
                for language, value in value.items():
                    value = datatype.encode(value)
                    value = XMLDataType.encode(value)
                    lines.append('  <%s xml:lang="%s">%s</%s>'
                                 % (qname, language, value, qname))
            elif isinstance(value, list):
                if datatype is Record:
                    # Record
                    for value in value:
                        lines.append('  <%s>' % qname)
                        for key, value in value.items():
                            prefix, local_name = key
                            if prefix is not None:
                                prefixes.add(prefix)
                            datatype = get_datatype(key)
                            value = datatype.encode(value)
                            value = XMLDataType.encode(value)
                            qname2 = QName.encode(key)
                            lines.append('    <%s>%s</%s>' % (qname2, value,
                                qname2))
                        lines.append('  </%s>' % qname)
                else:
                    # Regular field
                    for value in value:
                        value = datatype.encode(value)
                        value = XMLDataType.encode(value)
                        lines.append('  <%s>%s</%s>' % (qname, value, qname))
            else:
                value = datatype.encode(value)
                value = XMLDataType.encode(value)
                lines.append('  <%s>%s</%s>' % (qname, value, qname))

        if prefixes:
            aux = [ (x, get_schema(x).class_uri) for x in prefixes ]
            aux = '\n          '.join([ 'xmlns:%s="%s"' % x for x in aux ])
            lines.insert(1, '<metadata %s>' % aux)
        else:
            lines.insert(1, '<metadata>')

        lines.append('</metadata>')
        return '\n'.join(lines)


    ########################################################################
    # API
    ########################################################################
    def get_property_and_language(self, name, language=None):
        """Return the value for the given property and the language of that
        value.

        For monolingual properties, the language always will be None.
        """
        key = QName.decode(name)
        # Check the property exists
        datatype = get_datatype(key)
        if key not in self.properties:
            return datatype.default, None
        # Get the value
        value = self.properties[key]

        # Monolingual property
        if not isinstance(value, dict):
            return value, None

        # Language negotiation
        if language is None:
            context = get_context()
            if context is None:
                language = None
            else:
                languages = [ k for k, v in value.items() if v.strip() ]
                accept = context.get_accept_language()
                language = accept.select_language(languages)
            # Default (FIXME pick one at random)
            if language is None:
                language = value.keys()[0]
            return value[language], language

        if language in value:
            return value[language], language
        return datatype.default, None


    def get_property(self, name, language=None):
        return self.get_property_and_language(name, language=language)[0]


    def has_property(self, name, language=None):
        key = QName.decode(name)

        if key not in self.properties:
            return False

        if language is not None:
            return language in self.properties[key]

        return True


    def set_property(self, name, value, language=None):
        self.set_changed()

        key = QName.decode(name)

        # Set the value
        if language is None:
            datatype = get_datatype(key)

            default = datatype.default
            if isinstance(default, list):
                if isinstance(value, list):
                    self.properties[key] = value
                else:
                    values = self.properties.setdefault(key, [])
                    values.append(value)
            else:
                self.properties[key] = value
        else:
            values = self.properties.setdefault(key, {})
            values[language] = value


    def del_property(self, name, language=None):
        key = QName.decode(name)

        if key in self.properties:
            if language is None:
                self.set_changed()
                del self.properties[key]
            else:
                values = self.properties[key]
                if language in values:
                    self.set_changed()
                    del values[language]



# Register handler classes, and mimetypes
for handler_class in [Lock, Metadata]:
    register_handler_class(handler_class)
    for mimetype in handler_class.class_mimetypes:
        mimetypes.add_type(mimetype, '.%s' % handler_class.class_extension)

