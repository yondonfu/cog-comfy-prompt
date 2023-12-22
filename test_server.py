from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/")
def read_root():
    return "Hello World!"

@app.get("/file/{filename}")
def read_file(filename: str):
    file_path = f"files/{filename}"
    try:
        return FileResponse(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, details="File not found")

@app.put("/file/{filename}")
def put_file(filename: str, file: UploadFile):
    file_path = f"files/{filename}"
    with open(file_path, "wb+") as f:
        f.write(file.file.read())

    return { "filename": filename }