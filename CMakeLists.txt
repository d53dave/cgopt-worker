cmake_minimum_required(VERSION 3.2)
project(csaopt_worker)

set(CMAKE_CXX_STANDARD 11) # adds -std=c++11
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_SOURCE_DIR}/CMakeModules)

set(PROJECT_INCLUDE_DIR ${PROJECT_SOURCE_DIR}/include)
include_directories("${PROJECT_INCLUDE_DIR}")

# ZMQ
find_package(ZMQ REQUIRED)
if (ZMQ_FOUND)
    include_directories(${ZMQ_INCLUDE_DIRS})
    list(APPEND ${PROJECT_NAME}_EXTERNAL_LIBRARIES "${ZMQ_LIBRARIES}")
endif ()

# ZMQPP
find_package(ZMQPP REQUIRED)
if (ZMQPP_FOUND)
    include_directories(${ZMQPP_INCLUDE_DIRS})
    list(APPEND ${PROJECT_NAME}_EXTERNAL_LIBRARIES "${ZMQPP_LIBRARIES}")
endif ()

find_package(Threads REQUIRED)
find_package(CUDA REQUIRED)

include(ExternalProject)
file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/include/tidings)
set(CAPNPC_OUTPUT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/include/tidings)

ExternalProject_Add(
        csaopt-tidings
        GIT_REPOSITORY https://github.com/d53dave/csaopt-tidings.git
        TIMEOUT 10
        LOG_DOWNLOAD ON
        CMAKE_CACHE_ARGS -DCAPNPC_OUTPUT_DIR:STRING=${CAPNPC_OUTPUT_DIR}
        BUILD_COMMAND "make"
        INSTALL_COMMAND ""
)

ExternalProject_Add(
        cpp-hocon
        GIT_REPOSITORY https://github.com/puppetlabs/cpp-hocon
        GIT_TAG 0.1.5
        TIMEOUT 10
        LOG_DOWNLOAD ON
        BUILD_COMMAND "make"
        INSTALL_COMMAND ""
)

set(SOURCE_FILES
        src/MessageQueueClient.h, src/MessageQueueClient.cpp
        src/kj/KjStringPipe.h,
        src/main.cpp)

set(CUDA_FILES
        src/CUDA/OptRunner.cu
        src/CUDA/OptRunner.h)

cuda_compile(CUDA_Os ${CUDA_FILES} OPTIONS -G)

set(CUDA_NVCC_FLAGS ${CUDA_NVCC_FLAGS}--relocatable-device-code=false
        -gencode arch=compute_30,code=compute_30 -gencode arch=compute_30,code=sm_30)

cuda_add_executable(csaopt_worker ${CUDA_FILES} ${SOURCE_FILES})
target_link_libraries(csaopt_worker zmq zmqpp Threads::Threads)
add_dependencies(csaopt_worker csaopt-tidings)