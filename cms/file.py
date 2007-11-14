# -*- coding: UTF-8 -*-
# Copyright (C) 2005-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2006-2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007 Henry Obein <henry@itaapy.com>
# Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
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
from datetime import datetime, timedelta
import mimetypes

# Import from itools
from itools.uri import get_reference
from itools.datatypes import FileName
from itools.handlers import File as FileHandler
from itools import vfs
from itools.rest import checkid
from itools.i18n import guess_language
from itools.handlers import Text
from itools.stl import stl

# Import from itools.cms
from base import DBObject
from messages import *
from registry import register_object_class, get_object_class
from versioning import VersioningAware
from workflow import WorkflowAware
from catalog import schedule_to_reindex



class File(WorkflowAware, VersioningAware, DBObject):

    class_id = 'file'
    class_version = '20040625'
    class_title = u'File'
    class_description = u'Upload office documents, images, media files, etc.'
    class_icon16 = 'images/File16.png'
    class_icon48 = 'images/File48.png'
    class_views = [['download_form', 'view'],
                   ['externaledit', 'upload_form'],
                   ['edit_metadata_form'],
                   ['state_form'],
                   ['history_form']]
    class_handler = FileHandler


    @classmethod
    def _make_object(cls, folder, name, body=None):
        DBObject._make_object.im_func(cls, folder, name)
        # Add the body
        if body is not None:
            handler = cls.class_handler(string=body)
            folder.set_handler(name, handler)


    @classmethod
    def new_instance_form(cls, context):
        namespace = {}
        namespace['class_id'] = cls.class_id
        handler = context.root.get_object('ui/file/new_instance.xml')
        return stl(handler, namespace)


    @classmethod
    def new_instance(cls, container, context):
        # Check input data
        file = context.get_form_value('file')
        if file is None:
            return context.come_back(MSG_EMPTY_FILENAME)

        # Interpret input data (the mimetype sent by the browser can be
        # minimalistic)
        name, mimetype, body = file
        guessed, encoding = mimetypes.guess_type(name)
        if encoding is not None:
            encoding_map = {'gzip': 'application/x-gzip',
                            'bzip2': 'application/x-bzip2'}
            if encoding_map.has_key(encoding):
                mimetype = encoding_map[encoding]
        elif guessed is not None:
            mimetype = guessed

        # Check the name
        name = checkid(name)
        if name is None:
            return context.come_back(MSG_BAD_NAME)

        # Add the language extension to the name
        if mimetype.startswith('text/'):
            short_name, type, language = FileName.decode(name)
            if language is None:
                encoding = Text.guess_encoding(body)
                data = unicode(body, encoding)
                language = guess_language(data)
                # Rebuild the name
                name = FileName.encode((short_name, type, language))

        # Check the name is free
        if container.has_object(name):
            return context.come_back(MSG_NAME_CLASH)

        # Build the object
        cls = get_object_class(mimetype)
        object = cls.make_object(container, name, body)

        goto = './%s/;%s' % (name, object.get_firstview())
        return context.come_back(MSG_NEW_RESOURCE, goto=goto)


    GET__mtime__ = DBObject.get_mtime
    def GET(self, context):
        return self.download(context)


    #######################################################################
    # Versioning & Indexing
    def to_text(self):
        return self.handler.to_text()


    def get_size(self):
        return len(self.handler.to_str())


    def before_commit(self):
        self.commit_revision()


