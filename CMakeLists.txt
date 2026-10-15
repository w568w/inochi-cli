cmake_minimum_required(VERSION 3.24)
project(inochi VERSION 0.1.0 LANGUAGES CXX)
include(FetchContent)
include(GNUInstallDirs)
find_package(Git REQUIRED)
find_program(DUB dub REQUIRED)
find_program(DC NAMES ldc2 dmd gdc REQUIRED)
find_package(SDL2 CONFIG REQUIRED)
find_package(Freetype REQUIRED)
find_package(OpenGL REQUIRED)

# Creator and SDK share a fixed format/algorithm baseline; only their patches vary.
FetchContent_Declare(creator GIT_REPOSITORY https://github.com/Inochi2D/inochi-creator.git GIT_TAG 371e5f4e21117102dbecc82371bfd9a6e2f5df02 GIT_SUBMODULES "" PATCH_COMMAND ${GIT_EXECUTABLE} reset --hard HEAD COMMAND ${GIT_EXECUTABLE} apply --index ${CMAKE_CURRENT_SOURCE_DIR}/patches/creator.patch)
FetchContent_Declare(sdk GIT_REPOSITORY https://github.com/Inochi2D/inochi2d.git GIT_TAG dda3a8f005f808104caa43183ab8753fb989e30f GIT_SUBMODULES "" PATCH_COMMAND ${GIT_EXECUTABLE} reset --hard HEAD COMMAND ${GIT_EXECUTABLE} apply --index ${CMAKE_CURRENT_SOURCE_DIR}/patches/sdk.patch)
FetchContent_Declare(bindings GIT_REPOSITORY https://github.com/Inochi2D/i2d-imgui.git GIT_TAG c6a78f4a7510fd31a86998b7ceedfc2916ecfae0 GIT_SUBMODULES "" SOURCE_SUBDIR source)
FetchContent_Declare(cimgui GIT_REPOSITORY https://github.com/Inochi2D/cimgui.git GIT_TAG bb241882da8294b648ac1f9be1aca0421eaa4191 GIT_SUBMODULES imgui SOURCE_SUBDIR source)
FetchContent_MakeAvailable(creator sdk bindings cimgui)
set(imgui_SOURCE_DIR "${cimgui_SOURCE_DIR}/imgui")

add_library(inochi-native SHARED
    source/compat.cpp ${cimgui_SOURCE_DIR}/cimgui.cpp
    ${imgui_SOURCE_DIR}/imgui.cpp ${imgui_SOURCE_DIR}/imgui_draw.cpp
    ${imgui_SOURCE_DIR}/imgui_demo.cpp ${imgui_SOURCE_DIR}/imgui_tables.cpp
    ${imgui_SOURCE_DIR}/imgui_widgets.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_sdl2.cpp
    ${imgui_SOURCE_DIR}/backends/imgui_impl_opengl3.cpp
    ${imgui_SOURCE_DIR}/misc/freetype/imgui_freetype.cpp)
target_compile_features(inochi-native PRIVATE cxx_std_17)
target_include_directories(inochi-native PRIVATE ${cimgui_SOURCE_DIR} ${imgui_SOURCE_DIR})
target_compile_definitions(inochi-native PRIVATE IMGUI_ENABLE_FREETYPE IMGUI_ENABLE_STB_TRUETYPE IMGUI_IMPL_BACKEND_SDL2 IMGUI_IMPL_BACKEND_OPENGL3 "IMGUI_IMPL_API=extern \"C\"")
if(NOT WIN32)
    target_compile_definitions(inochi-native PRIVATE __cdecl=)
endif()
target_link_libraries(inochi-native PRIVATE SDL2::SDL2 Freetype::Freetype OpenGL::GL "$<$<PLATFORM_ID:Windows>:imm32>")
set_target_properties(inochi-native PROPERTIES WINDOWS_EXPORT_ALL_SYMBOLS ON LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>" RUNTIME_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>")

# Dub links one native target; CMake owns its system-library dependencies.
if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
    set(platform_dependencies "\"mir-linux-kernel\": \"1.0.1\", \"dportals\": \"0.1.0\",")
endif()
configure_file(cmake/dub.json.in dub.in.json @ONLY)
file(GENERATE OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>/dub.json" INPUT "${CMAKE_CURRENT_BINARY_DIR}/dub.in.json")
file(GENERATE OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>/dub.selections.json" INPUT "${CMAKE_CURRENT_SOURCE_DIR}/dub.selections.json")
add_custom_target(inochi ALL COMMAND ${DUB} build --root=${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG> --compiler=${DC} --build=$<IF:$<CONFIG:Debug>,debug,release> DEPENDS inochi-native USES_TERMINAL VERBATIM)
install(TARGETS inochi-native RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR} LIBRARY DESTINATION ${CMAKE_INSTALL_BINDIR})
install(PROGRAMS "${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>/inochi${CMAKE_EXECUTABLE_SUFFIX}" DESTINATION ${CMAKE_INSTALL_BINDIR})
install(FILES LICENSE CONTRIBUTORS.md DESTINATION ${CMAKE_INSTALL_DATADIR}/inochi)
foreach(upstream IN ITEMS sdk bindings cimgui imgui)
    file(GLOB licenses "${${upstream}_SOURCE_DIR}/LICENSE*")
    install(FILES ${licenses} DESTINATION ${CMAKE_INSTALL_DATADIR}/inochi/licenses/${upstream})
endforeach()
include(CTest)
if(BUILD_TESTING)
    find_package(Python3 COMPONENTS Interpreter REQUIRED)
    add_custom_target(native-actions ALL COMMAND ${DUB} build --root=${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG> --compiler=${DC} --build=$<IF:$<CONFIG:Debug>,debug,release> --config=native-actions DEPENDS inochi USES_TERMINAL VERBATIM)
    add_test(NAME integration COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/tests/run.py ${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>/inochi${CMAKE_EXECUTABLE_SUFFIX} ${CMAKE_CURRENT_BINARY_DIR}/$<CONFIG>/inochi-native-actions${CMAKE_EXECUTABLE_SUFFIX})
endif()
set(CPACK_PACKAGE_CONTACT "Inochi CLI contributors")
set(CPACK_SOURCE_IGNORE_FILES "/[.]git/;/[.]dub/;/build/;/vendor/;/out/;/bin/;/dist/;/tests/results/;__pycache__")
include(CPack)
