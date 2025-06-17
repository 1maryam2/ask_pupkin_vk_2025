def application(environ, start_response):
    get_params = environ.get('QUERY_STRING', '')
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    post_params = environ['wsgi.input'].read(request_body_size).decode('utf-8')
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    
    response = [
        f"GET parameters: {get_params}\n".encode('utf-8'),
        f"POST parameters: {post_params}\n".encode('utf-8')
    ]
    
    return response