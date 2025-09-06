import requests
import json
import time
from tqdm import trange

# https://api.jikan.moe/v4/

def get_top_characters(pages=10):
    for page in trange(1, pages + 1):
        r = requests.get(f"https://api.jikan.moe/v4/top/characters?page={page}")
        data = r.json()["data"]

        for character in data:
            yield {
                "mal_id": character["mal_id"],
                "name": character["name"],
                "description": character["about"]
            }
        
        time.sleep(1)


def main():
    for character in get_top_characters(50):
        if len(character["description"]) < 500:
            continue

        with open("anime_characters.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(character, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
