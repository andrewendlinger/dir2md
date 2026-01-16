from dir2md.merge import estimate_tokens, is_binary


def test_token_estimation():
    # 4 chars = 1 token
    assert estimate_tokens("1234") == 1
    assert estimate_tokens("12345678") == 2
    # 0 chars = 0 tokens
    assert estimate_tokens("") == 0


def test_is_binary(tmp_path):
    # Create a text file
    text_file = tmp_path / "clean.txt"
    text_file.write_text("Hello World", encoding="utf-8")
    assert is_binary(text_file) is False

    # Create a binary file (contains null byte)
    bin_file = tmp_path / "program.exe"
    with open(bin_file, "wb") as f:
        f.write(b"Hello\x00World")
    assert is_binary(bin_file) is True
