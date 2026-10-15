#include "imgui.h"
#include "imgui_internal.h"
#include "cimgui.h"
#include <filesystem>

// The pinned D bindings use the earlier names for these native ImGui entry points.
CIMGUI_API bool igIsKeyPressed(ImGuiKey key, bool repeat) { return igIsKeyPressed_Bool(key, repeat); }
CIMGUI_API bool igIsKeyDown(ImGuiKey key) { return igIsKeyDown_Nil(key); }
CIMGUI_API bool igIsMouseClicked(ImGuiMouseButton button, bool repeat) { return igIsMouseClicked_Bool(button, repeat); }
CIMGUI_API bool igIsMouseReleased(ImGuiMouseButton button) { return igIsMouseReleased_Nil(button); }
CIMGUI_API bool igIsMouseDoubleClicked(ImGuiMouseButton button) { return igIsMouseDoubleClicked_Nil(button); }
CIMGUI_API bool igIsMouseDown(ImGuiMouseButton button) { return igIsMouseDown_Nil(button); }
CIMGUI_API bool igBeginChildFrame(ImGuiID id, const ImVec2 size, ImGuiWindowFlags flags) { return igBeginChild_ID(id, size, ImGuiChildFlags(0), flags); }
CIMGUI_API void igEndChildFrame() { igEndChild(); }
CIMGUI_API void igShowStackToolWindow(bool* open) { igShowMetricsWindow(open); }
CIMGUI_API void igRenderNavHighlight(const ImRect bb, ImGuiID id, int flags) { ImGui::RenderNavCursor(bb, id, ImGuiNavRenderCursorFlags(flags)); }
CIMGUI_API void igSetItemAllowOverlap() { ImGui::SetItemAllowOverlap(); }

CIMGUI_API ImDrawList* igGetForegroundDrawList_Nil() { return ImGui::GetForegroundDrawList(); }
CIMGUI_API ImDrawList* igGetBackgroundDrawList_Nil() { return ImGui::GetBackgroundDrawList(); }
CIMGUI_API ImDrawList* igGetBackgroundDrawList_ViewportPtr(ImGuiViewport* viewport) { return ImGui::GetBackgroundDrawList(viewport); }
CIMGUI_API float igImFloorSigned_Float(float value) { return ImFloor(value); }
CIMGUI_API void igImFloorSigned_Vec2(ImVec2* out, const ImVec2 value) { *out = ImFloor(value); }
CIMGUI_API bool igCombo_FnBoolPtr(const char* label, int* current, bool (*getter)(void*, int, const char**), void* data, int count, int height) { return ImGui::Combo(label, current, getter, data, count, height); }
CIMGUI_API bool igListBox_FnBoolPtr(const char* label, int* current, bool (*getter)(void*, int, const char**), void* data, int count, int height) { return ImGui::ListBox(label, current, getter, data, count, height); }

CIMGUI_API bool inochiSameFile(const char* first, const char* second) {
    std::error_code error;
    return std::filesystem::equivalent(std::filesystem::u8path(first), std::filesystem::u8path(second), error);
}
