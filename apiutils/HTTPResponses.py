from flask import Response
import json

def add_access_control(resp):
    # adds the correct access control to a given response
    # in our case we just always want all
    resp.headers['Access-Control-Allow-Origin'] = '*'

def make_json_response( resp_dict:dict, status=200):
    data = {
        'success' : True,
        'payload': resp_dict
    }
    # receives a dictionary and crafts the Flask JSON response object for it
    resp = Response(
        response=json.dumps(data), status=status, mimetype="text/plain"
    )

    # add_access_control(resp)
    resp.headers['Content-type'] = 'application/json'
    return resp

def error_response(status:int, message:str=None, error_json=None):
    # crafts an erroneous message with the status and returns it
    
    if message is not None:
        content = { 'error_message': message }

    elif error_json is not None:
        content = error_json

    else:
        raise Exception('No content provided')

    if 'error' not in content:
        content['error'] = True
        content['success'] = False

    content['statusCode'] = status

    resp = Response(
        response=json.dumps(content), status=status, mimetype="text/plain"
    )

    # resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Content-type'] = 'application/json'
    return resp
