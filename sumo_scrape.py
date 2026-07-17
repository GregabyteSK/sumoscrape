import requests
import json
import subprocess
import datetime
import os
from pathlib import Path

from bs4 import BeautifulSoup

url_date = datetime.datetime.now().strftime('%Y%m')
base_url = "https://www3.nhk.or.jp"
index_url = f"{base_url}/nhkworld/en/tv/sumo/tournament/{url_date}/index.json"

def main():
    Path(url_date).mkdir(exist_ok=True)
    r = requests.get(str(index_url))
    for day in json.loads(r.content)["items"]:
        try:
            vod_id = get_vod_id(f"{base_url}{day['url']}")
            vod_json = requests.get(f"https://api.nhkworld.jp/showsapi/v1/en/video_episodes/{vod_id}")
            video_url = json.loads(vod_json.content)["video"]["url"]
            print(f"Found video: {day['title']}")
            filename = os.path.join(url_date, f'{day["title"]}.mp4')
            if not Path(filename).exists():
                if save_video(video_url, filename):
                    print(f"File saved at {filename}")
                else:
                    print(f"Error while saving {filename}")
            else:
                print(f"File found at {filename}, skipping")
        except:
            pass

def get_vod_id(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    for i in soup.find_all('a'):
        if i.has_attr('data-vod'):
            return i.attrs['data-vod'].replace('-','')

def save_video(url, filename):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
    command = f'ffmpeg -i {url} -user_agent "{user_agent}" -c copy "{filename}"'
    subprocess.call(command, shell=True)
    path = Path(filename)
    return path.is_file() & path.stat().st_size > 0

if __name__ == "__main__":
    main()