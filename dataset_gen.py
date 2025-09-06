import json
from random import shuffle, randint
from tqdm import tqdm
import anthropic


# NOTE: First 47 conversations use Claude Sonnet 4, onwards is Claude Opus 4.1


with open("prompt.txt", "r") as f:
    prompt = f.read()

with open("character_cards.jsonl", "r", encoding="utf-8") as f:
    cards = [json.loads(line) for line in f.readlines()]
    shuffle(cards)
    cards = [(cards[i], cards[i + 1]) for i in range(0, len(cards), 2)]


def generate_conversation(client, char_a, char_b, max_turns=20):
    prompt_a = (
        prompt.replace("{{CHARACTER_NAME}}", char_a["name"])
        .replace("{{CHARACTER_PERSONALITY}}", char_a["personality"])
        .replace("{{CHARACTER_DESCRIPTION}}", char_a["description"])
        .replace("{{USER_NAME}}", char_b["name"])
    )

    prompt_b = (
        prompt.replace("{{CHARACTER_NAME}}", char_b["name"])
        .replace("{{CHARACTER_PERSONALITY}}", char_b["personality"])
        .replace("{{CHARACTER_DESCRIPTION}}", char_b["description"])
        .replace("{{USER_NAME}}", char_a["name"])
    )

    conversation = []

    messages_a = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt_a
                    + f"\n\nStart off by greeting {char_b['name']} in a way that fits your character.",
                    "cache_control": {"type": "ephemeral"},
                }
            ],
        }
    ]

    messages_b = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt_b,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
        }
    ]

    current_speaker = "A"

    for turn in range(max_turns):
        try:
            if current_speaker == "A":
                response = client.messages.create(
                    model="claude-opus-4-1-20250805",
                    max_tokens=300,
                    messages=messages_a,
                    temperature=0.8,
                )

                message_content = response.content[0].text
                conversation.append(
                    {
                        "speaker": char_a["name"],
                        "message": message_content,
                        "turn": turn + 1,
                    }
                )

                messages_b.append(
                    {"role": "user", "content": f"{char_a['name']}: {message_content}"}
                )

                current_speaker = "B"

            else:
                response = client.messages.create(
                    model="claude-opus-4-1-20250805",
                    max_tokens=300,
                    messages=messages_b,
                    temperature=0.7,
                )

                message_content = response.content[0].text
                conversation.append(
                    {
                        "speaker": char_b["name"],
                        "message": message_content,
                        "turn": turn + 1,
                    }
                )

                messages_a.append(
                    {
                        "role": "assistant",
                        "content": (
                            messages_a[-1]["content"]
                            if turn == 0
                            else conversation[-2]["message"]
                        ),
                    }
                )
                messages_a.append(
                    {"role": "user", "content": f"{char_b['name']}: {message_content}"}
                )

                current_speaker = "A"

        except Exception as e:
            print(f"Error generating turn {turn + 1}: {e}")
            break

    return conversation


def save_conversation(conversation, char_a, char_b, filename="conversations.jsonl"):
    conversation_data = {
        "character_a": char_a["name"],
        "character_b": char_b["name"],
        "character_a_info": {
            "personality": char_a["personality"],
            "description": char_a["description"],
        },
        "character_b_info": {
            "personality": char_b["personality"],
            "description": char_b["description"],
        },
        "conversation": conversation,
        "total_turns": len(conversation),
    }

    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(conversation_data, ensure_ascii=False) + "\n")


def main():
    client = anthropic.Anthropic()

    for i, (char_a, char_b) in tqdm(enumerate(cards)):
        print(
            f"Generating conversation {i+1}/{len(cards)}: {char_a['name']} x {char_b['name']}"
        )

        try:
            conversation = generate_conversation(client, char_a, char_b, max_turns=randint(5, 30))
            save_conversation(conversation, char_a, char_b)

            print(f"  Generated {len(conversation)} turns")

        except Exception as e:
            print(f"  Failed to generate conversation: {e}")
            continue

    print("All conversations generated and saved to conversations.jsonl")


if __name__ == "__main__":
    main()
