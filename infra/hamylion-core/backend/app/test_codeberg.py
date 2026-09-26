from .codeberg import parse_codeberg_rss


def test_parse_codeberg_release_and_commit():
    xml = """<rss><channel>
      <item><title>durian выпуск 0.2.30</title><link>https://codeberg.org/durian/tiny-moments/releases/tag/0.2.30</link><guid>83404022</guid><author>durian</author><pubDate>Wed, 24 Dec 2025 11:33:08 +0100</pubDate></item>
      <item><title>durian изменения отправлены в main</title><link>https://codeberg.org/durian/tiny-moments/commit/abc</link><guid>83403914</guid><author>durian</author><pubDate>Wed, 08 Oct 2025 15:42:15 +0200</pubDate></item>
    </channel></rss>"""
    events = parse_codeberg_rss(xml)
    assert [e["type"] for e in events] == [
        "codeberg.release.published",
        "codeberg.commit.pushed",
    ]
    assert events[0]["payload"]["repository"] == "durian/tiny-moments"
    assert events[0]["idempotency_key"].startswith("codeberg:")


def test_codeberg_guid_is_idempotent_key():
    xml = """<rss><channel><item>
      <title>release</title><link>https://codeberg.org/a/b/releases/tag/1</link>
      <guid>same-guid</guid><pubDate>Wed, 24 Dec 2025 11:33:08 +0100</pubDate>
    </item></channel></rss>"""
    a = parse_codeberg_rss(xml)
    b = parse_codeberg_rss(xml)
    assert a[0]["idempotency_key"] == b[0]["idempotency_key"]
