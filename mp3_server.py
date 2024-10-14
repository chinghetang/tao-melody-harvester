from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn

app = FastAPI()

# 設置MP3文件的目錄
MP3_DIR = Path("downloads")  # 假設MP3文件存放在 'downloads' 目錄

# 掛載靜態文件目錄
app.mount("/static", StaticFiles(directory="downloads"), name="static")

@app.get("/")
async def read_root():
    # 獲取所有MP3文件
    mp3_files = [f for f in MP3_DIR.glob("*.mp3")]
    
    # 生成HTML內容
    html_content = """
    <html>
        <head>
            <title>MP3 下載列表</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                ul { list-style-type: none; padding: 0; }
                li { margin-bottom: 10px; }
                a { color: #1a73e8; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>可用的MP3文件</h1>
            <ul>
    """
    
    for mp3 in mp3_files:
        html_content += f'<li><a href="/download/{mp3.name}">{mp3.name}</a></li>'
    
    html_content += """
            </ul>
        </body>
    </html>
    """
    
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = MP3_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename, media_type='audio/mpeg')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)