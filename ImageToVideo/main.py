import os
import uuid
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from video_processor import create_video_from_images

app = FastAPI(title="Image to Video Demo")

UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = Path("static/index.html")
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Image to Video Demo</h1>")


@app.post("/api/upload")
async def upload_images(files: list[UploadFile] = File(...)):
    session_id = str(uuid.uuid4())[:8]
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    uploaded_files = []
    for file in files:
        if not file.content_type or not file.content_type.startswith("image/"):
            continue
        file_path = session_dir / file.filename
        content = await file.read()
        file_path.write_bytes(content)
        uploaded_files.append(file.filename)

    if not uploaded_files:
        raise HTTPException(status_code=400, detail="No valid image files uploaded")

    return {
        "session_id": session_id,
        "files": uploaded_files,
        "count": len(uploaded_files),
    }


@app.post("/api/generate")
async def generate_video(
    session_id: str = Form(...),
    fps: int = Form(1),
    duration_per_image: float = Form(2.0),
    output_format: str = Form("mp4"),
    transition: str = Form("none"),
):
    session_dir = UPLOAD_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")

    image_files = sorted(
        [f for f in session_dir.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    )
    if not image_files:
        raise HTTPException(status_code=400, detail="No images found in session")

    output_filename = f"video_{session_id}_{uuid.uuid4().hex[:6]}.{output_format}"
    output_path = OUTPUT_DIR / output_filename

    try:
        create_video_from_images(
            image_paths=image_files,
            output_path=output_path,
            fps=fps,
            duration_per_image=duration_per_image,
            transition=transition,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

    return {
        "video_url": f"/api/download/{output_filename}",
        "filename": output_filename,
    }


@app.get("/api/download/{filename}")
async def download_video(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        media_type="video/mp4",
        filename=filename,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
