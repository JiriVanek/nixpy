# -*- coding: utf-8 -*-
# Copyright © 2018, German Neuroinformatics Node (G-Node)
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted under the terms of the BSD License. See
# LICENSE file in the root of the Project.
import sys
import os
import platform
from glob import glob

import distutils.sysconfig
from distutils import ccompiler
from distutils.errors import CompileError, LinkError


WINDOWS = False
if platform.platform().startswith("Windows"):
    WINDOWS = True


def cc(filenames, dest,
       library_dirs=None, include_dirs=None,
       libraries=None, compile_args=None,
       runtime_lib_dirs=None):
    compiler = ccompiler.new_compiler()

    distutils.sysconfig.customize_compiler(compiler)
    compiler.set_library_dirs(library_dirs)
    compiler.set_include_dirs(include_dirs)
    compiler.set_libraries(libraries)
    compiler.set_runtime_library_dirs(runtime_lib_dirs)

    try:
        objnames = compiler.compile(filenames, output_dir=dest,
                                    extra_postargs=compile_args)
        for obj in objnames:
            execname, ext = os.path.splitext(obj)
            compiler.link_executable(
                [obj], execname, output_dir=dest,
                target_lang="c++",
            )
    except (CompileError, LinkError):
        return False
    return True


def maketests(dest):
    scriptloc, _ = os.path.split(os.path.abspath(__file__))
    os.chdir(scriptloc)
    filenames = glob("*.cpp")
    nix_inc_dir = os.getenv('NIX_INCDIR', '/usr/local/include/nixio-1.0')
    nix_lib_dir = os.getenv('NIX_LIBDIR', '/usr/local/lib')

    boost_inc_dir = os.getenv('BOOST_INCDIR', '/usr/local/include')
    boost_lib_dir = os.getenv('BOOST_LIBDIR', '/usr/local/lib')
    library_dirs = [boost_lib_dir, nix_lib_dir]
    include_dirs = [boost_inc_dir, nix_inc_dir, 'src']
    runtime_dirs = ["/usr/local/lib"]
    llp = os.getenv("LD_LIBRARY_PATH", None)
    if llp is not None:
        runtime_dirs.append(llp)
    libraries = ["nixio"]
    compile_args = ["--std=c++11"]
    if WINDOWS:
        compile_args = []

    print("Compiling {}".format(" ".join(filenames)))
    success = cc(filenames, dest,
                 library_dirs=library_dirs,
                 include_dirs=include_dirs,
                 libraries=libraries,
                 compile_args=compile_args,
                 runtime_lib_dirs=runtime_dirs)
    if success:
        print("Done")
    else:
        print("Failed")
    return success


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Need a target dir")
        sys.exit(1)

    dest = sys.argv[1]
    sys.exit(not maketests(dest))