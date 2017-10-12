from flask import abort

def get_or_abort(model, object_id, code=404):
    result = model.query.get(object_id)
    if result is None:
        abort(code)
    return result
