import asyncio

from synchronizer.poller import group_consecutive_albums, pick_canonical_message


class FakeMessage:
    def __init__(self, id, grouped_id=None, text=None):
        self.id = id
        self.grouped_id = grouped_id
        self.text = text


async def async_iter(items):
    for item in items:
        yield item


async def collect_groups(messages):
    return [group async for group in group_consecutive_albums(async_iter(messages))]


def group(messages):
    return asyncio.run(collect_groups(messages))


def test_ungrouped_messages_each_become_their_own_group():
    messages = [FakeMessage(1), FakeMessage(2), FakeMessage(3)]

    assert group(messages) == [[messages[0]], [messages[1]], [messages[2]]]


def test_consecutive_same_grouped_id_messages_become_one_group():
    messages = [FakeMessage(1, grouped_id=100), FakeMessage(2, grouped_id=100), FakeMessage(3, grouped_id=100)]

    assert group(messages) == [messages]


def test_album_followed_by_ungrouped_message_splits_into_two_groups():
    messages = [FakeMessage(1, grouped_id=100), FakeMessage(2, grouped_id=100), FakeMessage(3)]

    assert group(messages) == [[messages[0], messages[1]], [messages[2]]]


def test_two_different_albums_back_to_back_stay_separate():
    messages = [FakeMessage(1, grouped_id=100), FakeMessage(2, grouped_id=200)]

    assert group(messages) == [[messages[0]], [messages[1]]]


def test_pick_canonical_message_prefers_the_one_with_text():
    captioned = FakeMessage(2, grouped_id=100, text="caption")
    members = [FakeMessage(1, grouped_id=100), captioned, FakeMessage(3, grouped_id=100)]

    assert pick_canonical_message(members) is captioned


def test_pick_canonical_message_falls_back_to_first_when_none_have_text():
    members = [FakeMessage(1, grouped_id=100), FakeMessage(2, grouped_id=100)]

    assert pick_canonical_message(members) is members[0]
