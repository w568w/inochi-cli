# Inochi Creator v0.8.6 UI coverage

Baseline: `371e5f4e21117102dbecc82371bfd9a6e2f5df02`. Source locations refer to the unmodified baseline.

492 GUI control call sites are inventoried. Command execution coverage and GUI behavior equivalence are separate gates. Command results: `tests/results/acceptance.json`; semantic assertions: `tests/results/semantics/results.json`. Run `ctest --test-dir build --output-on-failure` to refresh the execution evidence.

UI selection, cursor gestures and clipboard state map to explicit node/vertex/key arguments or command sequences. Shared widget implementations and application/device controls are identified separately.

| Baseline source | Function/control | CLI equivalent | Verification |
|---|---|---|---|
| source/creator/panels/actionhistory.d:38 | onUpdate: if (igSelectable(action.describeUndo().toStringz, i <= cast(ptrdiff_t)incActionIndex())) { | history seek | semantic assertion passed |
| source/creator/panels/actionhistory.d:43 | onUpdate: if (igSelectable(action.describe().toStringz, i+1 <= incActionIndex())) { | history seek | semantic assertion passed |
| source/creator/panels/actionhistory.d:56 | onUpdate: if (igButton(__("Clear History"), ImVec2(0, 0))) { | history clear | semantic assertion passed |
| source/creator/panels/animlist.d:34 | onUpdate: if (igMenuItem(__("Duplicate"))) { | animation duplicate | semantic assertion passed |
| source/creator/panels/animlist.d:49 | onUpdate: if (igMenuItem(__("Edit..."))) { | animation set | semantic assertion passed |
| source/creator/panels/animlist.d:52 | onUpdate: if (igMenuItem(__("Delete"))) { | animation delete | semantic assertion passed |
| source/creator/panels/animlist.d:62 | onUpdate: if (igSelectable(name.toStringz, name == currAnimName)) { | render image | semantic assertion passed |
| source/creator/panels/animlist.d:79 | onUpdate: if (igButton("", ImVec2(24, 24))) { | animation add | semantic assertion passed |
| source/creator/panels/inspector.d:203 | incInspectorModelInfo: incInputText("META_NAME", puppet.meta.name); | project meta | semantic assertion passed |
| source/creator/panels/inspector.d:210 | incInspectorModelInfo: incInputText("META_ARTISTS", puppet.meta.artist); | project meta | semantic assertion passed |
| source/creator/panels/inspector.d:217 | incInspectorModelInfo: incInputText("META_RIGGERS", puppet.meta.rigger); | project meta | semantic assertion passed |
| source/creator/panels/inspector.d:224 | incInspectorModelInfo: incInputText("META_CONTACT", puppet.meta.contact); | project meta | semantic assertion passed |
| source/creator/panels/inspector.d:233 | incInspectorModelInfo: incInputText("META_LICENSEURL", puppet.meta.licenseURL); | project meta | semantic assertion passed |
| source/creator/panels/inspector.d:240 | incInspectorModelInfo: incInputText("META_COPYRIGHT", puppet.meta.copyright); | project meta | semantic assertion passed |
| source/creator/panels/inspector.d:247 | incInspectorModelInfo: incInputText("META_ORIGIN", puppet.meta.reference); | project meta | semantic assertion passed |
| source/creator/panels/inspector.d:256 | incInspectorModelInfo: incDragFloat("PixelsPerMeter", &puppet.physics.pixelsPerMeter, 1, 1, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:263 | incInspectorModelInfo: incDragFloat("Gravity", &puppet.physics.gravity, 0.01, 0, float.max, _("%.2f m/s²"), ImGuiSliderFlags.NoRoundToFormat); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:270 | incInspectorModelInfo: if (igCheckbox(__("Use Point Filtering"), &incActivePuppet().meta.preservePixels)) { | project meta | semantic assertion passed |
| source/creator/panels/inspector.d:285 | incModelModeHeader: if (incInputText("###MODEL_NODE_HEADER", incAvailableSpace().x-24, node.name)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:319 | incInspectorModelTRS: if (incDragFloat("translation_x", &node.localTransform.translation.vector[0], adjustSpeed, -float.max, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:336 | incInspectorModelTRS: if (incDragFloat("translation_y", &node.localTransform.translation.vector[1], adjustSpeed, -float.max, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:353 | incInspectorModelTRS: if (incDragFloat("translation_z", &node.localTransform.translation.vector[2], adjustSpeed, -float.max, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:381 | incInspectorModelTRS: if (incLockButton(&lockToRoot, "root_lk")) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:411 | incInspectorModelTRS: if (incDragFloat("rotation_x", &rotationDegrees, adjustSpeed/100, -float.max, float.max, "%.2f°", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:431 | incInspectorModelTRS: if (incDragFloat("rotation_y", &rotationDegrees, adjustSpeed/100, -float.max, float.max, "%.2f°", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:451 | incInspectorModelTRS: if (incDragFloat("rotation_z", &rotationDegrees, adjustSpeed/100, -float.max, float.max, "%.2f°", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:481 | incInspectorModelTRS: if (incDragFloat("scale_x", &node.localTransform.scale.vector[0], adjustSpeed/100, -float.max, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:498 | incInspectorModelTRS: if (incDragFloat("scale_y", &node.localTransform.scale.vector[1], adjustSpeed/100, -float.max, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:521 | incInspectorModelTRS: if (incLockButton(&node.localTransform.pixelSnap, "pix_lk")) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:544 | incInspectorModelTRS: if (igInputFloat("###ZSort", &zsortV, 0.01, 0.05, "%0.2f")) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:573 | incInspectorModelDrawable: if (incDragFloat("offset_x", &node.getMesh().origin.vector[0], adjustSpeed, -float.max, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:590 | incInspectorModelDrawable: if (incDragFloat("offset_y", &node.getMesh().origin.vector[1], adjustSpeed, -float.max, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:682 | applyTextureToSlot: if (igMenuItem(__("Save to File"))) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:696 | applyTextureToSlot: if (igMenuItem(__("Load from File"))) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:710 | applyTextureToSlot: if (igMenuItem(__("Remove"))) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:719 | applyTextureToSlot: if (igMenuItem(__("Make Emissive"))) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:787 | incInspectorModelPart: igColorEdit3("###TINT", cast(float[3]*)node.tint.ptr); | node set | semantic assertion passed |
| source/creator/panels/inspector.d:790 | incInspectorModelPart: igColorEdit3("###S_TINT", cast(float[3]*)node.screenTint.ptr); | node set | semantic assertion passed |
| source/creator/panels/inspector.d:794 | incInspectorModelPart: if (igDragFloat("###S_EMISSION", &strengthPerc, 0.1, 0, float.max, "%.0f%%")) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:809 | incInspectorModelPart: if (igSelectable(__("Normal"), node.blendingMode == BlendMode.Normal)) node.blendingMode = BlendMode.Normal; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:813 | incInspectorModelPart: if (igSelectable(__("Multiply"), node.blendingMode == BlendMode.Multiply)) node.blendingMode = BlendMode.Multiply; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:816 | incInspectorModelPart: if (igSelectable(__("Screen"), node.blendingMode == BlendMode.Screen)) node.blendingMode = BlendMode.Screen; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:819 | incInspectorModelPart: if (igSelectable(__("Overlay"), node.blendingMode == BlendMode.Overlay)) node.blendingMode = BlendMode.Overlay; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:822 | incInspectorModelPart: if (igSelectable(__("Darken"), node.blendingMode == BlendMode.Darken)) node.blendingMode = BlendMode.Darken; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:825 | incInspectorModelPart: if (igSelectable(__("Lighten"), node.blendingMode == BlendMode.Lighten)) node.blendingMode = BlendMode.Lighten; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:828 | incInspectorModelPart: if (igSelectable(__("Color Dodge"), node.blendingMode == BlendMode.ColorDodge)) node.blendingMode = BlendMode.ColorDodge; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:831 | incInspectorModelPart: if (igSelectable(__("Linear Dodge"), node.blendingMode == BlendMode.LinearDodge)) node.blendingMode = BlendMode.LinearDodge; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:834 | incInspectorModelPart: if (igSelectable(__("Add (Glow)"), node.blendingMode == BlendMode.AddGlow)) node.blendingMode = BlendMode.AddGlow; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:837 | incInspectorModelPart: if (igSelectable(__("Color Burn"), node.blendingMode == BlendMode.ColorBurn)) node.blendingMode = BlendMode.ColorBurn; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:840 | incInspectorModelPart: if (igSelectable(__("Hard Light"), node.blendingMode == BlendMode.HardLight)) node.blendingMode = BlendMode.HardLight; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:843 | incInspectorModelPart: if (igSelectable(__("Soft Light"), node.blendingMode == BlendMode.SoftLight)) node.blendingMode = BlendMode.SoftLight; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:846 | incInspectorModelPart: if (igSelectable(__("Subtract"), node.blendingMode == BlendMode.Subtract)) node.blendingMode = BlendMode.Subtract; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:849 | incInspectorModelPart: if (igSelectable(__("Difference"), node.blendingMode == BlendMode.Difference)) node.blendingMode = BlendMode.Difference; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:852 | incInspectorModelPart: if (igSelectable(__("Exclusion"), node.blendingMode == BlendMode.Exclusion)) node.blendingMode = BlendMode.Exclusion; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:855 | incInspectorModelPart: if (igSelectable(__("Inverse"), node.blendingMode == BlendMode.Inverse)) node.blendingMode = BlendMode.Inverse; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:859 | incInspectorModelPart: if (igSelectable(__("Destination In"), node.blendingMode == BlendMode.DestinationIn)) node.blendingMode = BlendMode.DestinationIn; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:862 | incInspectorModelPart: if (igSelectable(__("Clip to Lower"), node.blendingMode == BlendMode.ClipToLower)) node.blendingMode = BlendMode.ClipToLower; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:866 | incInspectorModelPart: if (igSelectable(__("Slice from Lower"), node.blendingMode == BlendMode.SliceFromLower)) node.blendingMode = BlendMode.SliceFromLower; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:875 | incInspectorModelPart: igSliderFloat("###Opacity", &node.opacity, 0, 1f, "%0.2f"); | node set | semantic assertion passed |
| source/creator/panels/inspector.d:885 | incInspectorModelPart: igSliderFloat("###Threshold", &node.maskAlphaThreshold, 0.0, 1.0, "%.2f"); | node set | semantic assertion passed |
| source/creator/panels/inspector.d:903 | incInspectorModelPart: if (igMenuItem(__("Mask"), null, masker.mode == MaskingMode.Mask)) masker.mode = MaskingMode.Mask; | mask set | semantic assertion passed |
| source/creator/panels/inspector.d:904 | incInspectorModelPart: if (igMenuItem(__("Dodge"), null, masker.mode == MaskingMode.DodgeMask)) masker.mode = MaskingMode.DodgeMask; | mask set | semantic assertion passed |
| source/creator/panels/inspector.d:909 | incInspectorModelPart: if (igMenuItem(__("Delete"))) { | mask remove | semantic assertion passed |
| source/creator/panels/inspector.d:921 | incInspectorModelPart: if (masker.mode == MaskingMode.Mask) igSelectable(_("%s (Mask)").format(masker.maskSrc.name).toStringz); | mask set | semantic assertion passed |
| source/creator/panels/inspector.d:922 | incInspectorModelPart: else igSelectable(_("%s (Dodge)").format(masker.maskSrc.name).toStringz); | mask set | semantic assertion passed |
| source/creator/panels/inspector.d:987 | incInspectorModelCamera: igDragFloat2("###VIEWPORT", &node.getViewport().vector, 2); | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1010 | incInspectorModelComposite: igColorEdit3("###TINT", cast(float[3]*)node.tint.ptr); | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1013 | incInspectorModelComposite: igColorEdit3("###S_TINT", cast(float[3]*)node.screenTint.ptr); | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1021 | incInspectorModelComposite: if (igSelectable(__("Normal"), node.blendingMode == BlendMode.Normal)) node.blendingMode = BlendMode.Normal; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1025 | incInspectorModelComposite: if (igSelectable(__("Multiply"), node.blendingMode == BlendMode.Multiply)) node.blendingMode = BlendMode.Multiply; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1028 | incInspectorModelComposite: if (igSelectable(__("Screen"), node.blendingMode == BlendMode.Screen)) node.blendingMode = BlendMode.Screen; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1031 | incInspectorModelComposite: if (igSelectable(__("Overlay"), node.blendingMode == BlendMode.Overlay)) node.blendingMode = BlendMode.Overlay; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1034 | incInspectorModelComposite: if (igSelectable(__("Darken"), node.blendingMode == BlendMode.Darken)) node.blendingMode = BlendMode.Darken; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1037 | incInspectorModelComposite: if (igSelectable(__("Lighten"), node.blendingMode == BlendMode.Lighten)) node.blendingMode = BlendMode.Lighten; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1040 | incInspectorModelComposite: if (igSelectable(__("Color Dodge"), node.blendingMode == BlendMode.ColorDodge)) node.blendingMode = BlendMode.ColorDodge; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1043 | incInspectorModelComposite: if (igSelectable(__("Linear Dodge"), node.blendingMode == BlendMode.LinearDodge)) node.blendingMode = BlendMode.LinearDodge; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1046 | incInspectorModelComposite: if (igSelectable(__("Add (Glow)"), node.blendingMode == BlendMode.AddGlow)) node.blendingMode = BlendMode.AddGlow; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1049 | incInspectorModelComposite: if (igSelectable(__("Color Burn"), node.blendingMode == BlendMode.ColorBurn)) node.blendingMode = BlendMode.ColorBurn; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1052 | incInspectorModelComposite: if (igSelectable(__("Hard Light"), node.blendingMode == BlendMode.HardLight)) node.blendingMode = BlendMode.HardLight; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1055 | incInspectorModelComposite: if (igSelectable(__("Soft Light"), node.blendingMode == BlendMode.SoftLight)) node.blendingMode = BlendMode.SoftLight; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1058 | incInspectorModelComposite: if (igSelectable(__("Subtract"), node.blendingMode == BlendMode.Subtract)) node.blendingMode = BlendMode.Subtract; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1061 | incInspectorModelComposite: if (igSelectable(__("Difference"), node.blendingMode == BlendMode.Difference)) node.blendingMode = BlendMode.Difference; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1064 | incInspectorModelComposite: if (igSelectable(__("Exclusion"), node.blendingMode == BlendMode.Exclusion)) node.blendingMode = BlendMode.Exclusion; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1067 | incInspectorModelComposite: if (igSelectable(__("Inverse"), node.blendingMode == BlendMode.Inverse)) node.blendingMode = BlendMode.Inverse; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1071 | incInspectorModelComposite: if (igSelectable(__("Destination In"), node.blendingMode == BlendMode.DestinationIn)) node.blendingMode = BlendMode.DestinationIn; | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1079 | incInspectorModelComposite: igSliderFloat("###Opacity", &node.opacity, 0, 1f, "%0.2f"); | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1089 | incInspectorModelComposite: igSliderFloat("###Threshold", &node.threshold, 0.0, 1.0, "%.2f"); | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1107 | incInspectorModelComposite: if (igMenuItem(__("Mask"), null, masker.mode == MaskingMode.Mask)) masker.mode = MaskingMode.Mask; | mask set | semantic assertion passed |
| source/creator/panels/inspector.d:1108 | incInspectorModelComposite: if (igMenuItem(__("Dodge"), null, masker.mode == MaskingMode.DodgeMask)) masker.mode = MaskingMode.DodgeMask; | mask set | semantic assertion passed |
| source/creator/panels/inspector.d:1113 | incInspectorModelComposite: if (igMenuItem(__("Delete"))) { | mask remove | semantic assertion passed |
| source/creator/panels/inspector.d:1126 | incInspectorModelComposite: if (masker.mode == MaskingMode.Mask) igSelectable(_("%s (Mask)").format(masker.maskSrc.name).toStringz); | mask set | semantic assertion passed |
| source/creator/panels/inspector.d:1127 | incInspectorModelComposite: else igSelectable(_("%s (Dodge)").format(masker.maskSrc.name).toStringz); | mask set | semantic assertion passed |
| source/creator/panels/inspector.d:1180 | incInspectorModelComposite: if (igCheckbox(__("Propagate MeshGroup"), &propagateMeshGroup)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1208 | incInspectorModelSimplePhysics: if (igMenuItem(__("Unmap"))) { | physics unmap | semantic assertion passed |
| source/creator/panels/inspector.d:1222 | incInspectorModelSimplePhysics: igInputText("###TARGET_PARAM", cast(char*)paramName.toStringz, paramName.length, ImGuiInputTextFlags.ReadOnly); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1241 | incInspectorModelSimplePhysics: if (igSelectable(__("Pendulum"), node.modelType == PhysicsModel.Pendulum)) node.modelType = PhysicsModel.Pendulum; | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1243 | incInspectorModelSimplePhysics: if (igSelectable(__("SpringPendulum"), node.modelType == PhysicsModel.SpringPendulum)) node.modelType = PhysicsModel.SpringPendulum; | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1253 | incInspectorModelSimplePhysics: if (igSelectable(__("AngleLength"), node.mapMode == ParamMapMode.AngleLength)) node.mapMode = ParamMapMode.AngleLength; | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1255 | incInspectorModelSimplePhysics: if (igSelectable(__("XY"), node.mapMode == ParamMapMode.XY)) node.mapMode = ParamMapMode.XY; | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1257 | incInspectorModelSimplePhysics: if (igSelectable(__("LengthAngle"), node.mapMode == ParamMapMode.LengthAngle)) node.mapMode = ParamMapMode.LengthAngle; | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1259 | incInspectorModelSimplePhysics: if (igSelectable(__("YX"), node.mapMode == ParamMapMode.YX)) node.mapMode = ParamMapMode.YX; | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1269 | incInspectorModelSimplePhysics: igCheckbox(__("Local Transform Lock"), &node.localOnly); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1277 | incInspectorModelSimplePhysics: incDragFloat("gravity", &node.gravity, adjustSpeed/100, -float.max, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1284 | incInspectorModelSimplePhysics: incDragFloat("length", &node.length, adjustSpeed/100, 0, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1291 | incInspectorModelSimplePhysics: incDragFloat("frequency", &node.frequency, adjustSpeed/100, 0.01, 30, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1298 | incInspectorModelSimplePhysics: incDragFloat("damping_angle", &node.angleDamping, adjustSpeed/100, 0, 5, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1302 | incInspectorModelSimplePhysics: incDragFloat("damping_length", &node.lengthDamping, adjustSpeed/100, 0, 5, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1309 | incInspectorModelSimplePhysics: incDragFloat("output_scale.x", &node.outputScale.vector[0], adjustSpeed/100, 0, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1313 | incInspectorModelSimplePhysics: incDragFloat("output_scale.y", &node.outputScale.vector[1], adjustSpeed/100, 0, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | physics set | semantic assertion passed |
| source/creator/panels/inspector.d:1335 | incInspectorModelMeshGroup: if (igCheckbox(__("Dynamic Deformation (slower)"), &dynamic)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1341 | incInspectorModelMeshGroup: if (igCheckbox(__("Translate origins"), &translateChildren)) { | node set | semantic assertion passed |
| source/creator/panels/inspector.d:1364 | incInspectorDeformFloatDragVal: if (incDragFloat(name, &currFloat, adjustSpeed, -float.max, float.max, rotation ? "%.2f°" : "%.2f", ImGuiSliderFlags.NoRoundToFormat)) { | key set | semantic assertion passed |
| source/creator/panels/inspector.d:1404 | incInspectorDeformInputFloat: if (igInputFloat(name.toStringz, &currFloat, step, stepFast, "%.2f")) { | key set | semantic assertion passed |
| source/creator/panels/inspector.d:1450 | incInspectorDeformColorEdit3: if (igColorEdit3("###COLORADJ", &rgbadj)) { | key set | semantic assertion passed |
| source/creator/panels/inspector.d:1483 | incInspectorDeformSliderFloat: if (igSliderFloat(name.toStringz, &currFloat, min, max, "%.2f")) { | key set | semantic assertion passed |
| source/creator/panels/inspector.d:1507 | incInspectorDeformDragFloat: if (igDragFloat(name.toStringz, &value, speed, min, max, fmt)) { | key set | semantic assertion passed |
| source/creator/panels/inspector.d:1677 | incInspectorDeformPart: if (igDragFloat("###S_EMISSION", &strengthPerc, 0.1, 0, float.max, "%.0f%%")) { | key set | semantic assertion passed |
| source/creator/panels/nodes.d:148 | nodeActionsPopup: if (igMenuItem(__("Node"), "", false, true)) incAddChildWithHistory(new Node(cast(Node)null), n); | node add | semantic assertion passed |
| source/creator/panels/nodes.d:152 | nodeActionsPopup: if (igMenuItem(__("Mask"), "", false, true)) { | node add | semantic assertion passed |
| source/creator/panels/nodes.d:159 | nodeActionsPopup: if (igMenuItem(__("Composite"), "", false, true)) { | node add | semantic assertion passed |
| source/creator/panels/nodes.d:165 | nodeActionsPopup: if (igMenuItem(__("Simple Physics"), "", false, true)) incAddChildWithHistory(new SimplePhysics(cast(Node)null), n); | node add | semantic assertion passed |
| source/creator/panels/nodes.d:170 | nodeActionsPopup: if (igMenuItem(__("Camera"), "", false, true)) incAddChildWithHistory(new ExCamera(cast(Node)null), n); | node add | semantic assertion passed |
| source/creator/panels/nodes.d:174 | nodeActionsPopup: if (igMenuItem(__("MeshGroup"), "", false, true)) incAddChildWithHistory(new MeshGroup(cast(Node)null), n); | node add | semantic assertion passed |
| source/creator/panels/nodes.d:184 | nodeActionsPopup: if (igMenuItem(__("Edit Mesh"))) { | mesh get | semantic assertion passed |
| source/creator/panels/nodes.d:190 | nodeActionsPopup: if (igMenuItem(n.enabled ? /* Option to hide the node (and subnodes) */ __("Hide") :  /* Option to show the node (and subnodes) */ __("Show"))) { | node set | semantic assertion passed |
| source/creator/panels/nodes.d:194 | nodeActionsPopup: if (igMenuItem(__("Delete"), "", false, !isRoot)) { | node delete | semantic assertion passed |
| source/creator/panels/nodes.d:238 | nodeActionsPopup: if (igMenuItem(__("Recalculate origin"), "", false, true)) { | node origin | semantic assertion passed |
| source/creator/panels/nodes.d:360 | treeAddNode: if (igSelectable(isRoot ? __("Puppet") : n.name.toStringz, selected, ImGuiSelectableFlags.None, ImVec2(0, 0))) { | node get | semantic assertion passed |
| source/creator/panels/nodes.d:529 | onUpdate: if (incInputText("Node Filter", filter)) { | node list | semantic assertion passed |
| source/creator/panels/nodes.d:578 | onUpdate: if (igButton("", ImVec2(24, 24))) { | node delete | semantic assertion passed |
| source/creator/panels/parameters.d:276 | keypointActions: if (igMenuItem(__("Unset"), "", false, true)) { | key unset | semantic assertion passed |
| source/creator/panels/parameters.d:285 | keypointActions: if (igMenuItem(__("Set to current"), "", false, true)) { | key current | semantic assertion passed |
| source/creator/panels/parameters.d:294 | keypointActions: if (igMenuItem(__("Reset"), "", false, true)) { | key reset | semantic assertion passed |
| source/creator/panels/parameters.d:303 | keypointActions: if (igMenuItem(__("Invert"), "", false, true)) { | key invert | semantic assertion passed |
| source/creator/panels/parameters.d:313 | keypointActions: if (igMenuItem(__("Horizontally"), "", false, true)) { | key mirror | semantic assertion passed |
| source/creator/panels/parameters.d:322 | keypointActions: if (igMenuItem(__("Vertically"), "", false, true)) { | key mirror | semantic assertion passed |
| source/creator/panels/parameters.d:333 | keypointActions: if (igMenuItem(__("Flip Deform"), "", false, true)) { | key flip-deform | semantic assertion passed |
| source/creator/panels/parameters.d:356 | keypointActions: if (igMenuItem(__("Horizontally"), "", false, true)) { | key mirror | semantic assertion passed |
| source/creator/panels/parameters.d:373 | keypointActions: if (igMenuItem(__("Vertically"), "", false, true)) { | key mirror | semantic assertion passed |
| source/creator/panels/parameters.d:390 | keypointActions: if (igMenuItem(__("Diagonally"), "", false, true)) { | key mirror | semantic assertion passed |
| source/creator/panels/parameters.d:410 | keypointActions: if (igMenuItem(__("Set from mirror"), "", false, true)) { | key from-mirror | semantic assertion passed |
| source/creator/panels/parameters.d:429 | keypointActions: if (igMenuItem(__("Copy"), "", false, true)) { | key copy | semantic assertion passed |
| source/creator/panels/parameters.d:437 | keypointActions: if (igMenuItem(__("Paste"), "", false,  true)) { | key copy | semantic assertion passed |
| source/creator/panels/parameters.d:534 | bindingList: if (igMenuItem(__("Remove"), "", false, true)) { | binding remove | semantic assertion passed |
| source/creator/panels/parameters.d:547 | bindingList: if (igMenuItem(__("Nearest"), "", false, true)) { | binding set | semantic assertion passed |
| source/creator/panels/parameters.d:553 | bindingList: if (igMenuItem(__("Linear"), "", false, true)) { | binding set | semantic assertion passed |
| source/creator/panels/parameters.d:559 | bindingList: if (igMenuItem(__("Cubic"), "", false, true)) { | binding set | semantic assertion passed |
| source/creator/panels/parameters.d:571 | bindingList: if (igMenuItem(cNode.name.toStringz, "", false, true)) { | param set | semantic assertion passed |
| source/creator/panels/parameters.d:579 | bindingList: if (igMenuItem(cNode.name.toStringz, "", false, true)) { | param set | semantic assertion passed |
| source/creator/panels/parameters.d:865 | incParameterView: if (igMenuItem(__("Edit Properties"), "", false, true)) { | param set | semantic assertion passed |
| source/creator/panels/parameters.d:869 | incParameterView: if (igMenuItem(__("Edit Axes Points"), "", false, true)) { | param axis-add | semantic assertion passed |
| source/creator/panels/parameters.d:873 | incParameterView: if (igMenuItem(__("Split"), "", false, true)) { | param split | semantic assertion passed |
| source/creator/panels/parameters.d:877 | incParameterView: if (!param.isVec2 && igMenuItem(__("To 2D"), "", false, true)) { | param to-2d | semantic assertion passed |
| source/creator/panels/parameters.d:882 | incParameterView: if (igMenuItem(__("Flip X"), "", false, true)) { | param flip | semantic assertion passed |
| source/creator/panels/parameters.d:888 | incParameterView: if (igMenuItem(__("Flip Y"), "", false, true)) { | param flip | semantic assertion passed |
| source/creator/panels/parameters.d:895 | incParameterView: if (igMenuItem(__("Flip"), "", false, true)) { | param flip | semantic assertion passed |
| source/creator/panels/parameters.d:903 | incParameterView: if (igMenuItem(__("Horizontally"), "", false, true)) { | param set | semantic assertion passed |
| source/creator/panels/parameters.d:907 | incParameterView: if (igMenuItem(__("Vertically"), "", false, true)) { | param set | semantic assertion passed |
| source/creator/panels/parameters.d:914 | incParameterView: if (igMenuItem("", "", false, true)) { | param autofill | semantic assertion passed |
| source/creator/panels/parameters.d:918 | incParameterView: if (igMenuItem("", "", false, true)) { | param autofill | semantic assertion passed |
| source/creator/panels/parameters.d:923 | incParameterView: if (igMenuItem("", "", false, true)) { | param autofill | semantic assertion passed |
| source/creator/panels/parameters.d:927 | incParameterView: if (igMenuItem("", "", false, true)) { | param autofill | semantic assertion passed |
| source/creator/panels/parameters.d:938 | incParameterView: if (igMenuItem(__("Copy"), "", false, true)) { | param paste | semantic assertion passed |
| source/creator/panels/parameters.d:941 | incParameterView: if (igMenuItem(__("Paste"), "", false, true)) { | param paste | semantic assertion passed |
| source/creator/panels/parameters.d:945 | incParameterView: if (igMenuItem(__("Paste and Horizontal Flip"), "", false, true)) { | param flip | semantic assertion passed |
| source/creator/panels/parameters.d:950 | incParameterView: if (igMenuItem(__("Duplicate"), "", false, true)) { | param duplicate | semantic assertion passed |
| source/creator/panels/parameters.d:959 | incParameterView: if (igMenuItem(__("Delete"), "", false, true)) { | param delete | semantic assertion passed |
| source/creator/panels/parameters.d:971 | incParameterView: if (igMenuItem(__("Set Starting Position"), "", false, true)) { | param set | semantic assertion passed |
| source/creator/panels/parameters.d:980 | incParameterView: if (igButton("", ImVec2(24, 24))) { | cli-lifecycle | Opens the parameter action menu; each action is inventoried separately. |
| source/creator/panels/parameters.d:986 | incParameterView: if (incButtonColored(isArmed ? "" : "", ImVec2(24, 24), isArmed ? ImVec4(1f, 0f, 0f, 1f) : *igGetStyleColorVec4(ImGuiCol.Text))) { | cli-lifecycle | Parameter arming selects the parameter and exact key used by --param/--at; no persistent arming state is needed in a single command. |
| source/creator/panels/parameters.d:1004 | incParameterView: if (igButton("", ImVec2(24, 24))) { | param set | semantic assertion passed |
| source/creator/panels/parameters.d:1047 | onUpdate: if (igMenuItem(__("Add 1D Parameter (0..1)"), "", false, true)) { | param add | semantic assertion passed |
| source/creator/panels/parameters.d:1055 | onUpdate: if (igMenuItem(__("Add 1D Parameter (-1..1)"), "", false, true)) { | param add | semantic assertion passed |
| source/creator/panels/parameters.d:1066 | onUpdate: if (igMenuItem(__("Add 2D Parameter (0..1)"), "", false, true)) { | param add | semantic assertion passed |
| source/creator/panels/parameters.d:1074 | onUpdate: if (igMenuItem(__("Add 2D Parameter (-1..+1)"), "", false, true)) { | param add | semantic assertion passed |
| source/creator/panels/parameters.d:1086 | onUpdate: if (igMenuItem(__("Add Mouth Shape"), "", false, true)) { | param mouth-shape | semantic assertion passed |
| source/creator/panels/parameters.d:1105 | onUpdate: if (incInputText("Filter", filter)) { | param list | semantic assertion passed |
| source/creator/panels/parameters.d:1159 | displayParameters: if (igMenuItem(__("Rename"))) { | param group-set | semantic assertion passed |
| source/creator/panels/parameters.d:1168 | displayParameters: if (igColorButton("NONE", ImVec4(0, 0, 0, 0), flags \| ImGuiColorEditFlags.AlphaPreview, swatchSize)) group.color = vec3(float.nan, float.nan, float.nan); | param group-set | semantic assertion passed |
| source/creator/panels/parameters.d:1170 | displayParameters: if (igColorButton("RED", ImVec4(1, 0, 0, 1), flags, swatchSize)) group.color = vec3(0.25, 0.15, 0.15); | param group-set | semantic assertion passed |
| source/creator/panels/parameters.d:1172 | displayParameters: if (igColorButton("GREEN", ImVec4(0, 1, 0, 1), flags, swatchSize)) group.color = vec3(0.15, 0.25, 0.15); | param group-set | semantic assertion passed |
| source/creator/panels/parameters.d:1174 | displayParameters: if (igColorButton("BLUE", ImVec4(0, 0, 1, 1), flags, swatchSize)) group.color = vec3(0.15, 0.15, 0.25); | param group-set | semantic assertion passed |
| source/creator/panels/parameters.d:1176 | displayParameters: if (igColorButton("PURPLE", ImVec4(1, 0, 1, 1), flags, swatchSize)) group.color = vec3(0.25, 0.15, 0.25); | param group-set | semantic assertion passed |
| source/creator/panels/parameters.d:1178 | displayParameters: if (igColorButton("CYAN", ImVec4(0, 1, 1, 1), flags, swatchSize)) group.color = vec3(0.15, 0.25, 0.25); | param group-set | semantic assertion passed |
| source/creator/panels/parameters.d:1180 | displayParameters: if (igColorButton("YELLOW", ImVec4(1, 1, 0, 1), flags, swatchSize)) group.color = vec3(0.25, 0.25, 0.15); | param group-set | semantic assertion passed |
| source/creator/panels/parameters.d:1182 | displayParameters: if (igColorButton("WHITE", ImVec4(1, 1, 1, 1), flags, swatchSize)) group.color = vec3(0.25, 0.25, 0.25); | param group-set | semantic assertion passed |
| source/creator/panels/parameters.d:1188 | displayParameters: igColorPicker3(__("Custom Color"), &group.color.vector, ImGuiColorEditFlags.InputRGB \| ImGuiColorEditFlags.DisplayHSV); | param set | semantic assertion passed |
| source/creator/panels/parameters.d:1192 | displayParameters: if (igMenuItem(__("Delete"))) { | param group-delete | semantic assertion passed |
| source/creator/panels/parameters.d:1261 | displayParameters: if (igButton("", ImVec2(32, 32))) { | param set | semantic assertion passed |
| source/creator/panels/scene.d:28 | onUpdate: igColorEdit3( | scene set | semantic assertion passed |
| source/creator/panels/timeline.d:74 | drawHeaders: if (igMenuItem(__("Nearest"), null, lane.interpolation == InterpolateMode.Nearest)) { | animation lane-set | semantic assertion passed |
| source/creator/panels/timeline.d:77 | drawHeaders: if (igMenuItem(__("Stepped"), null, lane.interpolation == InterpolateMode.Stepped)) { | render image | semantic assertion passed |
| source/creator/panels/timeline.d:80 | drawHeaders: if (igMenuItem(__("Linear"), null, lane.interpolation == InterpolateMode.Linear)) { | render image | semantic assertion passed |
| source/creator/panels/timeline.d:83 | drawHeaders: if (igMenuItem(__("Cubic"), null, lane.interpolation == InterpolateMode.Cubic)) { | render image | semantic assertion passed |
| source/creator/panels/timeline.d:93 | drawHeaders: if (igMenuItem(__("Additive"), null, lane.mergeMode == ParamMergeMode.Additive)) { | disabled | The v0.8.6 source wraps these merge mode entries in igBeginDisabled(true) because playback merging is marked broken. |
| source/creator/panels/timeline.d:96 | drawHeaders: if (igMenuItem(__("Multiplicative"), null, lane.mergeMode == ParamMergeMode.Multiplicative)) { | disabled | The v0.8.6 source wraps these merge mode entries in igBeginDisabled(true) because playback merging is marked broken. |
| source/creator/panels/timeline.d:101 | drawHeaders: if (igMenuItem(__("Forced"), null, lane.mergeMode == ParamMergeMode.Forced)) { | animation lane-set | semantic assertion passed |
| source/creator/panels/timeline.d:107 | drawHeaders: if (igMenuItem(__("Delete"))) { | animation lane-remove | semantic assertion passed |
| source/creator/panels/timeline.d:208 | onUpdate: if (incToolbarButton(player.snapToFramerate ? "" : "", 32)) { | render image | semantic assertion passed |
| source/creator/panels/timeline.d:213 | onUpdate: if (incToolbarButton("", 32)) { | render image | semantic assertion passed |
| source/creator/panels/timeline.d:217 | onUpdate: if (incToolbarButton(anim && !(!anim.playing \|\| anim.paused) ? "" : "", 32)) { | render image | semantic assertion passed |
| source/creator/panels/tracking.d:34 | trackingModeCheckbox: if (igCheckbox(recvName, &track)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/panels/tracking.d:64 | onUpdate: if (incInputText(_("Bind Address"), avail.x/2, bindingIP, ImGuiInputTextFlags.None)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/panels/tracking.d:76 | onUpdate: if (igInputInt(__("Port"), &bindingPort)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/panels/tracking.d:91 | onUpdate: if (incInputText("iPhoneIP", _("iPhone IP"), avail.x/2, bindingIP, ImGuiInputTextFlags.None)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/panels/tracking.d:105 | onUpdate: if (incInputText("osfBindAddress", _("OSF Bind Address"), avail.x/2, bindingIP, ImGuiInputTextFlags.None)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/panels/tracking.d:116 | onUpdate: if (igInputInt(__("OSF Listen Port"), &bindingPort)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/panels/tracking.d:134 | onUpdate: if (igSelectable(nm)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/panels/tracking.d:143 | onUpdate: if (igButton("", ImVec2(0, 32))) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/panels/viewport.d:276 | onUpdate: if (igSliderFloat( | render image | semantic assertion passed |
| source/creator/panels/viewport.d:289 | onUpdate: if (igButton("", ImVec2(0, 0))) { | render image | semantic assertion passed |
| source/creator/panels/viewport.d:301 | onUpdate: if (igButton("##2", ImVec2(0, 0))) { | render image | semantic assertion passed |
| source/creator/viewport/common/automesh/contours.d:186 | : if (igSelectable(__("Normal parts"))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:194 | : if (igSelectable(__("Detailed mesh"))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:202 | : if (igSelectable(__("Large parts"))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:210 | : if (igSelectable(__("Small parts"))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:219 | : if (igSelectable(__("Thin and minimum parts"))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:228 | : if (igSelectable(__("Preserve edges"))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:249 | : if (incDragFloat( | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:264 | : if (incDragFloat( | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:279 | : if (incDragFloat( | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:293 | : if (incDragFloat( | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:318 | : if (incDragFloat( | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:329 | : if (igButton("", ImVec2(24, 24))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:333 | : if (igButton("", ImVec2(24, 24))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:340 | : if (igButton("", ImVec2(24, 24))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/contours.d:349 | : if (igButton("", ImVec2(24, 24))) { | mesh automesh | semantic assertion passed; Horizontal mirror sampling uses nearest-contour matching; vertical mirror sampling is unimplemented in v0.8.6. |
| source/creator/viewport/common/automesh/grid.d:98 | editScale: if (incDragFloat( | mesh automesh | semantic assertion passed; Grid automesh does not implement horizontal/vertical mirroring in v0.8.6. |
| source/creator/viewport/common/automesh/grid.d:109 | editScale: if (igButton("", ImVec2(24, 24))) { | mesh automesh | semantic assertion passed; Grid automesh does not implement horizontal/vertical mirroring in v0.8.6. |
| source/creator/viewport/common/automesh/grid.d:113 | editScale: if (igButton("", ImVec2(24, 24))) { | mesh automesh | semantic assertion passed; Grid automesh does not implement horizontal/vertical mirroring in v0.8.6. |
| source/creator/viewport/common/automesh/grid.d:120 | editScale: if (igButton("", ImVec2(24, 24))) { | mesh automesh | semantic assertion passed; Grid automesh does not implement horizontal/vertical mirroring in v0.8.6. |
| source/creator/viewport/common/automesh/grid.d:129 | editScale: if (igButton("", ImVec2(24, 24))) { | mesh automesh | semantic assertion passed; Grid automesh does not implement horizontal/vertical mirroring in v0.8.6. |
| source/creator/viewport/common/automesh/grid.d:166 | divideAxes: if (incDragFloat( | mesh automesh | semantic assertion passed; Grid automesh does not implement horizontal/vertical mirroring in v0.8.6. |
| source/creator/viewport/common/automesh/grid.d:179 | divideAxes: if (incDragFloat( | mesh automesh | semantic assertion passed; Grid automesh does not implement horizontal/vertical mirroring in v0.8.6. |
| source/creator/viewport/common/automesh/grid.d:192 | divideAxes: if (incDragFloat( | mesh automesh | semantic assertion passed; Grid automesh does not implement horizontal/vertical mirroring in v0.8.6. |
| source/creator/viewport/common/automesh/grid.d:205 | divideAxes: if (incDragFloat( | mesh automesh | semantic assertion passed; Grid automesh does not implement horizontal/vertical mirroring in v0.8.6. |
| source/creator/viewport/common/mesheditor/brushes/circlebrush.d:63 | configure: incDragFloat( | mesh brush | semantic assertion passed |
| source/creator/viewport/common/mesheditor/brushes/doublethreshbrush.d:70 | configure: incDragFloat( | mesh brush | semantic assertion passed |
| source/creator/viewport/common/mesheditor/brushes/doublethreshbrush.d:79 | configure: incDragFloat( | mesh brush | semantic assertion passed |
| source/creator/viewport/common/mesheditor/brushes/rectanglebrush.d:66 | configure: incDragFloat( | mesh brush | semantic assertion passed |
| source/creator/viewport/common/mesheditor/brushes/rectanglebrush.d:75 | configure: incDragFloat( | mesh brush | semantic assertion passed |
| source/creator/viewport/common/mesheditor/brushes/rectanglebrush.d:84 | configure: incDragFloat( | mesh brush | semantic assertion passed; The rectangle inner ratio control is exposed but unused by v0.8.6 weightAt(). |
| source/creator/viewport/common/mesheditor/package.d:282 | popupMenu: if (igMenuItem(__("Reset selected"), "", false, true)) { | key reset | semantic assertion passed |
| source/creator/viewport/common/mesheditor/package.d:285 | popupMenu: if (igMenuItem(__("Flip selected from mirror"), "", false, true)) { | key from-mirror | semantic assertion passed |
| source/creator/viewport/common/mesheditor/tools/base.d:95 | viewportTools: if (incButtonColored(icon.toStringz, ImVec2(0, 0), toolMode == mode ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { | cli-lifecycle | Selecting a canvas tool is represented by choosing the mesh operation; explicit selection arguments replace tool-local mouse state. |
| source/creator/viewport/common/mesheditor/tools/brush.d:253 | displayToolOptions: if (incButtonColored("", ImVec2(0, 0), (brushTool !is null && !brushTool.getFlow())? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { // path definition | mesh brush | semantic assertion passed |
| source/creator/viewport/common/mesheditor/tools/brush.d:263 | displayToolOptions: if (incButtonColored("", ImVec2(0, 0), (brushTool !is null && brushTool.getFlow())? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { // path definition | mesh brush | semantic assertion passed |
| source/creator/viewport/common/mesheditor/tools/brush.d:283 | displayToolOptions: if (igSelectable(brush.name().toStringz)) { | mesh brush | semantic assertion passed |
| source/creator/viewport/common/mesheditor/tools/pathdeform.d:408 | displayToolOptions: if (incButtonColored("", ImVec2(0, 0), (deformTool !is null && deformTool.mode == PathDeformTool.Mode.Define)? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { // path definition | mesh path | semantic assertion passed |
| source/creator/viewport/common/mesheditor/tools/pathdeform.d:419 | displayToolOptions: if (incButtonColored("", ImVec2(0, 0), (deformTool !is null && deformTool.mode == PathDeformTool.Mode.Transform) ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { // path deformation | mesh path | semantic assertion passed |
| source/creator/viewport/common/mesheditor/tools/pathdeform.d:432 | displayToolOptions: if (incButtonColored("", ImVec2(0, 0), (deformTool !is null && deformTool.getIsRotateMode()) ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { // rotation mode | mesh path | semantic assertion passed |
| source/creator/viewport/common/mesheditor/tools/pathdeform.d:445 | displayToolOptions: if (incButtonColored("", ImVec2(0, 0), (deformTool !is null && deformTool.getIsShiftMode()) ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { // move shift | mesh path | semantic assertion passed |
| source/creator/viewport/common/mesheditor/tools/point.d:486 | displayToolOptions: if (incButtonColored("", ImVec2(0, 0), (pointTool !is null && !pointTool.isAutoConnect())? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { | mesh vertex-set | semantic assertion passed |
| source/creator/viewport/model/package.d:82 | incViewportModelMenu: if (igMenuItem(incViewportModelMenuSortMode == ViewporMenuSortMode.ZSort ? __("Z-Sort") : __("Size-Sort"))) { | node hit | semantic assertion passed |
| source/creator/viewport/model/package.d:92 | incViewportModelMenu: if (igMenuItem(__("Focus Selected"))) { | render image | semantic assertion passed |
| source/creator/viewport/model/package.d:107 | incViewportModelMenu: if (igSelectable("###PartSelectable", false, ImGuiSelectableFlags.None, ImVec2(avail.x, ENTRY_SIZE))) { | node hit | semantic assertion passed |
| source/creator/viewport/model/package.d:161 | incViewportModelConfirmBar: if (igButton(text, ImVec2(0, 26))) { | render image | semantic assertion passed |
| source/creator/viewport/model/package.d:198 | incViewportModelOptions: if (incButtonColored("", ImVec2(0, 0), incShowVertices ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { | render image | semantic assertion passed |
| source/creator/viewport/model/package.d:204 | incViewportModelOptions: if (incButtonColored("", ImVec2(0, 0), incShowBounds ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { | render image | semantic assertion passed |
| source/creator/viewport/model/package.d:210 | incViewportModelOptions: if (incButtonColored("", ImVec2(0, 0), incShowOrientation ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { | render image | semantic assertion passed |
| source/creator/viewport/model/package.d:228 | incViewportModelOptions: igColorPicker3(__("COLOR"), &clearColor.vector, | render image | semantic assertion passed |
| source/creator/viewport/model/package.d:239 | incViewportModelOptions: if (igButton(__("Reset"), ImVec2(space.x, 0))) incResetClearColor(); | render image | semantic assertion passed |
| source/creator/viewport/package.d:522 | isOwned: igButton("", ImVec2(32, 32)); | node set | semantic assertion passed |
| source/creator/viewport/package.d:650 | isOwned: igButton("", ImVec2(32, 32)); | node set | semantic assertion passed |
| source/creator/viewport/package.d:740 | getArg: igButton("", ImVec2(32, 32)); | node set | semantic assertion passed |
| source/creator/viewport/vertex/package.d:72 | incViewportVertexOptions: if (incButtonColored("\ue3eb##mesh-group-view-node", ImVec2(0, 0), editor.getShowMeshgroupNodeChild() ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:81 | incViewportVertexOptions: if (igButton("")) { | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:92 | incViewportVertexOptions: if (igButton("")) { | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:105 | incViewportVertexOptions: if (incButtonColored("", ImVec2(0, 0), editor.getMirrorHoriz() ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:113 | incViewportVertexOptions: if (incButtonColored("", ImVec2(0, 0), editor.getMirrorVert() ? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:123 | incViewportVertexOptions: if (incButtonColored("", ImVec2(0, 0), | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:135 | incViewportVertexOptions: if (incButtonColored(__("Bake"), ImVec2(incAvailableSpace().x, 0), | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:153 | incViewportVertexOptions: if (igButton("")) { | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:169 | incViewportVertexOptions: if (incButtonColored(processor.icon().toStringz, ImVec2(0, 0), (processor == activeProcessor)? ImVec4.init : ImVec4(0.6, 0.6, 0.6, 1))) { | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:180 | incViewportVertexOptions: if (igButton(__("Bake"),ImVec2(incAvailableSpace().x, 0))) { | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:204 | incViewportVertexConfirmBar: if (igButton(__(" Apply"), ImVec2(0, 26))) { | render image | semantic assertion passed |
| source/creator/viewport/vertex/package.d:227 | incViewportVertexConfirmBar: if (igButton(__(" Cancel"), ImVec2(0, 26))) { | cli-lifecycle | Dialog dismissal has no model operation; discard an edit group with history end followed by history undo. |
| source/creator/widgets/button.d:16 | incButtonColored: return igButton(text, size); | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/button.d:22 | incButtonColored: return igButton(text, size); | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/dialog.d:118 | incRenderDialogs: if (igButton(__("Yes"), ImVec2(btnSize, btnHeight))) { | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/dialog.d:126 | incRenderDialogs: if (igButton(__("OK"), ImVec2(btnSize, btnHeight))) { | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/dialog.d:134 | incRenderDialogs: if (igButton(__("No"), ImVec2(btnSize, btnHeight))) { | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/dialog.d:142 | incRenderDialogs: if (igButton(__("Cancel"), ImVec2(btnSize, btnHeight))) { | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/drag.d:42 | incDragFloat: if (igDragFloat("###DRAG", value, adjustSpeed, minValue, maxValue, fmt.ptr, flags)) { | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/inputtext.d:28 | incInputText: return incInputText(wId, available.x, buffer, flags); | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/inputtext.d:60 | incInputText: if (igInputText( | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/inputtext.d:108 | incInputText: return incInputText(wId, label, available.x, buffer, flags); | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/inputtext.d:141 | incInputText: if (igInputText( | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/mainmenu.d:128 | incMainMenu: if(igMenuItem(__("New"), "Ctrl+N", false, true)) { | project new | semantic assertion passed |
| source/creator/widgets/mainmenu.d:132 | incMainMenu: if (igMenuItem(__("Open"), "Ctrl+O", false, true)) { | cli-lifecycle | Each command opens its model and exits; any saved/autosaved model path is accepted. |
| source/creator/widgets/mainmenu.d:143 | incMainMenu: if (igMenuItem(autosavePath, "", false, true)) { | cli-lifecycle | Each command opens its model and exits; any saved/autosaved model path is accepted. |
| source/creator/widgets/mainmenu.d:155 | incMainMenu: if (igMenuItem(project.baseName.toStringz, "", false, true)) { | cli-lifecycle | Each command opens its model and exits; any saved/autosaved model path is accepted. |
| source/creator/widgets/mainmenu.d:163 | incMainMenu: if(igMenuItem(__("Save"), "Ctrl+S", false, true)) { | project save | semantic assertion passed |
| source/creator/widgets/mainmenu.d:167 | incMainMenu: if(igMenuItem(__("Save As..."), "Ctrl+Shift+S", false, true)) { | project save | semantic assertion passed |
| source/creator/widgets/mainmenu.d:172 | incMainMenu: if(igMenuItem(__("Photoshop Document"), "", false, true)) { | project import | semantic assertion passed |
| source/creator/widgets/mainmenu.d:177 | incMainMenu: if(igMenuItem(__("Krita Document"), "", false, true)) { | project import | semantic assertion passed |
| source/creator/widgets/mainmenu.d:183 | incMainMenu: if (igMenuItem(__("Inochi2D Puppet"), "", false, true)) { | project import | semantic assertion passed |
| source/creator/widgets/mainmenu.d:195 | incMainMenu: if (igMenuItem(__("Image Folder"))) { | project import | semantic assertion passed |
| source/creator/widgets/mainmenu.d:205 | incMainMenu: if(igMenuItem(__("Photoshop Document"), "", false, true)) { | project merge | semantic assertion passed |
| source/creator/widgets/mainmenu.d:218 | incMainMenu: if(igMenuItem(__("Krita Document"), "", false, true)) { | project merge | semantic assertion passed |
| source/creator/widgets/mainmenu.d:231 | incMainMenu: if(igMenuItem(__("Image Files"), "", false, true)) { | project merge | semantic assertion passed |
| source/creator/widgets/mainmenu.d:249 | incMainMenu: if (igMenuItem(__("Inochi Creator Project"), "", false, true)) { | unimplemented | The v0.8.6 callback only dismisses the welcome window; project merge is implemented separately by the CLI. |
| source/creator/widgets/mainmenu.d:266 | incMainMenu: if(igMenuItem(__("Inochi2D Puppet"), "", false, true)) { | export inp | semantic assertion passed |
| source/creator/widgets/mainmenu.d:275 | incMainMenu: if(igMenuItem(__("PNG (*.png)"), "", false, true)) { | export image | semantic assertion passed |
| source/creator/widgets/mainmenu.d:284 | incMainMenu: if(igMenuItem(__("JPEG (*.jpeg)"), "", false, true)) { | export image | semantic assertion passed |
| source/creator/widgets/mainmenu.d:293 | incMainMenu: if(igMenuItem(__("TARGA (*.tga)"), "", false, true)) { | export image | semantic assertion passed |
| source/creator/widgets/mainmenu.d:304 | incMainMenu: if(igMenuItem(__("Video"), "", false, incVideoCanExport())) { | export video | semantic assertion passed |
| source/creator/widgets/mainmenu.d:324 | incMainMenu: if (igMenuItem(__("Close Project"))) { | cli-lifecycle | Each command opens its model and exits; any saved/autosaved model path is accepted. |
| source/creator/widgets/mainmenu.d:333 | incMainMenu: if (igMenuItem(__("Quit"), "Alt+F4", false, true)) incExit(); | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:338 | incMainMenu: if(igMenuItem(__("Undo"), "Ctrl+Z", false, incActionCanUndo())) incActionUndo(); | history undo | semantic assertion passed |
| source/creator/widgets/mainmenu.d:339 | incMainMenu: if(igMenuItem(__("Redo"), "Ctrl+Shift+Z", false, incActionCanRedo())) incActionRedo(); | history redo | semantic assertion passed |
| source/creator/widgets/mainmenu.d:342 | incMainMenu: if(igMenuItem(__("Cut"), "Ctrl+X", false, false)) {} | disabled | Disabled in v0.8.6. |
| source/creator/widgets/mainmenu.d:343 | incMainMenu: if(igMenuItem(__("Copy"), "Ctrl+C", false, false)) {} | disabled | Disabled in v0.8.6. |
| source/creator/widgets/mainmenu.d:344 | incMainMenu: if(igMenuItem(__("Paste"), "Ctrl+V", false, false)) {} | disabled | Disabled in v0.8.6. |
| source/creator/widgets/mainmenu.d:347 | incMainMenu: if(igMenuItem(__("Settings"), "", false, true)) { | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:358 | incMainMenu: if(igMenuItem(__("Style Editor"), "", dbgShowStyleEditor, true)) dbgShowStyleEditor = !dbgShowStyleEditor; | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:359 | incMainMenu: if(igMenuItem(__("ImGui Debugger"), "", dbgShowDebugger, true)) dbgShowDebugger = !dbgShowDebugger; | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:360 | incMainMenu: if(igMenuItem(__("ImGui Metrics"), "", dbgShowMetrics, true)) dbgShowMetrics = !dbgShowMetrics; | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:361 | incMainMenu: if(igMenuItem(__("ImGui Stack Tool"), "", dbgShowStackTool, true)) dbgShowStackTool = !dbgShowStackTool; | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:367 | incMainMenu: if (igMenuItem(__("Reset Layout"), null, false, true)) { | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:387 | incMainMenu: if(igMenuItem(panel.displayNameC, null, panel.visible, true)) { | out-of-scope | Panel visibility/layout control excluded by the scope. |
| source/creator/widgets/mainmenu.d:405 | incMainMenu: if (igMenuItem(__("Open Configuration Folder"), null, false, true)) { | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:417 | incMainMenu: if (igMenuItem(__("Save Screenshot"), "", false, true)) { | render image | semantic assertion passed |
| source/creator/widgets/mainmenu.d:450 | incMainMenu: if (igMenuItem(__("Show Stats for Nerds"), "", incShowStatsForNerds, true)) { | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:466 | incMainMenu: if (igMenuItem(__("Import Inochi Session Data"), null, false, true)) { | project import-session | semantic assertion passed |
| source/creator/widgets/mainmenu.d:492 | incMainMenu: if (igMenuItem(__("Premultiply textures"), "", false)) { | texture premultiply | semantic assertion passed |
| source/creator/widgets/mainmenu.d:498 | incMainMenu: if (igMenuItem(__("Bleed textures..."), "", false)) { | texture bleed | semantic assertion passed |
| source/creator/widgets/mainmenu.d:503 | incMainMenu: if (igMenuItem(__("Generate Mipmaps..."), "", false)) { | texture mipmaps | semantic assertion passed |
| source/creator/widgets/mainmenu.d:508 | incMainMenu: if (igMenuItem(__("Generate fake layer name info..."), "", false)) { | project layer-names | semantic assertion passed |
| source/creator/widgets/mainmenu.d:528 | incMainMenu: if (igMenuItem(__("Attempt full repair..."), "", false)) { | project repair | semantic assertion passed |
| source/creator/widgets/mainmenu.d:534 | incMainMenu: if (igMenuItem(__("Regenerate Node IDs"), "", false)) { | project regenerate-ids | semantic assertion passed |
| source/creator/widgets/mainmenu.d:544 | incMainMenu: if (igMenuItem(__("Verify INP File..."), "", false)) { | project check | semantic assertion passed |
| source/creator/widgets/mainmenu.d:554 | incMainMenu: if(igMenuItem(__("Online Documentation"), "", false, true)) { | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:558 | incMainMenu: if(igMenuItem(__("Inochi2D Documentation"), "", false, true)) { | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:566 | incMainMenu: if (igMenuItem(__("Report a Bug"))) { | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:569 | incMainMenu: if (igMenuItem(__("Request a Feature"))) { | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:577 | incMainMenu: if(igMenuItem(__("About"), "", false, true)) { | out-of-scope | Application/UI command. |
| source/creator/widgets/mainmenu.d:615 | incMainMenu: if(igMenuItem(__("Donate"))) { | out-of-scope | Application/UI command. |
| source/creator/widgets/modal/nagscreen.d:120 | onUpdate: if (igButton(btnText, ImVec2(64, 24))) { | ui-only | Shared widget/input implementation; semantic callers are listed separately. |
| source/creator/widgets/toolbar.d:37 | incToolbar: if (incButtonColored("##MirrorView", ImVec2(32, 32), incShouldMirrorViewport ? ImVec4.init : ImVec4(0.6f, 0.6f, 0.6f, 1f))) { | render image | semantic assertion passed |
| source/creator/widgets/toolbar.d:44 | incToolbar: if (incButtonColored("", ImVec2(32, 32), incActivePuppet().enableDrivers ? ImVec4.init : ImVec4(0.6f, 0.6f, 0.6f, 1f))) { | render image | semantic assertion passed |
| source/creator/widgets/toolbar.d:51 | incToolbar: if (incButtonColored("", ImVec2(32, 32), incShouldPostProcess ? ImVec4.init : ImVec4(0.6f, 0.6f, 0.6f, 1f))) { | render image | semantic assertion passed |
| source/creator/widgets/toolbar.d:56 | incToolbar: if (incButtonColored("", ImVec2(32, 32), ImVec4.init)) { | render image | semantic assertion passed |
| source/creator/widgets/toolbar.d:63 | incToolbar: if (incButtonColored("", ImVec2(32, 32), ImVec4.init)) { | render image | semantic assertion passed |
| source/creator/widgets/toolbar.d:68 | incToolbar: if (incButtonColored("", ImVec2(32, 32), ImVec4.init)) { | render image | semantic assertion passed |
| source/creator/widgets/toolbar.d:92 | incToolbar: if (incButtonColored("", ImVec2(32, 32), incEditMode == EditMode.ModelEdit ? ImVec4.init : ImVec4(0.6f, 0.6f, 0.6f, 1f))) { | cli-lifecycle | Editor mode selection is represented by node/mesh/key, animation and render command groups. |
| source/creator/widgets/toolbar.d:97 | incToolbar: if (incButtonColored("", ImVec2(32, 32), incEditMode == EditMode.AnimEdit ? ImVec4.init : ImVec4(0.6f, 0.6f, 0.6f, 1f))) { | cli-lifecycle | Editor mode selection is represented by node/mesh/key, animation and render command groups. |
| source/creator/widgets/toolbar.d:102 | incToolbar: if (incButtonColored("", ImVec2(32, 32), incEditMode == EditMode.ModelTest ? ImVec4.init : ImVec4(0.6f, 0.6f, 0.6f, 1f))) { | cli-lifecycle | Editor mode selection is represented by node/mesh/key, animation and render command groups. |
| source/creator/widgets/toolbar.d:179 | incToolbarButton: bool clicked = igButton(text, ImVec2(width, incAvailableSpace().y)); | ui-only | Shared button helper; concrete operation callers are inventoried separately. |
| source/creator/windows/about.d:115 | onUpdate: if (igButton("GitHub", ImVec2(8+spacing, 0))) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/about.d:121 | onUpdate: if (igButton("Twitter", ImVec2(spacing, 0))) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/about.d:128 | onUpdate: if (igButton(__("Donate"), ImVec2(spacing, 0))) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/autosave.d:55 | onUpdate: if (igButton(__("Discard"), ImVec2(64, 24))) { | cli-lifecycle | Open the selected saved model by its file path. |
| source/creator/windows/autosave.d:61 | onUpdate: if (igButton(__("Restore"), ImVec2(64, 24))) { | cli-lifecycle | Open the selected saved model by its file path. |
| source/creator/windows/editanim.d:83 | onUpdate: if (incInputText("NAME", avail.x-16, name, ImGuiInputTextFlags.EnterReturnsTrue)) { | animation set | semantic assertion passed |
| source/creator/windows/editanim.d:90 | onUpdate: igCheckbox(__("Additive"), &newAnim.additive); | animation set | semantic assertion passed; Editable persisted fields; v0.8.6 AnimationPlayback does not consume additive or animationWeight. |
| source/creator/windows/editanim.d:91 | onUpdate: igInputFloat(__("Weight"), &newAnim.animationWeight); | animation set | semantic assertion passed; Editable persisted fields; v0.8.6 AnimationPlayback does not consume additive or animationWeight. |
| source/creator/windows/editanim.d:93 | onUpdate: if (igDragInt(__("Frames"), &newAnim.length, 1, 1, int.max)) { | animation set | semantic assertion passed |
| source/creator/windows/editanim.d:96 | onUpdate: igDragInt(__("Lead In"), &newAnim.leadIn, 1, 0, newAnim.length); | animation set | semantic assertion passed |
| source/creator/windows/editanim.d:97 | onUpdate: igDragInt(__("Lead Out"), &newAnim.leadOut, 1, 0, newAnim.length); | animation set | semantic assertion passed |
| source/creator/windows/editanim.d:102 | onUpdate: if (igSelectable(fpsOptions[i], i == frameRateOption)) | animation set | semantic assertion passed |
| source/creator/windows/editanim.d:112 | onUpdate: igInputFloat(__("Custom Framerate"), &framerate); | animation set | semantic assertion passed |
| source/creator/windows/editanim.d:131 | onUpdate: if (igButton(btnName.toStringz, ImVec2(doneLength+8, 20))) { | animation set | semantic assertion passed |
| source/creator/windows/flipconfig.d:221 | treeView: igSelectable((incTypeIdToIcon(node.typeId)~node.name).toStringz, false, ImGuiSelectableFlagsI.SpanAvailWidth); | param pair-add | semantic assertion passed |
| source/creator/windows/flipconfig.d:266 | pairView: igSelectable("##%s".format(pair.parts[0].cName).toStringz, active == &pair, ImGuiSelectableFlags.SpanAllColumns, ImVec2(0, 16)); | param pair-add | semantic assertion passed |
| source/creator/windows/flipconfig.d:349 | pairView: if (igButton("", ImVec2(16, 16))) { | param pair-set | semantic assertion passed |
| source/creator/windows/flipconfig.d:421 | onUpdate: incInputText("##", childWidth, nodeFilter); | node list | semantic assertion passed |
| source/creator/windows/flipconfig.d:432 | onUpdate: incInputText("##part1", (childWidth - 50) / 2, part1Pattern); | param pair-auto | semantic assertion passed |
| source/creator/windows/flipconfig.d:434 | onUpdate: if (igButton(__("Pair"), ImVec2(48, 0))) { | param pair-auto | semantic assertion passed |
| source/creator/windows/flipconfig.d:438 | onUpdate: incInputText("##part2", (childWidth - 50) / 2, part2Pattern); | param pair-auto | semantic assertion passed |
| source/creator/windows/flipconfig.d:479 | onUpdate: if (igButton(__("Cancel"), ImVec2(96, 24))) { | cli-lifecycle | Dialog dismissal has no model operation; discard an edit group with history end followed by history undo. |
| source/creator/windows/flipconfig.d:486 | onUpdate: if (igButton(__("Save"), ImVec2(96, 24))) { | param pair-add | semantic assertion passed |
| source/creator/windows/imgexport.d:101 | onUpdate: if (igMenuItem(camera.cName)) { | export image | semantic assertion passed |
| source/creator/windows/imgexport.d:110 | onUpdate: igCheckbox(__("Allow Transparency"), &transparency); | export image | semantic assertion passed |
| source/creator/windows/imgexport.d:111 | onUpdate: igCheckbox(__("Use Post Processing"), &postprocessing); | export image | semantic assertion passed |
| source/creator/windows/imgexport.d:122 | onUpdate: if (igButton(__("Save"), ImVec2(64, 24))) { | export image | semantic assertion passed |
| source/creator/windows/inpexport.d:106 | onUpdate: if (igSelectable(__("Atlassing"), pane == ExportOptionsPane.Atlassing)) { | ui-only | Export settings pane navigation; all settings are explicit export options. |
| source/creator/windows/inpexport.d:110 | onUpdate: if (igSelectable(__("Decoration"), pane == ExportOptionsPane.Decoration)) { | ui-only | Export settings pane navigation; all settings are explicit export options. |
| source/creator/windows/inpexport.d:149 | onUpdate: if (igMenuItem(sizestr, null, settings.atlasResolution == size)) { | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:158 | onUpdate: igCheckbox(__("Non-linear Scaling"), &settings.nonLinearScaling); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:162 | onUpdate: if (igInputInt(__("Texture Scale"), &resScaleInt, 1, 10)) { | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:168 | onUpdate: if (igInputInt(__("Padding"), &settings.padding, 1, 10)) { | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:176 | onUpdate: igCheckbox(__("Prune unused nodes"), &settings.optimizePruneUnused); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:200 | onUpdate: if (igMenuItem(__("Load"))) { | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:222 | onUpdate: if (igMenuItem(__("Remove"), null, false, settings.decorateWatermark !is null)) { | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:269 | onUpdate: if (igSelectable(__("Normal"), settings.decorateWatermarkBlendMode == BlendMode.Normal)) this.setBlending(BlendMode.Normal); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:273 | onUpdate: if (igSelectable(__("Multiply"), settings.decorateWatermarkBlendMode == BlendMode.Multiply)) this.setBlending(BlendMode.Multiply); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:276 | onUpdate: if (igSelectable(__("Screen"), settings.decorateWatermarkBlendMode == BlendMode.Screen)) this.setBlending(BlendMode.Screen); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:279 | onUpdate: if (igSelectable(__("Overlay"), settings.decorateWatermarkBlendMode == BlendMode.Overlay)) this.setBlending(BlendMode.Overlay); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:282 | onUpdate: if (igSelectable(__("Darken"), settings.decorateWatermarkBlendMode == BlendMode.Darken)) this.setBlending(BlendMode.Darken); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:285 | onUpdate: if (igSelectable(__("Lighten"), settings.decorateWatermarkBlendMode == BlendMode.Lighten)) this.setBlending(BlendMode.Lighten); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:288 | onUpdate: if (igSelectable(__("Color Dodge"), settings.decorateWatermarkBlendMode == BlendMode.ColorDodge)) this.setBlending(BlendMode.ColorDodge); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:291 | onUpdate: if (igSelectable(__("Linear Dodge"), settings.decorateWatermarkBlendMode == BlendMode.LinearDodge)) this.setBlending(BlendMode.LinearDodge); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:294 | onUpdate: if (igSelectable(__("Add (Glow)"), settings.decorateWatermarkBlendMode == BlendMode.AddGlow)) this.setBlending(BlendMode.AddGlow); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:297 | onUpdate: if (igSelectable(__("Color Burn"), settings.decorateWatermarkBlendMode == BlendMode.ColorBurn)) this.setBlending(BlendMode.ColorBurn); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:300 | onUpdate: if (igSelectable(__("Hard Light"), settings.decorateWatermarkBlendMode == BlendMode.HardLight)) this.setBlending(BlendMode.HardLight); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:303 | onUpdate: if (igSelectable(__("Soft Light"), settings.decorateWatermarkBlendMode == BlendMode.SoftLight)) this.setBlending(BlendMode.SoftLight); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:306 | onUpdate: if (igSelectable(__("Subtract"), settings.decorateWatermarkBlendMode == BlendMode.Subtract)) this.setBlending(BlendMode.Subtract); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:309 | onUpdate: if (igSelectable(__("Difference"), settings.decorateWatermarkBlendMode == BlendMode.Difference)) this.setBlending(BlendMode.Difference); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:312 | onUpdate: if (igSelectable(__("Exclusion"), settings.decorateWatermarkBlendMode == BlendMode.Exclusion)) this.setBlending(BlendMode.Exclusion); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:315 | onUpdate: if (igSelectable(__("Inverse"), settings.decorateWatermarkBlendMode == BlendMode.Inverse)) this.setBlending(BlendMode.Inverse); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:319 | onUpdate: if (igSelectable(__("Destination In"), settings.decorateWatermarkBlendMode == BlendMode.DestinationIn)) this.setBlending(BlendMode.DestinationIn); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:322 | onUpdate: if (igSelectable(__("Clip to Lower"), settings.decorateWatermarkBlendMode == BlendMode.ClipToLower)) this.setBlending(BlendMode.ClipToLower); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:331 | onUpdate: if (igDragInt("###LOOPS", cast(int*)&settings.decorateWatermarkLoops, 1, 1, 1000)) this.regenPreview(); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:336 | onUpdate: if (igDragFloat("###OPACITY", &settings.decorateWatermarkOpacity, 0.01, 0, 1)) this.regenPreview(); | export inp | semantic assertion passed |
| source/creator/windows/inpexport.d:364 | onUpdate: if (igButton(__("Export"), ImVec2(64, 24))) { | export inp | semantic assertion passed |
| source/creator/windows/kramerge.d:252 | layerView: igSelectable(displayName, false, ImGuiSelectableFlagsI.SpanAvailWidth); | project merge-plan | semantic assertion passed |
| source/creator/windows/kramerge.d:280 | layerView: if (igMenuItem(__("Unmap"))) { | project merge | semantic assertion passed |
| source/creator/windows/kramerge.d:285 | layerView: if (igMenuItem(!layer.ignore ? __("Ignore") : __("Use"))) { | project merge | semantic assertion passed |
| source/creator/windows/kramerge.d:300 | treeView: igSelectable(part.cName, false, ImGuiSelectableFlagsI.SpanAvailWidth); | project merge-plan | semantic assertion passed |
| source/creator/windows/kramerge.d:376 | onUpdate: incInputText("##", childWidth-gapspace, layerFilter); | project merge-plan | semantic assertion passed |
| source/creator/windows/kramerge.d:382 | onUpdate: igCheckbox(__("Only show unmapped"), &onlyUnmapped); | project merge-plan | semantic assertion passed |
| source/creator/windows/kramerge.d:389 | onUpdate: incInputText("##", childWidth, nodeFilter); | project merge-plan | semantic assertion passed |
| source/creator/windows/kramerge.d:402 | onUpdate: igCheckbox(__("Auto-rename"), &renameMapped); | project merge | semantic assertion passed |
| source/creator/windows/kramerge.d:406 | onUpdate: igCheckbox(__("Re-translate"), &retranslateMapped); | project merge | semantic assertion passed |
| source/creator/windows/kramerge.d:420 | onUpdate: if (igButton(__("Merge"), ImVec2(64, 24))) { | project merge | semantic assertion passed |
| source/creator/windows/paramaxes.d:71 | axisPointList: if (incDragFloat( | param axis-move | semantic assertion passed |
| source/creator/windows/paramaxes.d:82 | axisPointList: if (igButton("", ImVec2(24, 24))) { | param axis-remove | semantic assertion passed |
| source/creator/windows/paramaxes.d:86 | axisPointList: if (igButton("", ImVec2(24, 24))) { | param axis-add | semantic assertion passed |
| source/creator/windows/paramaxes.d:93 | axisPointList: if (igButton("", ImVec2(24, 24))) { | param axis-remove | semantic assertion passed |
| source/creator/windows/paramaxes.d:102 | axisPointList: if (igButton("", ImVec2(24, 24))) { | param axis-add | semantic assertion passed |
| source/creator/windows/paramaxes.d:169 | onUpdate: if (igButton(__("Cancel"), ImVec2(64, 24))) { | cli-lifecycle | Dialog dismissal has no model operation; discard an edit group with history end followed by history undo. |
| source/creator/windows/paramaxes.d:176 | onUpdate: if (igButton(__("Save"), ImVec2(64, 24))) { | param axis-move | semantic assertion passed |
| source/creator/windows/paramprop.d:45 | onUpdate: incInputText("Name", paramName); | param set | semantic assertion passed |
| source/creator/windows/paramprop.d:58 | onUpdate: incDragFloat("adj_x_min", &min.vector[0], 1, -float.max, max.x-1, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | param set | semantic assertion passed |
| source/creator/windows/paramprop.d:66 | onUpdate: incDragFloat("adj_x_max", &max.vector[0], 1, min.x+1, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | param set | semantic assertion passed |
| source/creator/windows/paramprop.d:79 | onUpdate: incDragFloat("adj_y_min", &min.vector[1], 1, -float.max, max.y-1, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | param set | semantic assertion passed |
| source/creator/windows/paramprop.d:87 | onUpdate: incDragFloat("adj_y_max", &max.vector[1], 1, min.y+1, float.max, "%.2f", ImGuiSliderFlags.NoRoundToFormat); | param set | semantic assertion passed |
| source/creator/windows/paramprop.d:102 | onUpdate: if (igButton(__("Save"), ImVec2(64, 24))) { | param set | semantic assertion passed |
| source/creator/windows/paramsplit.d:79 | oldBindingsList: igSelectable(mapping.node.name.toStringz); | param split | semantic assertion passed |
| source/creator/windows/paramsplit.d:95 | newBindingsList: igSelectable(mapping.node.name.toStringz); | param split | semantic assertion passed |
| source/creator/windows/paramsplit.d:171 | onUpdate: if (igButton(__("Apply"), ImVec2(64, 24))) { | param split | semantic assertion passed |
| source/creator/windows/psdmerge.d:248 | layerView: igSelectable(displayName, false, ImGuiSelectableFlagsI.SpanAvailWidth); | project merge-plan | semantic assertion passed |
| source/creator/windows/psdmerge.d:276 | layerView: if (igMenuItem(__("Unmap"))) { | project merge | semantic assertion passed |
| source/creator/windows/psdmerge.d:281 | layerView: if (igMenuItem(!layer.ignore ? __("Ignore") : __("Use"))) { | project merge | semantic assertion passed |
| source/creator/windows/psdmerge.d:296 | treeView: igSelectable(part.cName, false, ImGuiSelectableFlagsI.SpanAvailWidth); | project merge-plan | semantic assertion passed |
| source/creator/windows/psdmerge.d:372 | onUpdate: incInputText("##", childWidth-gapspace, layerFilter); | project merge-plan | semantic assertion passed |
| source/creator/windows/psdmerge.d:378 | onUpdate: igCheckbox(__("Only show unmapped"), &onlyUnmapped); | project merge-plan | semantic assertion passed |
| source/creator/windows/psdmerge.d:385 | onUpdate: incInputText("##", childWidth, nodeFilter); | project merge-plan | semantic assertion passed |
| source/creator/windows/psdmerge.d:398 | onUpdate: igCheckbox(__("Auto-rename"), &renameMapped); | project merge | semantic assertion passed |
| source/creator/windows/psdmerge.d:402 | onUpdate: igCheckbox(__("Re-translate"), &retranslateMapped); | project merge | semantic assertion passed |
| source/creator/windows/psdmerge.d:416 | onUpdate: if (igButton(__("Merge"), ImVec2(64, 24))) { | project merge | semantic assertion passed |
| source/creator/windows/rename.d:47 | onUpdate: if (incInputText("RENAME", avail.x-16, strcpy, ImGuiInputTextFlags.EnterReturnsTrue)) { | node set | semantic assertion passed |
| source/creator/windows/rename.d:57 | onUpdate: if (igButton(__("Rename"), ImVec2(doneLength+8, 20))) { | node set | semantic assertion passed |
| source/creator/windows/settings.d:81 | onUpdate: if (igSelectable(__("Look and Feel"), settingsPane == SettingsPane.LookAndFeel)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:85 | onUpdate: if (igSelectable(__("Viewport"), settingsPane == SettingsPane.Viewport)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:89 | onUpdate: if (igSelectable(__("Accessbility"), settingsPane == SettingsPane.Accessibility)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:93 | onUpdate: if (igSelectable(__("File Handling"), settingsPane == SettingsPane.FileHandling)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:114 | onUpdate: if (igSelectable(__("Dark"), incGetDarkMode())) incSetDarkMode(true); | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:115 | onUpdate: if (igSelectable(__("Light"), !incGetDarkMode())) incSetDarkMode(false); | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:122 | onUpdate: if (igSelectable("English")) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:127 | onUpdate: if (igSelectable(entry.humanNameC)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:140 | onUpdate: if (igInputInt(__("UI Scale"), &tmpUIScale, 25, 50, ImGuiInputTextFlags.EnterReturnsTrue)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:150 | onUpdate: if (igDragInt(__("Max Undo History"), &maxHistory, 1, 1, 1000, "%d")) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:158 | onUpdate: if (igCheckbox(__("Disable Compositor"), &disableCompositor)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:167 | onUpdate: if (igCheckbox(__("Use OpenDyslexic Font"), &disableCompositor)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:174 | onUpdate: if (igCheckbox(__("Scroll to armed parameter"), &paramAutoScroll)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:183 | onUpdate: if (igCheckbox(__("Enable Autosaves"), &autosaveEnabled)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:188 | onUpdate: if (igInputInt(__("Save Interval (Minutes)"), &autosaveFreq, 5, 15, ImGuiInputTextFlags.EnterReturnsTrue)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:193 | onUpdate: if (igInputInt(__("Maximum Autosaves"), &saveFileLimit, 1, 5, ImGuiInputTextFlags.EnterReturnsTrue)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:210 | onUpdate: if (igSelectable(displayName.toStringz, keepLayerFolder == key)) | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:224 | onUpdate: if (igSelectable(options.toStringz)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:232 | onUpdate: if (igDragFloat(__("Zoom Speed"), &zoomSpeed, 0.1, 1, 50, "%f")) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/settings.d:259 | onUpdate: if (igButton(__("Done"), ImVec2(64, 24))) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/texviewer.d:30 | onUpdate: igSliderFloat("Zoom", &zoom, 0.1, 10, "%.2f"); | ui-only | Image viewer zoom is available to the Agent image viewer; texture export supplies the pixels. |
| source/creator/windows/trkbind.d:29 | boneElementSelectable: if (igSelectable(name, binding.mode == mode)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/trkbind.d:51 | onUpdate: if (igSelectable(param.name.toStringz, isSelected)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/trkbind.d:65 | onUpdate: if (igSelectable(name.toStringz, isSelected)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/trkbind.d:95 | onUpdate: if (igSelectable("X", binding.axis == 0)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/trkbind.d:100 | onUpdate: if (igSelectable("Y", binding.axis == 1)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/trkbind.d:110 | onUpdate: igCheckbox(__("Invert"), &binding.inverse); | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/trkbind.d:115 | onUpdate: if (igButton(__("Refresh Bindable"), ImVec2(0, 24))) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/trkbind.d:129 | onUpdate: if (igButton(__("Save"), ImVec2(64, 24))) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/videoexport.d:165 | onUpdate: if (igMenuItem(camera.cName)) { | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:174 | onUpdate: igCheckbox(__("Allow Transparency"), &transparency); | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:175 | onUpdate: igCheckbox(__("Use Post Processing"), &postprocessing); | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:183 | onUpdate: if (igMenuItem(name.toStringz)) { | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:192 | onUpdate: igDragInt(__("Loops"), &loops, 1, 0, int.max); | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:195 | onUpdate: igDragInt(__("Framerate"), &framerate, 1, -1, 240); | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:202 | onUpdate: igCheckbox(__("Lock to Animation Framerate"), &player.snapToFramerate); | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:208 | onUpdate: if (igMenuItem(cdc.name.toStringz)) { | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:234 | onUpdate: bool clicked = igButton(__("Export"), ImVec2(64, 24)); | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:272 | onUpdate: if (igButton(__("Cancel"), ImVec2(64, 24))) { | export video | semantic assertion passed |
| source/creator/windows/videoexport.d:278 | onUpdate: if (igButton(__("Close"), ImVec2(64, 24))) { | cli-lifecycle | Dismisses the completed export window; a CLI command exits after export. |
| source/creator/windows/welcome.d:162 | onUpdate: if (igSelectable("English")) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/welcome.d:167 | onUpdate: if (igSelectable(entry.humanNameC)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/welcome.d:176 | onUpdate: if (igSelectable(__("Dark"), incGetDarkMode())) incSetDarkMode(true); | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/welcome.d:177 | onUpdate: if (igSelectable(__("Light"), !incGetDarkMode())) incSetDarkMode(false); | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/welcome.d:187 | onUpdate: if (igInputInt(__("UI Scale"), &tmpUIScale, 25, 50, ImGuiInputTextFlags.EnterReturnsTrue)) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/welcome.d:212 | onUpdate: if (igButton(__("Next"), ImVec2(64, 24))) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/welcome.d:251 | onUpdate: if(igMenuItem(__("Import PSD..."))) { | out-of-scope | Application setup, help or tracking-device configuration. |
| source/creator/windows/welcome.d:257 | onUpdate: if(igMenuItem(__("Import KRA..."))) { | out-of-scope | Application setup, help or tracking-device configuration. |

## Canvas operations

| Upstream entry | Operations | CLI | Result assertion |
|---|---|---|---|
| source/creator/viewport/common/mesheditor/tools/point.d | Insert/delete vertices; drag; arrow-key translation and speed modifiers | mesh vertex-add/vertex-remove/transform | point insertion with auto-connect uses native mesh connections |
| source/creator/viewport/common/mesheditor/tools/connect.d | Connect/disconnect selected points, including mirror counterparts | mesh connect/disconnect | batch connection editing retains isolated edges through previews until a complete triangle can be saved |
| source/creator/viewport/common/mesheditor/tools/select.d | Click, toggle and rectangle selection; selected-point dragging | mesh select --vertices/--rect; mesh transform | native lasso polygon selection and reflected selection return the expected vertex indices |
| source/creator/viewport/common/mesheditor/tools/lasso.d | Polygon selection, additive/remove/toggle sets and mirrored selection | mesh select --polygon; explicit vertex sets | native lasso polygon selection and reflected selection return the expected vertex indices |
| source/creator/viewport/common/mesheditor/tools/grid.d | Create grid; add/delete/move axis points; drag X/Y/intersections | mesh grid --x/--y; mesh transform | grid axis addition, movement and removal regenerate the requested native rows and columns |
| source/creator/viewport/common/mesheditor/tools/brush.d | Weighted brush drag/flow strokes, axis lock via constrained stroke coordinates | mesh brush --stroke/--flow/--vertices | viewport brush normal and flow strokes with explicit sampling |
| source/creator/viewport/common/mesheditor/tools/pathdeform.d | Define/add/remove/translate path points; change target path; pivot rotation; along-path shift | mesh path --from/--to/--pivot/--dragged/--angle/--shift-point/--shift-to | path rotation uses the selected pivot and rotates the dragged side through the shared native operation |
| source/creator/panels/nodes.d | Node drag/drop reparenting and sibling order; multi-selection applies explicit grouped operations | node reparent --parent/--index; history begin/end | node sorting inserts a sibling at the requested index without changing local properties |
| source/creator/panels/parameters.d | Parameter group drag/drop and ungrouping | param set --group | group rename updates parameter paths and group deletion keeps all parameter data |
| source/creator/panels/timeline.d | Seek playhead; double-click add/remove lane keys; record both parameter axes | render --frame; animation lane-add/key-set/key-remove | animation duplication keeps independent key arrays and key removal changes only its target |

Upstream v0.8.6 limitations: disabled animation track merge controls; stored but unused animation Weight/Additive fields; rectangle brush inner ratio; vertical contour/grid mirroring; merge re-sort. Application settings, layout and tracking-device setup are outside the CLI scope.
