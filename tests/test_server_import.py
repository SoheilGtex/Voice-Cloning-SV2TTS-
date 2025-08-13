def test_import_server():
    import voice_cloner.server as s
    assert hasattr(s, "app")
