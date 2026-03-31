cmake_minimum_required(VERSION 3.16)
project(turbidity_package_smoke LANGUAGES C)

find_package(turbidity REQUIRED CONFIG)

add_executable(turbidity_package_smoke
    main.c
)

target_link_libraries(turbidity_package_smoke PRIVATE turbidity::turbidity)
