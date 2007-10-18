
itools is a Python library, it groups a number of packages into a single
meta-package for easier development and deployment.

The packages included are:

  itools.catalog          itools.i18n             itools.tmx
  itools.cms              itools.ical             itools.uri
  itools.csv              itools.odf              itools.vfs
  itools.datatypes        itools.pdf              itools.web
  itools.gettext          itools.rest             itools.workflow
  itools.handlers         itools.rss              itools.xhtml
  itools.html             itools.schemas          itools.xliff
  itools.http             itools.stl              itools.xml

The scripts included are:

  icatalog-inspect.py     icms-update.py          isetup-build.py
  icms-init.py            icms-update-catalog.py  isetup-copyright.py
  icms-restore.py         igettext-build.py       isetup-doc.py
  icms-start.py           igettext-extract.py     isetup-quality.py
  icms-stop.py            igettext-merge.py       isetup-update-locale.py


Requirements
------------

Python 2.5 or later is required.

For the implementation of RML (itools.pdf) to work the package reportlab [1]
must be installed.

For itools.cms, it is recommended to install PIL [2]. For the Wiki to work,
docutils [3] is required.

Apart from the Python packages listed above, itools.cms requires the commands
xlhtml, ppthtml, pdftotext, wvText and unrtf to index some types of documents.

[1] http://www.reportlab.org/
[2] http://www.pythonware.com/products/pil/
[3] http://docutils.sourceforge.net/



Install
-------

If you are reading this instructions you probably have already unpacked
the itools tarball with the command line:
    
  $ tar xzf itools-X.Y.Z.tar.gz

And changed the working directory this way:
    
  $ cd itools-X.Y.Z

So now to install itools you just need to type this:

  $ python setup.py install



Unit Tests
----------

To run the unit tests just type:
    
  $ cd test
  $ python test.py

If there are errors, please report either to the issue tracker or to
the mailing list:

  - http://bugs.ikaaro.org
  - http://mail.ikaaro.org/mailman/listinfo/itools



Documentation
-------------

The documentation is distributed as a separate package, itools-docs.
The PDF file can be downloaded from http://www.ikaaro.org/itools



Resources
---------

Home
http://www.ikaaro.org/itools

Mailing list
http://mail.ikaaro.org/mailman/listinfo/itools

Bug Tracker
http://bugs.ikaaro.org


Copyright
---------

Copyright (C) 2002-2007 Juan David Ibáñez Palomar <jdavid@itaapy.com>
Copyright (C) 2005-2007 Luis Arturo Belmar-Letelier <luis@itaapy.com>
Copyright (C) 2005-2007 Hervé Cauwelier <herve@itaapy.com>
Copyright (C) 2005-2007 Nicolas Deram <nicolas@itaapy.com>

And others. Check the CREDITS file for complete list.

Includes the DHTML Calendar, authored by Mihai Bazon and published under
the terms of the GNU Lesser General Public License.

The HTML editor is derived from Epoz (XXX), which is authored by Maik
Jablonski and Benoit Pin, and published under the terms of the Zope
Public License (ZPL) version 2.1.

Most icons used are copyrighted by the Tango Desktop Project, and licensed
under the Creative Commons Attribution Share-Alike license, including the
modifications to them. (http://creativecommons.org/licenses/by-sa/2.5/)


License
-------

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

