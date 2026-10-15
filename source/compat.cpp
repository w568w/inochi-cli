#include "imgui.h"
#include "imgui_internal.h"
#include "cimgui.h"
#include <filesystem>

CIMGUI_API bool inochiSameFile(const char* first, const char* second) {
    std::error_code error;
    return std::filesystem::equivalent(std::filesystem::u8path(first), std::filesystem::u8path(second), error);
}
