"""Live background Blender sessions for parallel modellers.

The Blender MCP add-on can serve the same bridge from a background Blender (``--command blender_mcp``). Each
modeller gets its own persistent session on its own port, with its own copy of the kit .blend. That gives the same
run -> read back -> render -> look loop as the GUI MCP, and the scene state stays between calls. Only the GUI
session (port 9876) is driven through the MCP tool itself; these are driven from the shell:

    PY=C:/Users/Orang/.local/bin/python3.14.exe
    $PY art/blender/kit/mcp/bgmcp.py start 9877 <work.blend>      # launch (returns once the server answers)
    $PY art/blender/kit/mcp/bgmcp.py run 9877 <code.py>           # run a file; prints the JSON response
    $PY art/blender/kit/mcp/bgmcp.py run 9877 - <<'EOF'           # or code on stdin
    result = {"objects": len(bpy.data.objects)}
    EOF
    $PY art/blender/kit/mcp/bgmcp.py stop 9877                    # quit that Blender

As with the MCP tool, assign a JSON-able dict to ``result``. The log is art/blender/logs/bgmcp-<port>.log.
"""
import json
import os
import socket
import subprocess
import sys
import time

BLENDER = os.environ.get("BLENDER_PATH", "D:/Steam/steamapps/common/Blender/blender.exe")
LOGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs")


def request(port, code, timeout=3600):
    with socket.create_connection(("127.0.0.1", port), timeout=timeout) as s:
        s.sendall((json.dumps({"type": "execute", "code": code, "strict_json": False}) + "\0").encode("utf-8"))
        buf = bytearray()
        while b"\0" not in buf:
            chunk = s.recv(65536)
            if not chunk:
                break
            buf.extend(chunk)
    return json.loads(bytes(buf).split(b"\0", 1)[0])


def start(port, blend):
    os.makedirs(LOGS, exist_ok=True)
    log = open(os.path.join(LOGS, f"bgmcp-{port}.log"), "w")
    # no --factory-startup: the MCP add-on is a user extension and must load
    subprocess.Popen([BLENDER, "--background", blend, "--command", "blender_mcp", "--port", str(port)],
                     stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                     creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))
    for _ in range(120):
        time.sleep(1)
        try:
            r = request(port, "import bpy\nresult = {'file': bpy.data.filepath}", timeout=5)
            print(json.dumps(r))
            return 0
        except OSError:
            pass
    print(f"bgmcp: no server on port {port} after 120 s; see {log.name}")
    return 1


def main(argv):
    cmd, port = argv[0], int(argv[1])
    if cmd == "start":
        return start(port, argv[2])
    if cmd == "stop":
        try:
            request(port, "import bpy, threading\nthreading.Timer(0.5, lambda: __import__('os')._exit(0)).start()\n"
                          "result = {'stopping': True}", timeout=10)
        except OSError:
            pass
        print(json.dumps({"stopped": port}))
        return 0
    if cmd == "run":
        code = sys.stdin.read() if argv[2] == "-" else open(argv[2], encoding="utf-8").read()
        r = request(port, code)
        print(json.dumps(r, indent=1))
        return 0 if r.get("status") == "ok" else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
