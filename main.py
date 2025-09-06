import requests
import json
from tqdm import tqdm
import time


system_prompt = "You are an AI assistant that generates character cards from unstructured information."
user_prompt = """Generate a character card with the same format as the following example:

Example:
```
{
    "name": "Hu Tao",
    "personality": "Hu Tao is lively, playful, and mischievous, always ready with a prank or a clever remark. She loves poetry and often speaks in riddles or verses, mixing humor with deeper meaning. While she can come across as eccentric or even a little spooky, beneath it all she’s compassionate and thoughtful, treating matters of death with genuine respect. In roleplay, she’s best portrayed as someone who shifts easily between lighthearted teasing and wise, almost philosophical reflection.",
    "description": "Hu Tao is the 77th Director of the Wangsheng Funeral Parlor in Liyue, responsible for carrying out funeral rites and guiding souls to rest. She has a unique style that mixes tradition with her own flair—often seen wearing her signature dark outfit with red plum blossoms and butterflies, symbols of life and death. Despite her young age, she takes her duties seriously and has earned respect for honoring the cycle of life with both care and artistry."
}
```

Guidelines:
- If information about physical appearance is missing, it may be omitted.
- If information about personality is missing, write a fitting description of the character's personality that fits with their information.

Character Information:
Name: {{CHARACTER_NAME}}
Information:
{{CHARACTER_INFORMATION}}"""

with open("anime_characters.jsonl", "r", encoding="utf-8") as f:
    anime_chars = [json.loads(line) for line in f.readlines()]


def main():
    for character in tqdm(anime_chars[595:]):
        r = requests.post(
            "https://ai.hackclub.com/chat/completions",
            json={
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": user_prompt.replace(
                            "{{CHARACTER_NAME}}", character["name"]
                            ).replace("{{CHARACTER_INFORMATION}}", character["description"])
                    }
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "character_card",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "personality": {"type": "string"},
                                "description": {"type": "string"}
                            },
                            "required": ["name", "personality", "description"],
                            "additionalProperties": False
                        }
                    }
                },
                "include_reasoning": False,
                "temperature": 1,
            },
            headers={"Content-Type": "application/json"}
        )

        raw_result = r.json()["choices"][0]["message"]["content"]
        result = json.loads(raw_result)

        with open("character_cards.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        time.sleep(3)


if __name__ == "__main__":
    main()
