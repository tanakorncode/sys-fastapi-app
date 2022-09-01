from typing import Union
from fastapi import FastAPI, File, UploadFile
from DrivingLicense import DrivingLicense
from PersonalCard import PersonalCard
from utils import Language, Provider
import aiofiles
import os
import uuid

app = FastAPI()

myuuid = uuid.uuid4()

@app.get("/")
def read_root():
    return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


@app.post("/files/")
async def create_file(file: bytes | None = File(default=None)):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}


@app.post("/ocr-driving-license/")
async def create_upload_file(file: UploadFile | None = File(default=None)):
    if not file:
        return {"message": "No upload file sent"}
    else:
        filename, file_extension = os.path.splitext(file.filename)
        destination_file_path = os.getcwd() + "/uploads/" + \
            str(myuuid) + file_extension  # location to store file
    async with aiofiles.open(destination_file_path, 'wb') as out_file:
        while content := await file.read(1024):  # async read file chunk
            await out_file.write(content)  # async write file chunk
        # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.
        reader = DrivingLicense(lang="mix", provider=Provider.TESSERACT)
        result = reader.extractInfo(destination_file_path)
        os.remove(destination_file_path)
        return {"license_number": result.License_Number}

@app.post("/ocr-national-id-card/")
async def create_upload_file(file: UploadFile = File(...)):
    if not file:
        return {"message": "No upload file sent"}
    else:
        filename, file_extension = os.path.splitext(file.filename)
        print(file_extension)
        destination_file_path = os.getcwd() + "/uploads/" + \
            str(myuuid) + file_extension  # location to store file
        print(destination_file_path)
    async with aiofiles.open(destination_file_path, 'wb') as out_file:
        while content := await file.read():  # async read file chunk
            await out_file.write(content)  # async write file chunk
        # for windows need to pass tesseract_cmd parameter to setup your tesseract command path.
        reader = PersonalCard(lang=Language.MIX, provider=Provider.TESSERACT)
        result = reader.extract_front_info(destination_file_path)
        os.remove(destination_file_path)
        return {"identification_number": result.Identification_Number}