#   def set_changed(self):
#       DBObject.set_changed(self)
#       if self.uri is not None:
#           schedule_to_reindex(self)


    #######################################################################
    # User Interface
    #######################################################################
    def get_human_size(self):
        file = self.handler
        bytes = len(file.to_str())
        size = bytes / 1024.0
        if size >= 1024:
            size = size / 1024.0
            str = u'%.01f MB'
        else:
            str = u'%.01f KB'

        return self.gettext(str) % size


    #######################################################################
    # Download
    download_form__access__ = 'is_allowed_to_view'
    download_form__label__ = u'View'
    download_form__sublabel__ = u'Download'
    def download_form(self, context):
        namespace = {}
        namespace['url'] = '../' + self.name
        namespace['title_or_name'] = self.get_title()
        handler = self.get_object('/ui/file/download_form.xml')
        return stl(handler, namespace)


    def get_content_type(self):
        # Content-Type
        return self.get_property('format')


    download__access__ = 'is_allowed_to_view'
    download__mtime__ = DBObject.get_mtime
    def download(self, context):
        response = context.response
        response.set_header('Content-Type', self.get_content_type())
        return self.handler.to_str()


    #######################################################################
    # Edit / External
    externaledit__access__ = 'is_allowed_to_edit'
    externaledit__label__ = u'Edit'
    externaledit__sublabel__ = u'External'
    def externaledit(self, context):
        handler = self.get_object('/ui/file/externaledit.xml')
        return stl(handler)


    external_edit__access__ = 'is_allowed_to_edit'
    def external_edit(self, context):
        # TODO check if zopeedit really needs the meta_type.
        encoding = context.get_form_value('encoding')

        # Get the context, request and response
        request, response = context.request, context.response

        uri = context.uri
        uri_string = '%s://%s/%s' % (uri.scheme, uri.authority, uri.path[:-1])
        uri = get_reference(uri_string)
        r = ['url:%s' % str(uri),
             'meta_type:toto', # XXX Maybe something more meaningful than toto?
             'content_type:%s' % self.get_mimetype(),
             'cookie:%s' % request.get_cookies_as_str()]

        title = self.get_property('dc:title')
        if title:
            title = title.encode(encoding or 'UTF-8')
        else:
            title = self.name
        r.append('title:%s' % title)

        if self.is_locked():
            lock = self.get_lock()
            # locks expire after 1 hour
            if lock.lock_timestamp + timedelta(hours=1) < datetime.now():
                self.unlock()
                context.commit = True
            else:
                # always borrow lock from same user
                if lock.username == context.user.name:
                    r.append('lock-token:%s' % lock.key)
                    r.append('borrow_lock:1')
                else:
                    goto = ';%s' % self.get_firstview()
                    msg = u'This page is lock by another user'
                    return context.come_back(message=msg, goto=goto)

        if request.has_header('Authorization'):
            r.append('auth:%s' % request.get_header('Authorization'))

        r.append('')

        # TODO known bug from ExternalEditor requires rfc1123_date()
        # Using RESPONSE.setHeader('Pragma', 'no-cache') would be better, but
        # this chokes crappy most MSIE versions when downloads happen on SSL.
        # cf. http://support.microsoft.com/support/kb/articles/q316/4/31.asp
        #response.set_header('Last-Modified', rfc1123_date())
        response.set_header('Pragma', 'no-cache')

        # Encoding
        if encoding is None:
            r.append(self.to_str())
        else:
            r.append(self.to_str(encoding))

        data = '\n'.join(r)

        response.set_header('Content-Type', 'application/x-zope-edit')
        return data


    #######################################################################
    # Edit / Upload
    upload_form__access__ = 'is_allowed_to_edit'
    upload_form__label__ = u'Edit'
    upload_form__sublabel__ = u'Upload'
    def upload_form(self, context):
        handler = self.get_object('/ui/file/upload.xml')
        return stl(handler)


    upload__access__ = 'is_allowed_to_edit'
    def upload(self, context):
        file = context.get_form_value('file')

        if file is None:
            return context.come_back(u'No file has been entered.')

        # Check wether the handler is able to deal with the uploaded file
        filename, mimetype, data = file
        try:
            self.load_state_from_string(data)
        except:
            self.load_state()
            message = (u'Upload failed: either the file does not match this'
                       u' document type ($mimetype) or it contains errors.')
            return context.come_back(message, mimetype=self.get_mimetype())

        return context.come_back(u'Version uploaded.')


register_object_class(File)
register_object_class(File, format="application/octet-stream")
