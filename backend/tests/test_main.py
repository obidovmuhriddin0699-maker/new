def test_root_and_health(client) -> None:
    assert client.get("/").json() == {"message": "Local AI SaaS API"}
    assert client.get("/health").json() == {"status": "ok"}
