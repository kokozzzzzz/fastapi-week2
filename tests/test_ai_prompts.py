from app.ai.prompts import (
    build_chat_messages,
    build_summary_messages,
    build_extract_messages,
)

# 测试chat
def test_build_chat_messages():
    messages = build_chat_messages("什么是Python？")

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == "什么是Python？"


# 测试summarize
def test_build_summary_messages():
    text = "这是一段测试文本。"

    messages = build_summary_messages(text)

    assert messages[0]["role"] == "system"
    assert text in messages[1]["content"]


# 测试0样本
def test_extract_zero_shot():
    text = "学校将于12月5日举办AI讲座。"

    messages = build_extract_messages(
        text,
        use_few_shot=False,
    )

    assert len(messages) == 2
    assert messages[-1]["role"] == "user"
    assert text in messages[-1]["content"]

# 测试少样本
def test_extract_few_shot():
    text = "学校将于12月5日举办AI讲座。"

    messages = build_extract_messages(
        text,
        use_few_shot=True,
    )

    assert len(messages) == 6

    assert messages[0]["role"] == "system"

    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"

    assert messages[3]["role"] == "user"
    assert messages[4]["role"] == "assistant"

    assert messages[5]["role"] == "user"
    assert text in messages[5]["content"]