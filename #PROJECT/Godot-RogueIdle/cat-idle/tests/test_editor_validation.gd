@tool
extends "res://addons/godot_ai/testing/test_suite.gd"
var history: EditorUndoRedoManager
func suite_name() -> String:
    return "editor_validation"
func suite_setup(ctx: Dictionary) -> void:
    history = ctx.undo_redo
func test_native_undo_and_redo() -> void:
    var root: Node = EditorInterface.get_edited_scene_root()
    if root == null or root.name != "McpValidation":
        skip("Independent validation scene must be open")
        return
    var label: Label = root.get_node("ProofLabel") as Label
    assert_eq(label.text, "MCP verified: editable and persistent")
    assert_true(editor_undo(history), "Native undo succeeds")
    assert_eq(label.text, "")
    assert_true(editor_redo(history), "Native redo succeeds")
    assert_eq(label.text, "MCP verified: editable and persistent")
    assert_eq(label.owner, root, "Node is owned by saved scene")
