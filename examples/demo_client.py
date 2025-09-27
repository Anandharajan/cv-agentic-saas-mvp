from urllib import request, parse
import mimetypes


def encode_multipart_formdata(fields, files):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    crlf = '\r\n'
    lines = []
    for (key, value) in fields:
        lines.append('--' + boundary)
        lines.append(f'Content-Disposition: form-data; name="{key}"')
        lines.append('')
        lines.append(value)
    for (key, filename, value) in files:
        lines.append('--' + boundary)
        lines.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"')
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        lines.append(f'Content-Type: {content_type}')
        lines.append('')
        lines.append(value)
    lines.append('--' + boundary + '--')
    lines.append('')
    body = crlf.join(lines).encode('utf-8')
    content_type = f'multipart/form-data; boundary={boundary}'
    return content_type, body


def main():
    # Sends a tiny 1x1 PNG to the /process endpoint
    import base64
    png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
    )
    img_bytes = base64.b64decode(png_base64)
    fields = []
    files = [("file", "tiny.png", img_bytes.decode('latin1'))]
    content_type, body = encode_multipart_formdata(fields, files)
    req = request.Request('http://127.0.0.1:8080/process')
    req.add_header('Content-Type', content_type)
    with request.urlopen(req, body) as resp:
        print(resp.read().decode())


if __name__ == '__main__':
    main()
