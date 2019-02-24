#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import os
import glob
from os import path as osp
from distutils.command.build import build as _build_orig

import __pkginfo__


# --- Classes et fonctions utitlitaires ---------------------------------------


SETUPTOOLS = False
try:
    from setuptools import setup, find_packages, Command
    SETUPTOOLS = True
except:
    from distutils.core import setup, Command

    def find_packages(path, base="", exclude=[]):
        """
        Find all packages in path
        """
        pkg = {}
        for item in os.listdir(path):
            dossier = osp.join(path, item)
            if osp.isdir(dossier) and osp.isfile(osp.join(dossier, '__init__.py')):
                if base:
                    module_name = "%(base)s.%(item)s" % vars()
                else:
                    module_name = item

                if len([txt for txt in exclude if dossier in glob.glob(osp.join(path, txt))]) == 0:
                    pkg[module_name] = dossier
                    pkg.update(find_packages(dossier, module_name, exclude))
        return pkg


def bootscript():
    nom = 'sitecustomize.py'
    with open(nom, 'w') as fp:
        fp.write("# -*- coding: UTF-8 -*-\n\n")
        fp.write("import sys\n")
        fp.write("sys.setdefaultencoding('utf-8')\n")
        fp.write("del sys\n")
    return nom


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
            pattern = osp.join(source, pattern)
            for filename in glob.glob(pattern):
                if osp.isfile(filename):
                    targetpath = osp.join(target, osp.relpath(filename, source))
                    path = osp.dirname(targetpath)
                    match.setdefault(path, []).append(filename)
        ret += sorted(match.items())

    return ret


class Buildrc(Command):
    description = "build resources file (images_rc)"
    user_options = []

    def initialize_options(self):
        self.build_dir = self.distribution.__dict__['command_obj']['build'].build_base

    def finalize_options(self):
        pass

    def run(self):
        chemin_rc = osp.join(self.build_dir, 'images_rc')

        if self.distribution.data_files:
            # Creation du script de liaison:
            f = open(chemin_rc, 'w')
            for dest, _res_liste in self.distribution.data_files:
                f.write(u"%s\n" % dest)
            f.close()

            packages_data = dict(self.distribution.data_files)
            if '' in packages_data:
                packages_data[''] += [chemin_rc]
            else:
                packages_data[''] = [chemin_rc]

            self.distribution.data_files = packages_data.items()


class Build(_build_orig):
    sub_commands = _build_orig.sub_commands + [('build_rc', None), ]


# --- Options génériques du setup ---------------------------------------------


packages = [pkg for pkg in find_packages(".", exclude=["test", "test.*", ".*test", ".*test.*", "*test"])]

packages_data = {}
for source, target, patterns in __pkginfo__.ressources:
    packages_data[source.replace(osp.sep, '.')] = patterns

# Options génériques pour executer les commandes:
#  - bdist (built distribution)
#  - sdist (source distribution)

options = {'name': __pkginfo__.nom_dist_package,
           'version': __pkginfo__.version,
           'description': __pkginfo__.desc_courte,
           'long_description': __pkginfo__.desc_longue,
           'license': __pkginfo__.licence,
           'author': __pkginfo__.auteur,
           'author_email': __pkginfo__.email,
           'url': __pkginfo__.site,
           'packages': packages,
           'package_data': packages_data,  # utilisé par bdist
           'install_requires': __pkginfo__.dependences,
           'zip_safe': False,
           'platforms': ["linux", "darwin", "win32"],
           }

if SETUPTOOLS:
    options['entry_points'] = {'console_scripts': ["%s = %s:%s" % (target, osp.splitext(source)[0].replace('/', '.'), fonction)
                                                   for target, source, fonction in __pkginfo__.scripts]}
else:
    options['scripts'] = []
    if not osp.isdir('scripts'):
        os.makedirs('scripts')
    for target, source, fonction in __pkginfo__.scripts:
        target = osp.join('scripts', target)
        with open(target, 'w') as fp:
            fp.write(open(source).read())
        options['scripts'].append(target)


# --- Options spécifiques à Windows (py2exe) ----------------------------------


if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
    import py2exe
    options['platforms'] = ["win32"]
    # site-packages étant zippé dans les distributions binaire les ressources
    # doivent êtres externalisées
    options.pop('package_data')
    options['data_files'] = find_data_files(__pkginfo__.ressources)
    options['windows'] = [{
        'script': __pkginfo__.scripts[0][1],
        'dest_base': __pkginfo__.nom_dist_package,
        'icon_resources': [(1, osp.join(__pkginfo__.nom_python_module, 'images', 'icon.ico'))],
    }]
    options['options'] = {
        'py2exe': {'packages': [__pkginfo__.nom_python_module],
                   'custom_boot_script': bootscript(),
                   'dll_excludes': ['MSVCP90.dll']}
    }


# --- Options spécifiques à Mac OSX (py2app) ----------------------------------


if len(sys.argv) >= 2 and sys.argv[1] == 'py2app':
    import py2app
    options['platforms'] = ["darwin"]
    # site-packages étant zippé dans les distributions binaire les ressources
    # doivent êtres externalisées
    options.pop('package_data')
    options['data_files'] = find_data_files(__pkginfo__.ressources)
    options['app'] = [__pkginfo__.scripts[0][1]]
    options['options'] = {
        'py2app': {'site_packages': False,
                   'argv_emulation': True,
                   'iconfile': osp.join(__pkginfo__.nom_python_module, 'images', 'icon.icns'),
                   'extra_scripts': bootscript()}
    }


if __name__ == '__main__':
    # Execution
    setup(cmdclass={'build': Build, 'build_rc': Buildrc}, **options)
