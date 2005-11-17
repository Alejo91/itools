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
from base64 import decodestring
from copy import copy
import datetime
import os
import socket
import thread
import traceback
from urllib import unquote

# Import from itools
from itools.resources.socket import File
from itools.handlers import transactions
from itools.web.exceptions import BadRequest, Forbidden, UserError
from itools.web.context import Context, get_context, set_context
from itools.web.request import Request
from itools.web.response import Response



class Pool(object):
    # XXX Right now we only support one handler tree (may use semaphores)

    def __init__(self, root):
        self.lock = thread.allocate_lock()
        self.pool = [root]


    def pop(self):
        self.lock.acquire()
        return self.pool.pop()


    def push(self, root):
        self.pool.append(root)
        self.lock.release()



def handle_request(connection, server):
    # Build the request object
    resource = File(connection)
    try:
        request = Request(resource)
    except BadRequest:
        response = Response(status_code=400)
        response.set_body('Bad Request')
        response = response.to_str()
        connection.send(response)
        return

    # Build and set the context
    context = Context(request, '%s:%s' % (server.address, server.port))
    set_context(context)

    # Get the root handler
    root = server.pool.pop()
    context.root = root

    # Authenticate
    cname = '__ac'
    cookie = context.get_cookie(cname)
    if cookie is not None:
        cookie = unquote(cookie)
        cookie = decodestring(cookie)
        username, password = cookie.split(':', 1)
        try:
            user = root.get_handler('users/%s' % username)
        except LookupError:
            pass
        except:
            server.log_error()
        else:
            if user.authenticate(password):
                context.user = user
    user = context.user

    # Hook (used to set the language)
    try:
        root.before_traverse()
    except:
        server.log_error()

    # Traverse
    try:
        handler = root.get_handler(context.path)
    except LookupError:
        # Not Found (response code 404)
        method = root.not_found
    except:
        server.log_error()
        # Internal Server Error (500)
        method = root.internal_server_error
    else:
        context.handler = handler
        # Get the method
        if context.method is None:
            method = handler.get_method(request.method)
        else:
            method = handler.get_method(context.method)
        # Check security
        if method is None:
            if user is None:
                # Unauthorized (401)
                method = root.login_form
            else:
                # Forbidden (403)
                method = root.forbidden

    # Set the list of needed resources. The method we are going to
    # call may need external resources to be rendered properly, for
    # example it could need an style sheet or a javascript file to
    # be included in the html head (which it can not control). This
    # attribute lets the interface to add those resources.
    context.styles = []
    context.scripts = []

    # Get the transaction object
    transaction = transactions.get_transaction()

    try:
        # Call the method
        if method.im_func.func_code.co_flags & 8:
            response_body = method(**request.form)
        else:
            response_body = method()
    except UserError, exception:
        # Redirection
        transaction.rollback()
        goto = copy(request.referrer)
        goto.query['message'] = exception.args[0].encode('utf8')
        context.redirect(goto)
        response_body = None
    except Forbidden:
        transaction.rollback()
        if user is None:
            # Unauthorized (401)
            response_body = root.login_form()
        else:
            # Forbidden (403)
            response_body = root.forbidden()
    except:
        transaction.rollback()
        response_body = root.internal_server_error()
    else:
        # Save changes
        transaction.commit(user and user.name or 'NONE', str(request.path))

    # Set the response body
    response = context.response
    response.set_body(response_body)

    # After traverse hook
    try:
        root.after_traverse()
    except:
        server.log_error()

    # Free the root object
    server.pool.push(root)
    # Finish, send back the response
    response = response.to_str()
    connection.send(response)
    connection.close()



class Server(object):

    def __init__(self, root, address='127.0.0.1', port=None, error_log=None,
                 pid_file=None):
        if port is None:
            port = 8000
        # The application's root
        self.pool = Pool(root)
        # The address and port the server will listen to
        self.address = address
        self.port = port
        # The error and access logs
        if error_log is not None:
            error_log = open(error_log, 'a+')
        self.error_log = error_log
        # The pid file
        self.pid_file = pid_file


    def start(self):
        if self.pid_file is not None:
            pid = os.getpid()
            open(self.pid_file, 'w').write(str(pid))

        ear = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ear.bind((self.address, self.port))
        ear.listen(5)
        print 'Listen port %s' % self.port

        while True:
            try:
                connection, client_address = ear.accept()
            except socket.error:
                continue
            except:
                ear.close()
                if self.error_log is not None:
                    self.error_log.close()
                break
            else:
                thread.start_new_thread(handle_request, (connection, self))


    def log_error(self):
        context = get_context()
        request, user = context.request, context.user

        user = context.user

        # Log request
        error_log = self.error_log
        error_log.write('\n')
        error_log.write('[Error]\n')
        error_log.write('date    : %s\n' % str(datetime.datetime.now()))
        error_log.write('uri     : %s\n' % str(context.uri))
        error_log.write('referrer: %s\n' % str(request.referrer))
        error_log.write('user    : %s\n' % (user and user.name or None))
        error_log.write('\n')

        # The traceback
        traceback.print_exc(file=error_log)
        error_log.flush()
