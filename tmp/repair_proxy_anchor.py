from pathlib import Path
import datetime, shutil, re, ast, json

target = Path('C:/Users/1/.workbuddy/netfix/proxy_anchor.py')
source = target.read_text(encoding='utf-8')
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
backup = target.with_name('proxy_anchor.before-' + stamp + '.py')
shutil.copy2(target, backup)
start = source.index('def scan_candidates():')
end = source.index('\ndef pipe(', start)
replacement = '''def scan_candidates():
    """Use only the primary Feiniaojiasu core's configured mixed port.

    Never scan arbitrary HTTP services or the DIRECT-only extra core.
    Read on every lookup so client restarts and port changes are followed.
    """
    config = os.path.join(os.environ.get("LOCALAPPDATA", ""),
                          "com.fnjs.clash", "data", "clash", "config.yaml")
    try:
        with open(config, encoding="utf-8-sig") as f:
            text = f.read()
        match = re.search(r"(?m)^mixed-port:\\s*[\\\"']?(\\d+)", text)
        if match:
            port = int(match.group(1))
            if 0 < port < 65536 and port != LISTEN_PORT:
                return [port]
    except (OSError, ValueError):
        pass
    return []


def probe_proxy(port):
    """Verify mixed-port SOCKS5 greeting, not just any HTTP response."""
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=2.0) as s:
            s.sendall(bytes([5, 1, 0]))
            result = b""
            while len(result) < 2:
                part = s.recv(2 - len(result))
                if not part:
                    break
                result += part
            return result == bytes([5, 0])
    except OSError:
        return False


def get_target_port():
    candidates = scan_candidates()
    for port in candidates:
        with _lock:
            cached = (_last_good["port"] == port and
                      time.time() - _last_good["ts"] < 5)
        if cached or probe_proxy(port):
            with _lock:
                changed = _last_good["port"] != port
                _last_good.update(port=port, ts=time.time())
            if changed:
                log(f"Verified primary mixed proxy port: {port}")
            return port
    return None

'''
source = source[:start] + replacement + source[end:]
source = source.replace('up = socket.create_connection(("127.0.0.1", port), timeout=15)', 'up = socket.create_connection(("127.0.0.1", port), timeout=15)\n        up.settimeout(None)\n        client.settimeout(None)')
source = source.replace('    if p:\n        set_env_anchor()', '    # Existing system and user proxy settings are preserved on restart.')
ast.parse(source)
target.write_text(source, encoding='utf-8')
print(json.dumps({'backup': str(backup), 'target': str(target)}))
