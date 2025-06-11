import requests
from PIL import Image
from io import BytesIO
import pyodbc
import os
import struct
from azure.identity import DefaultAzureCredential
import urllib
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="get_image_exif_metadata", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def get_image_exif_metadata(req: func.HttpRequest) -> func.HttpResponse:
    
    # Database connection parameters
    server = 'fl-campio-2025-svr.database.windows.net'
    database = 'fl-campio-2025-db'
    driver = '{ODBC Driver 18 for SQL Server}'

    # Build connection string for Azure SQL with Managed Identity access
    conn_str = (
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database};'
        'Authentication=Active Directory Managed Identity;'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
    )

    try:
        req_body = req.get_json()
    except ValueError:
        req_body = {}

    image_url_variable = req_body.get('image_url_param')
    if image_url_variable:
        try:
            # with pyodbc.connect(conn_str) as conn:
            #     with conn.cursor() as cursor:
            #         # Execute the stored procedure with image_url_variable as a parameter
            #         cursor.execute("EXEC dbo.usp_load_dbo_content_rtrn_key ?, ?, ?, ?", image_url_variable + "#img", image_url_variable, "image", image_url_variable)
            #         result = cursor.fetchone()
            response = requests.get(image_url_variable)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            exif_data = image.getexif()
            return func.HttpResponse(
                f"This HTTP triggered function executed successfully. The image URL is {image_url_variable}, and the EXIF metadata is: {exif_data}",
                status_code=200
            )
        except Exception as e:
            exif_data = None
            return func.HttpResponse(
                f"This HTTP triggered function didn't find any EXIF metadata for the image URL {image_url_variable}. Error: {str(e)}",
                status_code=404
            )
    else:
        return func.HttpResponse(
            "Please provide 'image_url_param' in the JSON body.",
            status_code=400
        )