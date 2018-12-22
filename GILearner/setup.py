from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import sys
import numpy

if sys.platform == 'linux':
    EXTRAS_COMPILE_ARGS = ['-DUSE_OPEN_MP', '-fopenmp',
                           '-std=c++11', '-O3']
    EXTRAS_LINK_ARGS = ['-fopenmp']
else:
    EXTRAS_COMPILE_ARGS = ['-DUSE_OPEN_MP', '/openmp',
                           '/Ox', '/Oi', '/GL', '/Zc:inline']
    EXTRAS_LINK_ARGS = ['/openmp'] 
setup(
    name='gi_learning',
    ext_modules=[
        Extension('gi_learning',
                  sources=["gi_learning.pyx", "src/EDSM.cpp", 
                           "src/BlueFringe.cpp",
                           "src/DFA.cpp", "src/BlueRedDFA.cpp", 
                           "src/LSTAR.cpp",
                           "src/utilities.cpp"],
                  include_dirs=['include', numpy.get_include()],
                  extra_compile_args=EXTRAS_COMPILE_ARGS,
                  extra_link_args=EXTRAS_LINK_ARGS,
                  language="c++")
    ],
    cmdclass={'build_ext': build_ext}
)
