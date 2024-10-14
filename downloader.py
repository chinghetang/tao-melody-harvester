import os
import json
import asyncio
import aiohttp
import yt_dlp

# 如果 ffmpeg 不在系統路徑中，請在這裡指定 ffmpeg 的完整路徑
FFMPEG_LOCATION = ""  # 例如："/path/to/ffmpeg" 或 "C:\\path\\to\\ffmpeg.exe"

async def fetch_json(session, url):
    async with session.get(url) as response:
        return await response.json()

async def download_youtube_as_mp3(video_id, title, output_path, max_retries=3):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
    }
    
    if FFMPEG_LOCATION:
        ydl_opts['ffmpeg_location'] = FFMPEG_LOCATION

    for attempt in range(max_retries):
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"正在下載 (嘗試 {attempt + 1}/{max_retries}): {title}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            print(f"下載完成: {title}")
            return os.path.join(output_path, f"{title}.mp3")
        except Exception as e:
            print(f"下載 {title} 時發生錯誤 (嘗試 {attempt + 1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                print(f"達到最大重試次數。下載 {title} 失敗。")
                return None
            await asyncio.sleep(2 ** attempt)  # 指數退避

async def process_json_data(json_url, output_path):
    async with aiohttp.ClientSession() as session:
        data = await fetch_json(session, json_url)
        
        tasks = []
        for video in data['data']:
            video_id = video['id']
            title = video['title']
            task = asyncio.ensure_future(download_youtube_as_mp3(video_id, title, output_path))
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
    
    for title, result in zip([v['title'] for v in data['data']], results):
        if result:
            print(f"文件 {title} 已成功下載")
        else:
            print(f"下載 {title} 最終失敗")

# 使用示例
json_url = "https://truth-gecko.web.app/data.json"
output_path = "downloads"

if not os.path.exists(output_path):
    os.makedirs(output_path)

asyncio.run(process_json_data(json_url, output_path))