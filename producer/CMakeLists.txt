cmake_minimum_required(VERSION 3.13)

project(evproducer VERSION 1.0)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "-Wall -Wno-unused-result")

add_subdirectory(libaxidma)

file(GLOB_RECURSE SRC_FILES ${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp)
add_executable(${PROJECT_NAME} ${SRC_FILES})

target_include_directories(${PROJECT_NAME} PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_include_directories(${PROJECT_NAME} PUBLIC ${AXIDMA_INC_DIR})

target_link_libraries(${PROJECT_NAME} PUBLIC axidma)

find_package(fmt REQUIRED)
target_link_libraries(${PROJECT_NAME} PUBLIC fmt::fmt)

find_package(ZeroMQ REQUIRED)
target_link_libraries(${PROJECT_NAME} PUBLIC zmq)

find_package(cppzmq REQUIRED)

target_link_libraries(${PROJECT_NAME} PUBLIC stdc++fs pthread)
