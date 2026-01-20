"""
Compatibility shim for Python 3.14+ where stdlib cgi was removed.
Only implements parse_header, which is required by httpx 0.13.x.
"""

def parse_header(line):
    """
    Parse a Content-Type style header into (value, params dict).
    This is a minimal replacement for cgi.parse_header.
    """
    if line is None:
        return "", {}

    parts = [part.strip() for part in line.split(";")]
    key = parts[0] if parts else ""
    params = {}
    for part in parts[1:]:
        if "=" not in part:
            continue
        name, value = part.split("=", 1)
        name = name.strip().lower()
        value = value.strip().strip('"').strip("'")
        params[name] = value
    return key, params
