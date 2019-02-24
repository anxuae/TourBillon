#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__doc__ = "Setup file used by `setuptools` to build the installation packages."

#--- Import ---------------------------------------------------------------

import sys
import os
import re
import imp
import glob
import inspect
from os import path as osp
from distutils.command.build import build as _build_orig
from distutils.util import convert_path

uses_setuptools = False
try:
    from setuptools import setup, find_packages, Extension, Command
    print "Info: setuptools detected"
    uses_setuptools = True
except:
    from distutils.core import setup, Extension, Command

    def is_package(path):
        return (
            os.path.isdir(path) and
            os.path.isfile(os.path.join(path, '__init__.py'))
        )

    def find_packages(path, base="", exclude=[]):
        """
        Find all packages in path
        """
        packages = {}
        for item in os.listdir(path):
            dir = os.path.join(path, item)
            if is_package(dir):
                if base:
                    module_name = "%(base)s.%(item)s" % vars()
                else:
                    module_name = item

                if len([txt for txt in exclude if dir in glob.glob(os.path.join(path, txt))]) == 0:
                    packages[module_name] = dir
                    packages.update(find_packages(dir, module_name, exclude))
        return packages


def find_data_files(package_data):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    ret = []
    for source, target, patterns in package_data:
        if glob.has_magic(source) or glob.has_magic(target):
            raise ValueError("Magic not allowed in src, target")
        match = {}
        for pattern in patterns:
            pattern = os.path.join(source, pattern)
            for filename in glob.glob(pattern):
                if os.path.isfile(filename):
                    targetpath = os.path.join(target, os.path.relpath(filename, source))
                    path = os.path.dirname(targetpath)
                    match.setdefault(path, []).append(filename)
        ret += sorted(match.items())

    return ret

#--- Informations -------------------------------------------------------------

python_module_name = "tourbillon"

dist_package_name = "TourBillon"

short_desc = u"TourBillon - logiciel officiel de la Billionnière"

long_desc = \
    u"""TourBillon, est le progromme officile de la Billonnière, utilisé
lors des tournois de billon de printemps (Mai) et d'été (Août).

Ce programme permet de gerer un nombre variable d'équipes lors d'
un tournoi de billon. Deux interfaces sont incluses dans le
package, une interface en ligne de commande et une interface
graphique"""

ce_fichier = inspect.currentframe().f_code.co_filename
chemin_init_ = os.path.join(os.path.dirname(os.path.abspath(ce_fichier)), 'tourbillon/__init__.py')
num_version = imp.load_source('tourbillon', chemin_init_).__version__

version = '.'.join([str(num) for num in num_version])

entry_scripts = [  # (script après install, chemin, fonction to be called)
    ("trb", "tourbillon/trb.py", "run"), ]

required_dependencies = [  # dist_name + version constraint
    "wxpython>=2.8",
    "pyyaml>=3.0"]

packages = [pkg for pkg in find_packages(".", exclude=["test", "test.*", ".*test", ".*test.*", "*test"])]

packages_data_files = [  # (source, target, pattern)
    ('', '', ["license.txt"]),
    ('tourbillon/images', 'skin', ["*.png", "*.txt", "*.jpg"])]

packages_data = {}
for source, target, patterns in packages_data_files:
    packages_data[source.replace(osp.sep, '.')] = patterns

#--- Définition des options du Setup ------------------------------------------

# Options génériques pour la création de bdist (built distribution) et sdist (source distribution)
options = {
    'name':              dist_package_name,
    'version':           version,
    'description':       short_desc,
    'long_description':  long_desc,
    'license':           "GNU GPL",
    'author':            "La Billonnière",
    'author_email':      "labillonniere@gmail.fr",
    'url':               'https://www.facebook.com/labillonniere',
    'packages':          packages,
    'package_data':      packages_data,  # ressources ajoutées à bdist et py2app
    'install_requires':  required_dependencies,
    'zip_safe':          False,
    'platforms':         ["linux", "darwin", "win32"],
}

if uses_setuptools:
    options['entry_points'] = {'console_scripts': ["%s = %s:%s" % (target, os.path.splitext(source)[0].replace('/', '.'), fonction)
                                                   for target, source, fonction in entry_scripts]}
else:
    options['scripts'] = [source for target, source, fonction in entry_scripts]

# Options spécifiques à la compilation d'executable Windows
if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
    try:
        import py2exe
    except ImportError:
        print 'Imporatation erreur: py2exe.   Windows exe ne peut pas être généré.'
        sys.exit(0)

    options['platforms'] = ["win32"]
    # site-packages etant zippé dans les distributions binaire les ressources
    # doivent êtres externalisées
    options['data_files'] = find_data_files(packages_data_files)
    options['windows'] = [{
        'script':            'tourbillon/trb.py',
        'dest_base':         'TourBillon',
        'icon_resources':    [(1, 'tourbillon/images/icon.ico')],
    }]
    options['options'] = {
        'py2exe':            {'packages': ['tourbillon']}
    }

# Options spécifiques à la compilation d'executable Mac OSX
if len(sys.argv) >= 2 and sys.argv[1] == 'py2app':
    try:
        import py2app
    except ImportError:
        print 'Imporatation erreur: py2app.   Mac app ne peut pas être généré.'
        sys.exit(0)

    options['platforms'] = ["darwin"]
    # site-packages etant zippé dans les distributions binaire les ressources
    # doivent êtres externalisées
    options['data_files'] = find_data_files(packages_data_files)
    options['app'] = ['tourbillon/trb.py']
    options['options'] = {
        'py2app':         {
            'site_packages': True,
            'argv_emulation': True,
            'iconfile': 'tourbillon/images/icon.icns',
        }
    }

#--- Ajout d'action avant le build --------------------------------------------


class build_rc(Command):
    description = "build resources file (images_rc)"
    user_options = []

    def initialize_options(self):
        self.build_dir = self.distribution.__dict__['command_obj']['build'].build_base

    def finalize_options(self):
        pass

    def run(self):
        chemin_rc = os.path.join(self.build_dir, 'images_rc')

        if self.distribution.data_files:
            # Creation du script de liaison:
            f = open(chemin_rc, 'w')
            for dest, res_liste in self.distribution.data_files:
                f.write(u"%s\n" % dest)
            f.close()

            packages_data = dict(self.distribution.data_files)
            if '' in packages_data:
                packages_data[''] += [chemin_rc]
            else:
                packages_data[''] = [chemin_rc]

            self.distribution.data_files = packages_data.items()


class build(_build_orig):
    sub_commands = _build_orig.sub_commands + [('build_rc', None), ]

cmdclass = {'build': build,
            'build_rc': build_rc, }


#--- Execution du Setup -------------------------------------------------------

setup(cmdclass=cmdclass, **options)
