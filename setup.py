#!/usr/bin/env python

# vi:set tabsize=3:
#
# Copyright (C) 2001-2004 Ichiro Fujinaga, Michael Droettboom,
#                         and Karl MacMillan
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#

from distutils.core import setup, Extension
from distutils.util import get_platform
from distutils.sysconfig import get_python_lib
import sys, os, glob
from gamera import gamera_setup

##########################################
# generate the command line startup scripts
command_line_utils = (
   ('gamera_gui', 'gamera_gui.py',
    """#!%(executable)s
%(header)s
print "Loading GAMERA..."
try:
   from gamera.gui import gui
   gui.run()
except:
   import traceback
   print "Gamera made a fatal error:"
   print
   traceback.print_exc()
   print
   print "Press <ENTER> to exit."
   x = raw_input()
   """), )
   
if sys.platform == 'win32':
   command_line_filename_at = 1
   scripts_directory_name = "Scripts"
else:
   command_line_filename_at = 0
   scripts_directory_name = "bin/"

scripts = [x[command_line_filename_at] for x in command_line_utils] + ['gamera_post_install.py']

info = {'executable': sys.executable,
        'header'    :
        """# This file was automatically generated by the\n"""
        """# Gamera setup script on %s.\n""" } #%
for util in command_line_utils:
   if sys.platform == 'win32':
      _, file, content = util
   else:
      file, _, content = util
   fd = open(file, 'w')
   fd.write(content % info)
   fd.close()
os.chmod(file, 0700)

##########################################
# generate the plugins
plugin_extensions = []
plugins = gamera_setup.get_plugin_filenames('gamera/plugins/')
plugin_extensions = gamera_setup.generate_plugins(
   plugins, "gamera.plugins", True)

########################################
# Non-plugin extensions

ga_files = glob.glob("src/ga/*.cpp")
ga_files.append("src/knncoremodule.cpp")
graph_files = glob.glob("src/graph/*.cpp")

extensions = [Extension("gamera.gameracore",
                        ["src/gameramodule.cpp",
                         "src/sizeobject.cpp",
                         "src/pointobject.cpp",
                         "src/dimensionsobject.cpp",
                         "src/rectobject.cpp",
                         "src/regionobject.cpp",
                         "src/regionmapobject.cpp",
                         "src/rgbpixelobject.cpp",
                         "src/imagedataobject.cpp",
                         "src/imageobject.cpp",
                         "src/imageinfoobject.cpp"
                         ],
                        include_dirs=["include"],
                        **gamera_setup.extras
                        ),
              Extension("gamera.knncore", ga_files,
                        include_dirs=["include", "src/ga", "src"],
                        **gamera_setup.extras),
              Extension("gamera.graph", graph_files,
                        include_dirs=["include", "src", "src/graph"],
                        **gamera_setup.extras)]
extensions.extend(plugin_extensions)

##########################################
# Here's the basic distutils stuff

description = ("This is the Gamera installer. " +
               "Please ensure that Python and wxPython 2.4.0 " +
               "(or later) are installed before proceeding.")

lib_path = os.path.join(get_python_lib(), 'gamera')

include_path = "include/gamera"

includes = [(os.path.join(include_path, a), glob.glob(os.path.join("include/", os.path.join(a, b)))) for a, b in
            ("", "*.hpp"),
            ("plugins", "*.hpp"),
            ("vigra", "*.hxx")]

gamera_version = open("version", 'r').readlines()[0].strip()
open("gamera/__version__.py", "w").write("ver = `%s`\n\n" % gamera_version)
            
setup(name = "gamera",
      version=gamera_version,
      url = "http://gamera.sourceforge.net/",
      author = "Michael Droettboom and Karl MacMillan",
      author_email = "gamera-devel@yahoogroups.com",
      ext_modules = extensions,
      description = description,
      packages = ['gamera', 'gamera.gui', 'gamera.plugins'],
      scripts = scripts,
      data_files=[(os.path.join(lib_path, "test"), glob.glob("gamera/test/*.tiff"))] + includes)
