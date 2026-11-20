import asyncio

from app.ai.client import generate_answer


async def main():

    messages = [
        {
            "role": "system",
            "content": "你是一名擅长科普写作的中文作者。",
        },
        {
            "role": "user",
            "content": (
                "请用100字以内介绍人工智能，"
                "要求语言生动，让大学生容易理解。"
            ),
        },
    ]

    for temperature in [0.2, 0.7, 1.2]:

        print(f"\n========== Temperature={temperature} ==========")

        answer = await generate_answer(
            messages,
            temperature=temperature,
        )

        print(answer)


if __name__ == "__main__":
    asyncio.run(main())