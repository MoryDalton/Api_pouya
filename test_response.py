def response_OK(detail):
    return {"isStatus": True, "detail": detail}

def response_ERROR(detail):
    return {"isStatus": False, "detail": detail}