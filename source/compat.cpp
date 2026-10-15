#include "imgui.h"
#include "imgui_internal.h"
#include "cimgui.h"
#include <filesystem>

// The pinned D bindings use the earlier names for these native ImGui entry points.
extern "C" {
bool igIsKeyPressed(ImGuiKey key, bool repeat) { return igIsKeyPressed_Bool(key, repeat); }
bool igIsKeyDown(ImGuiKey key) { return igIsKeyDown_Nil(key); }
bool igIsMouseClicked(ImGuiMouseButton button, bool repeat) { return igIsMouseClicked_Bool(button, repeat); }
bool igIsMouseReleased(ImGuiMouseButton button) { return igIsMouseReleased_Nil(button); }
bool igIsMouseDoubleClicked(ImGuiMouseButton button) { return igIsMouseDoubleClicked_Nil(button); }
bool igIsMouseDown(ImGuiMouseButton button) { return igIsMouseDown_Nil(button); }
bool igBeginChildFrame(ImGuiID id, const ImVec2 size, ImGuiWindowFlags flags) { return igBeginChild_ID(id, size, ImGuiChildFlags(0), flags); }
void igEndChildFrame() { igEndChild(); }
void igShowStackToolWindow(bool* open) { igShowMetricsWindow(open); }
void igRenderNavHighlight(const ImRect bb, ImGuiID id, int flags) { ImGui::RenderNavCursor(bb, id, ImGuiNavRenderCursorFlags(flags)); }
void igSetItemAllowOverlap() { ImGui::SetItemAllowOverlap(); }

bool inochiSameFile(const char* first, const char* second) {
    std::error_code error;
    return std::filesystem::equivalent(std::filesystem::u8path(first), std::filesystem::u8path(second), error);
}
}
