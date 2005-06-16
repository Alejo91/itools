# -*- coding: ISO-8859-1 -*-
# Copyright (C) 2005 Juan David Ib��ez Palomar <jdavid@itaapy.com>
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
import warnings

# Import from itools
from itools.xml.exceptions import XMLError
from itools import types



"""
This module keeps a registry for namespaces and namespace handlers.

Namespace handlers are used through the parsing process, they are
responsible to deal with the elements and attributes associated to
them.

This module provides an API to register namespace uris and handlers,
and to ask this registry.

It also provides a registry from namespace prefixes to namespace uris.
While namespace prefixes are local to an XML document, it is sometimes
useful to refer to a namespace through its prefix. This feature must
be used carefully, collisions 
"""


#############################################################################
# The registry
#############################################################################

namespaces = {}
prefixes = {}


def set_namespace(namespace):
    """
    Associates a namespace handler to a namespace uri. It a prefix is
    given it also associates that that prefix to the given namespace.
    """
    namespaces[namespace.class_uri] = namespace

    prefix = namespace.class_prefix
    if prefix is not None:
        if prefix in prefixes:
            warnings.warn('The prefix "%s" is already registered.' % prefix)
        prefixes[prefix] = namespace.class_uri


def get_namespace(namespace_uri):
    """
    Returns the namespace handler associated to the given uri. If there
    is none the default namespace handler will be returned, and a warning
    message will be issued.
    """
    if namespace_uri in namespaces:
        return namespaces[namespace_uri]

    # Use default
    warnings.warn('Unknown namespace "%s" (using default)' % namespace_uri)
    return namespaces[None]


def has_namespace(namespace_uri):
    """
    Returns true if there is namespace handler associated to the given uri.
    """
    return namespace_uri in namespaces


def get_namespace_by_prefix(prefix):
    """
    Returns the namespace handler associated to the given prefix. If there
    is none the default namespace handler is returned, and a warning message
    is issued.
    """
    if prefix in prefixes:
        namespace_uri = prefixes[prefix]
        return get_namespace(namespace_uri)

    # Use default
    warnings.warn('Unknown namespace prefix "%s" (using default)' % prefix)
    return namespaces[None]


#############################################################################
# Namespaces
#############################################################################

class AbstractNamespace(object):
    """
    This class defines the default behaviour for namespaces, which is to
    raise an error.

    Subclasses should define:

    class_uri
    - The uri that uniquely identifies the namespace.

    class_prefix
    - The recommended prefix.

    get_element_schema(name)
    - Returns a dictionary that defines the schema for the given element.

    get_attribute_schema(name)
    - Returns a dictionary that defines the schema for the given attribute.
    """

    class_uri = None
    class_prefix = None


    def get_element_schema(name):
        raise XMLError, 'undefined element "%s"' % name

    get_element_schema = staticmethod(get_element_schema)


    def get_attribute_schema(name):
        raise XMLError, 'undefined attribute "%s"' % name

    get_attribute_schema = staticmethod(get_attribute_schema)



class DefaultNamespace(AbstractNamespace):
    """
    Default namespace handler for elements and attributes that are not bound
    to a particular namespace.
    """

    class_uri = None
    class_prefix = None


    def get_element_schema(name):
        from XML import Element
        return {'type': Element,
                'is_empty': False}

    get_element_schema = staticmethod(get_element_schema)


    def get_attribute_schema(name):
        return {'type': types.String}

    get_attribute_schema = staticmethod(get_attribute_schema)



class XMLNamespace(AbstractNamespace):

    class_uri = 'http://www.w3.org/XML/1998/namespace'
    class_prefix = 'xml'


    def get_attribute_schema(name):
        if name == 'lang':
            return {'type': types.String}
        return {'type': types.Unicode}

    get_attribute_schema = staticmethod(get_attribute_schema)



class XMLNSNamespace(AbstractNamespace):

    class_uri = 'http://www.w3.org/2000/xmlns/'
    class_prefix = 'xmlns'


    def get_attribute_schema(name):
        return {'type': types.String}

    get_attribute_schema = staticmethod(get_attribute_schema)



# Register the namespaces
set_namespace(DefaultNamespace)
set_namespace(XMLNamespace)
set_namespace(XMLNSNamespace)
