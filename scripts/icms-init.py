#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2005-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2006-2007 Hervé Cauwelier <herve@itaapy.com>
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
from optparse import OptionParser
from os import mkdir
import sys

# Import from itools
import itools
from itools.catalog import make_catalog, CatalogAware
from itools.handlers import Config, Database, get_handler
from itools.uri import get_absolute_reference
from itools.cms.root import Root
from itools.cms.utils import generate_password


def init(parser, options, target):
    try:
        mkdir(target)
    except OSError:
        parser.error('can not create the instance (check permissions)')

    # Create the config file
    config = Config()
    # The modules
    comment = [
        'The variable "modules" lists the Python modules or packages that',
        'will be loaded when the applications starts.',
        '',
        'modules = ']
    if options.root:
        config.set_value('modules', options.root, comment=comment)
    else:
        config.append_comment(comment)
    # The address
    comment = [
        'The variable "address" defines the internet address the web server',
        'will listen to for HTTP connections.',
        '',
        'address = 127.0.0.1']
    if options.address:
        config.set_value('address', options.address, comment=comment)
    else:
        config.append_comment(comment)
    # The port
    comment = [
        'The variable "port" defines the port number the web server will',
        'listen to for HTTP connections.',
        '',
        'port = 8080']
    if options.port:
        config.set_value('port', options.port, comment=comment)
    else:
        config.append_comment(comment)
    # The SMTP host
    comment = [
        'The variable "smtp-host" defines the name or IP address of the SMTP',
        'relay. This option is required for the application to send emails.',
        '',
        'smtp-host = localhost']
    if options.smtp_host:
        config.set_value('smtp-host', options.smtp_host, comment=comment)
    else:
        config.append_comment(comment)
    # Save the file
    config.save_state_to('%s/config.conf' % target)

    # Load the root class
    if options.root is None:
        root_class = Root
    else:
        exec('import %s' % options.root)
        exec('root_class = %s.Root' % options.root)

    # Get the email address for the init user
    if options.email is None:
        sys.stdout.write("Type your email address: ")
        email = sys.stdin.readline().strip()
    else:
        email = options.email
    # Get the password
    if options.password is None:
        password = generate_password()
    else:
        password = options.password

    # Build the instance on memory
    database = Database()
    mkdir('%s/database' % target)
    base = get_absolute_reference(target).resolve2('database')
    # Make the root
    folder = database.get_handler(base)
    root = root_class._make_object(folder, email, password)
    database.save_changes()
    # Index everything
    catalog = make_catalog('%s/catalog' % target, *root._catalog_fields)
    for handler in root.traverse_objects():
        if isinstance(handler, CatalogAware):
            catalog.index_document(handler)
    catalog.save_changes()

    # Bravo!
    print '*'
    print '* Welcome to itools.cms'
    print '* A user with administration rights has been created for you:'
    print '*   username: %s' % email
    print '*   password: %s' % password
    print '*'
    print '* To start the new instance type:'
    print '*   icms-start.py %s' % target
    print '*'



if __name__ == '__main__':
    # The command line parser
    usage = '%prog [OPTIONS] TARGET'
    version = 'itools %s' % itools.__version__
    description = 'Creates a new instance of itools.cms with the name TARGET.'
    parser = OptionParser(usage, version=version, description=description)
    parser.add_option('-a', '--address', help='listen to IP ADDRESS')
    parser.add_option('-p', '--port', type='int', help='listen to PORT number')
    parser.add_option('-r', '--root',
        help='use the ROOT handler class to init the instance')
    parser.add_option('-e', '--email', help='e-mail address of the admin user')
    parser.add_option('-w', '--password',
        help='use the given PASSWORD for the admin user')
    parser.add_option('-s', '--smtp-host',
        help='use the given SMTP_HOST to send emails')

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('incorrect number of arguments')

    target = args[0]

    # Action!
    init(parser, options, target)
