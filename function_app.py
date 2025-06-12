import os
import urllib
import struct
from io import BytesIO

import requests
import pyodbc
from PIL import Image
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="get_image_exif_metadata", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
@app.route(route="get_image_url", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])

def get_image_url(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        req_body = {}

    image_url_variable = req_body.get('image_url_param')
    if image_url_variable:
        return func.HttpResponse(
            f"This is the image URL {image_url_variable}.",
            status_code=200
        )
    else:
        return func.HttpResponse(
            f"Error processing the image URL {image_url_variable}. Error: 404 Not Found",
            status_code=404
        )

def get_image_exif_metadata(req: func.HttpRequest) -> func.HttpResponse:
    
    # Database connection parameters
    server = 'fl-campio-2025-svr.database.windows.net'
    database = 'fl-campio-2025-db'
    driver = '{ODBC Driver 18 for SQL Server}'

    # Build connection string for Azure SQL with Managed Identity access
    conn_str = (
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Authentication=ActiveDirectoryMsi;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    try:
        req_body = req.get_json()
    except ValueError:
        req_body = {}

    image_url_variable = req_body.get('image_url_param')
    if image_url_variable:
        try:
            response = requests.get(image_url_variable)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            exif_data = image.getexif()
            with pyodbc.connect(conn_str) as conn:
                with conn.cursor() as cursor:
                    # Execute the stored procedure with image_url_variable as a parameter
                    cursor.execute("EXEC dbo.usp_load_dbo_content_rtrn_key ?, ?, ?, ?", image_url_variable + "#img", image_url_variable, "image", image_url_variable)
                    result = cursor.fetchone()
                    content_key = int(result[0]) if result else None
                    if exif_data:
                        for tag_id, value in exif_data.items():
                            cursor.execute(
                                "INSERT INTO dbo.image_exif_metadata ([image_exif_metadata_NK],[content_key],[key_name],[key_value]) VALUES (?, ?, ?, ?)",
                                image_url_variable + '#' + str(tag_id) + '#img', content_key, str(tag_id), str(value)
                            )
                        conn.commit()
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