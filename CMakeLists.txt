cmake_minimum_required(VERSION 3.16)
project(turbidity_sensor VERSION 0.1.0 LANGUAGES C CXX)

add_library(turbidity STATIC
    src/turbidity.c
)

target_include_directories(turbidity
    PUBLIC
        ${PROJECT_SOURCE_DIR}/include
)

target_compile_features(turbidity PUBLIC c_std_99)

if(MSVC)
    target_compile_options(turbidity PRIVATE /W4)
else()
    target_compile_options(turbidity PRIVATE -Wall -Wextra -Wpedantic)
    target_link_libraries(turbidity PUBLIC m)
endif()

add_executable(turbidity_calibrate
    apps/calibrate/turbidity_calibrate.c
)
target_link_libraries(turbidity_calibrate PRIVATE turbidity)

add_executable(turbidity_stream
    apps/posix/turbidity_stream.c
)
target_link_libraries(turbidity_stream PRIVATE turbidity)

enable_testing()

add_executable(turbidity_test_core
    tests/test_turbidity.c
)
target_link_libraries(turbidity_test_core PRIVATE turbidity)
add_test(NAME turbidity_core COMMAND turbidity_test_core)

add_executable(turbidity_test_stream
    tests/test_stream_app.c
)
target_link_libraries(turbidity_test_stream PRIVATE turbidity)
add_test(NAME turbidity_stream_fixture COMMAND turbidity_test_stream $<TARGET_FILE:turbidity_stream>)
