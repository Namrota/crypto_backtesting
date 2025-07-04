cmake_minimum_required(VERSION 3.10.0)
project(backtestingCpp VERSION 0.1.0 LANGUAGES C CXX)


#Specify C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)


include(CTest)
enable_testing()

# Tell CMake where to find HDF5 1.14.6
#set(HDF5_DIR "C:/Program Files/HDF_Group/HDF5/1.14.6/cmake")
# Find HDF5 package
find_package(HDF5 REQUIRED COMPONENTS C)
include_directories(${HDF5_INCLUDE_DIRS})


#Add source files
set(SOURCE_FILES
    main.cpp
    Database.cpp
    utils.cpp
    strategies/Sma.cpp
    strategies/Psar.cpp
)


#add_executable(${PROJECT_NAME} ${SOURCE_FILES})

# Create a shared library
add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})

# Include HDF5 headers
target_include_directories(${PROJECT_NAME} PRIVATE ${HDF5_INCLUDE_DIRS})
# Link against HDF5 libraries
target_link_libraries(${PROJECT_NAME}  ${HDF5_LIBRARIES} ${HDF5_C_LIBRARIES})


# Log what was found
message(STATUS "HDF5 include dirs: ${HDF5_INCLUDE_DIRS}")
message(STATUS "HDF5 libraries: ${HDF5_LIBRARIES}")
message(STATUS "HDF5 C libraries: ${HDF5_C_LIBRARIES}")
message(STATUS "CMAKE_CXX_COMPILER: ${CMAKE_CXX_COMPILER}")
message(STATUS "CMAKE_GENERATOR: ${CMAKE_GENERATOR}")
message(STATUS "CMAKE_SYSTEM_PROCESSOR: ${CMAKE_SYSTEM_PROCESSOR}")

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)