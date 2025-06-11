import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="get_image_exif_metadata/{image_url_param}", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def get_image_exif_metadata(req: func.HttpRequest) -> func.HttpResponse:
    
    name = req.params.get('image_url_param')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )