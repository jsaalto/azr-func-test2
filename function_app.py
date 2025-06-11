import requests
from PIL import Image
from io import BytesIO

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="get_image_exif_metadata/{image_url_param}", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def get_image_exif_metadata(req: func.HttpRequest) -> func.HttpResponse:
    
    image_url_variable = req.params.get('image_url_param')
    if image_url_variable:
        try:
            response = requests.get(image_url_variable)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            exif_data = image.getexif()
        except Exception as e:
            exif_data = None
        return func.HttpResponse(
            f"This HTTP triggered function executed successfully. The image URL is {image_url_variable}, and the EXIF metadata is: {exif_data}",
            status_code=200
        )  
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )