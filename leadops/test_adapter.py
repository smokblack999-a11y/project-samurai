from telegram_adapter import normalize_update


def test_update_new_message_normalizes():
    event = normalize_update({"@type":"updateNewMessage","message":{"id":7,"chat_id":9,"sender_id":{"user_id":11},"content":{"@type":"messageText","text":{"text":"Хочу купить сегодня"}}}})
    assert event is not None
    assert event.event_id == "tg:9:7"
    assert event.chat_id == "9"
    assert event.message_id == "7"
    assert event.sender_id == "11"


def test_non_text_update_is_ignored():
    assert normalize_update({"@type":"updateNewMessage","message":{"content":{"@type":"messagePhoto"}}}) is None
