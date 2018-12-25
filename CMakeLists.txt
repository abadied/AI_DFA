cmake_minimum_required(VERSION 3.9)
project(gi_learning)

set(CMAKE_CXX_STANDARD 11)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

add_definitions(-DUSE_OPEN_MP)
if (MSVC)
    set(CMAKE_CXX_FLAGS_RELEASE "/openmp")
else()
    set(CMAKE_CXX_FLAGS_RELEASE "-fopenmp")
endif()

find_package(OpenMP)
if (OPENMP_FOUND)
    set (CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
    set (CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
    set (CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS}")
endif()

if (MSVC)
    set(CMAKE_CXX_FLAGS_RELEASE "/Ox /Oi /GL /Zc:inline")
else()
    set(CMAKE_CXX_FLAGS_RELEASE "-O3")
endif()

include_directories(include)
add_executable(gi_learning
        include/utilities.hpp
        include/DFA.hpp
        include/BlueFringe.hpp
        include/BlueStar.hpp
        include/BlueRedDFA.hpp
        include/EDSM.hpp
        include/LSTAR.hpp
        src/utilities.cpp
        src/DFA.cpp
        src/BlueFringe.cpp
        src/BlueStar.cpp
        src/BlueRedDFA.cpp
        src/EDSM.cpp
        src/LSTAR.cpp
        src/gi-learning.cpp
        )
