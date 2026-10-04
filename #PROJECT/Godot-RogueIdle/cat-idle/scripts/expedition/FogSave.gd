@tool
class_name FogSave
extends RefCounted

const SLOT: String = "user://fog_expedition_v1.json"

static func save_state(state: Dictionary, path: String = SLOT) -> Dictionary:
    if not path.begins_with("user://fog_"):
        return {"ok": false, "message": "保存路径无效"}
    var text: String = JSON.stringify(state)
    var envelope: String = JSON.stringify({"payload": text, "sha256": text.sha256_text()})
    var temporary: String = path + ".tmp"
    var file: FileAccess = FileAccess.open(temporary, FileAccess.WRITE)
    if file == null:
        return {"ok": false, "message": "无法写入存档：" + error_string(FileAccess.get_open_error())}
    file.store_string(envelope)
    file.flush()
    var write_error: Error = file.get_error()
    file.close()
    if write_error != OK:
        return {"ok": false, "message": "存档写入失败：" + error_string(write_error)}
    var final_path: String = ProjectSettings.globalize_path(path)
    var backup_path: String = final_path + ".bak"
    if FileAccess.file_exists(path):
        var backup_error: Error = DirAccess.copy_absolute(final_path, backup_path)
        if backup_error != OK:
            return {"ok": false, "message": "无法保留存档备份"}
    var rename_error: Error = DirAccess.rename_absolute(ProjectSettings.globalize_path(temporary), final_path)
    if rename_error != OK:
        return {"ok": false, "message": "存档替换失败：" + error_string(rename_error)}
    return {"ok": true, "message": "已自动保存"}

static func load_state(path: String = SLOT) -> Dictionary:
    for candidate: String in [path, path + ".bak"]:
        if not FileAccess.file_exists(candidate):
            continue
        var parser: JSON = JSON.new()
        if parser.parse(FileAccess.get_file_as_string(candidate)) != OK:
            continue
        var decoded: Variant = parser.data
        if not decoded is Dictionary:
            continue
        var payload: String = str(decoded.get("payload", ""))
        if str(decoded.get("sha256", "")) != payload.sha256_text():
            continue
        if parser.parse(payload) != OK:
            continue
        var state: Variant = parser.data
        if state is Dictionary:
            return {"ok": true, "state": state, "from_backup": candidate != path}
    return {"ok": false, "message": "没有可恢复的有效存档"}

static func has_save(path: String = SLOT) -> bool:
    return FileAccess.file_exists(path) or FileAccess.file_exists(path + ".bak")
