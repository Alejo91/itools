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
from email.MIMEText import MIMEText
from email.Utils import formatdate
from time import time
import traceback
from types import GeneratorType

# Import from itools
import itools
from itools import get_abspath
from itools.datatypes import FileName
from itools import vfs
from itools.catalog import (make_catalog, CatalogAware, TextField,
    KeywordField, IntegerField, BoolField)
from itools.handlers import Folder as FolderHandler, Config
from itools.stl import stl
from itools.web import get_context
from itools.xml import Parser
from itools.xhtml import stream_to_str_as_html
from itools.uri import Path

# Import from itools.cms
from access import RoleAware
from text import PO
from users import UserFolder
from website import WebSite
from handlers import Metadata
from registry import register_object_class, get_object_class
from folder import Folder
from skins import ui
from utils import crypt_password


# itools source and target languages
config = get_abspath(globals(), '../setup.conf')
config = Config(config)
itools_source_language = config.get_value('source_language')
itools_target_languages = config.get_value('target_languages')



class Root(WebSite):

    class_id = 'iKaaro'
    class_version = '20070816'
    class_title = u'iKaaro'
    class_icon16 = 'images/Root16.png'
    class_icon48 = 'images/Root48.png'
    class_views = [
        ['browse_content?mode=list',
         'browse_content?mode=thumbnails'],
        ['new_resource_form'],
        ['edit_metadata_form',
         'virtual_hosts_form',
         'anonymous_form',
         'languages_form',
         'contact_options_form'],
        ['permissions_form',
         'new_user_form'],
        ['last_changes']]

    __fixed_handlers__ = ['users', 'ui']


    __roles__ = [
        {'name': 'ikaaro:admins', 'title': u'Admin'}]


    # Default email address to use in the Form fields when sending emails
    contact_email = None


    ########################################################################
    # Override itools.web.root.Root
    ########################################################################
    def init(self, context):
        # Set the list of needed resources. The method we are going to
        # call may need external resources to be rendered properly, for
        # example it could need an style sheet or a javascript file to
        # be included in the html head (which it can not control). This
        # attribute lets the interface to add those resources.
        context.styles = []
        context.scripts = []


    def get_user(self, name):
        users = self.get_object('users')
        if users.has_object(name):
            return users.get_object(name)
        return None


    def after_traverse(self, context, body):
        # If there is not content type and the body is not None,
        # wrap it in the skin template
        if context.response.has_header('Content-Type'):
            if isinstance(body, (list, GeneratorType, Parser)):
                body = stream_to_str_as_html(body)
            return body

        if isinstance(body, str):
            body = Parser(body)
        return self.get_skin().template(body)


    ########################################################################
    # Skeleton
    ########################################################################
    _catalog_fields = [
        KeywordField('abspath', is_stored=True),
        TextField('text'),
        TextField('title', is_stored=True),
        KeywordField('owner', is_stored=True),
        BoolField('is_role_aware'),
        KeywordField('format', is_stored=True),
        KeywordField('workflow_state', is_stored=True),
        KeywordField('members'),
        # Users
        KeywordField('email', is_stored=True),
        TextField('lastname', is_stored=True),
        TextField('firstname', is_stored=True),
        KeywordField('username', is_stored=True), # Login Name
        # Folder's view
        KeywordField('parent_path'),
        KeywordField('paths'),
        KeywordField('name', is_stored=True),
        KeywordField('mtime', is_indexed=False, is_stored=True),
        IntegerField('size', is_indexed=False, is_stored=True),
        # Versioning Aware
        BoolField('is_version_aware'),
        KeywordField('last_author', is_indexed=False, is_stored=True),
        ]


    @classmethod
    def _make_object(cls, folder, email, password):
        # The metadata
        kw = {'ikaaro:admins': ('0',)}
        metadata = cls.build_metadata(**kw)
        folder.set_handler('.metadata', metadata)
        # User Folder
        kw = {'dc:title': {'en': u'Users'}}
        users = UserFolder.build_metadata(owner=None, **kw)
        folder.set_handler('users.metadata', users)
        # Default User
        password = crypt_password(password)
        kw = {'ikaaro:email': email, 'ikaaro:password': password}
        user = get_object_class('user').build_metadata(owner='0', **kw)
        folder.set_handler('users/0.metadata', user)
        # Return
        return cls(metadata)


    ########################################################################
    # Publish
    ########################################################################
    def unauthorized(self, context):
        return self.login_form(context)


    def forbidden(self, context):
        message = (u'Access forbidden, you are not authorized to access'
                   u' this resource.')
        return self.gettext(message).encode('utf-8')


    def internal_server_error(self, context):
        namespace = {'traceback': traceback.format_exc()}

        handler = self.get_object('/ui/root/internal_server_error.xml')
        return stl(handler, namespace, mode='html')


    def not_found(self, context):
        namespace = {'uri': str(context.uri)}

        # Don't show the skin if it is not going to work
        request = context.request
        if request.has_header('x-base-path'):
            try:
                self.get_handler('%s/ui' % request.get_header('x-base-path'))
            except LookupError:
                response = context.response
                response.set_header('content-type', 'text/html; charset=UTF-8')

        handler = self.get_object('/ui/root/not_found.xml')
        return stl(handler, namespace)


    ########################################################################
    # Traverse
    ########################################################################
    def _get_object(self, name):
        if name == 'ui':
            return ui
        return Folder._get_object(self, name)


    def _get_names(self):
        names = [ x for x in Folder._get_names(self) if x ]
        return names + ['ui']


    ########################################################################
    # API
    ########################################################################
    def get_usernames(self):
        return self.get_handler('users').get_usernames()


    def get_document_types(self):
        return WebSite.get_document_types(self) + [WebSite]


    ########################################################################
    # Search
    def search(self, query=None, **kw):
        catalog = get_context().server.catalog
        return catalog.search(query, **kw)


    ########################################################################
    # Skins
    def get_skin(self):
        context = get_context()
        # Back-Office
        hostname = context.uri.authority.host
        if hostname[:3] in ['bo.', 'bo-']:
            return self.get_object('ui/aruni')
        # Fron-Office
        skin = context.site_root.class_skin
        return self.get_object(skin)


    def get_available_languages(self):
        """
        Returns the language codes for the user interface.
        """
        source = itools_source_language
        target = itools_target_languages
        # A package based on itools
        cls = self.__class__
        if cls is not Root:
            exec('import %s as pkg' % cls.__module__.split('.', 1)[0])
            config = Path(pkg.__path__[0]).resolve2('setup.conf')
            config = Config(str(config))
            source = config.get_value('source_language', default=source)
            target = config.get_value('target_languages', default=target)

        target = target.split()
        if source in target:
            target.remove(source)

        target.insert(0, source)
        return target


    ########################################################################
    # Email
    def send_email(self, from_addr, to_addr, subject, body, **kw):
        # Check input data
        if not isinstance(subject, unicode):
            raise TypeError, 'the subject must be a Unicode string'
        if not isinstance(body, unicode):
            raise TypeError, 'the body must be a Unicode string'

        # Build the message
        context = get_context()
        host = context.uri.authority.host
        encoding = 'utf-8'
        body = body.encode(encoding)
        message = MIMEText(body, _charset=encoding)
        message['Subject'] = '[%s] %s' % (host, subject.encode(encoding))
        message['Date'] = formatdate(localtime=True)
        message['From'] = from_addr
        message['To'] = to_addr
        # Send email
        server = context.server
        server.send_email(message)


    ########################################################################
    # Back Office
    ########################################################################

    ########################################################################
    # About
    about__access__ = True
    about__label__ = u'About'
    about__sublabel__ = u'About'
    def about(self, context):
        namespace = {}
        namespace['version'] = itools.__version__

        handler = self.get_object('/ui/root/about.xml')
        return stl(handler, namespace)


    ########################################################################
    # Credits
    credits__access__ = True
    credits__label__ = u'About'
    credits__sublabel__ = u'Credits'
    def credits(self, context):
        context.styles.append('/ui/credits.css')

        # Build the namespace
        credits = get_abspath(globals(), '../CREDITS')
        names = []
        for line in vfs.open(credits, 'r').readlines():
            if line.startswith('N: '):
                names.append(line[3:].strip())

        namespace = {'hackers': names}

        handler = self.get_object('/ui/root/credits.xml')
        return stl(handler, namespace)


    ########################################################################
    # License
    license__access__ = True
    license__label__ = u'About'
    license__sublabel__ = u'License'
    def license(self, context):
        handler = self.get_object('/ui/root/license.xml')
        return stl(handler)


    ########################################################################
    # Maintenance
    ########################################################################

    #######################################################################
    # Check groups
    def get_groups(self):
        """
        Returns a list with all the subgroups, including the subgroups of
        the subgroups, etc..
        """
        results = self.search(is_role_aware=True)
        return [ x.abspath for x in results.get_documents() ]


    check_groups__access__ = 'is_admin'
    check_groups__label__ = u'Maintenance'
    check_groups__sublabel__ = u'Check Groups'
    def check_groups(self, context):
        namespace = {}

        groups = []
        root_users = self.get_handler('users').get_usernames()
        for path in self.get_groups():
            group = self.get_handler(path)
            members = group.get_members()
            members = set(members)
            if not members.issubset(root_users):
                missing = list(members - root_users)
                missing.sort()
                missing = ' '.join(missing)
                groups.append({'path': path, 'users': missing})
        namespace['groups'] = groups

        handler = self.get_object('/ui/root/check_groups.xml')
        return stl(handler, namespace)


    fix_groups__access__ = 'is_admin'
    def fix_groups(self, context):
        root_users = self.get_handler('users').get_usernames()
        for path in self.get_groups():
            group = self.get_handler(path)
            members = group.get_members()
            group.set_user_role(members - root_users, None)

        return context.come_back(u'Groups fixed.')


    #######################################################################
    # Update
    #######################################################################
    def update_20070816(self):
        from forum import Message

        for handler in self.traverse_objects():
            # Forum messages are formal XHTML documents
            # XXX To test with old versions (TXT and XHTML fragments)
            if isinstance(handler, Message):
                body = handler.get_body()
                if body is None:
                    # Re-generage message with document fragment
                    data = handler.to_str()
                    new_message = Message(data=data)
                    handler.set_changed()
                    handler.events = new_message.events


register_object_class(Root)
