def get_cursor_word(code: str, cursor_pos: int) -> tuple[str, int]:
    """Return word under cursor as well as its index in `code.split()`.

    Args:
        code (str): The user's code.
        cursor_pos (int): The cursor's position in *code*.

    Returns:
        tuple[str, int]: Word under cursor and its position in `code.split()`
    """
    word_end = 0
    segments = code.replace("\n", " ").split(" ")
    for index, segment in enumerate(segments):
        word_end += len(segment)
        if cursor_pos <= word_end:
            cursor_word = segment
            word_index = index
            break
        # Space after segment
        word_end += 1

    return cursor_word, word_index


def get_cursor_words(code: str, cursor_pos: int) -> tuple[str, str | None]:
    """Return relevant information regarding the cursor and its environment.

    Args:
        code (str): The user's code.
        cursor_pos (int): The cursor's position in *code*.

    Returns:
        tuple[str, str | None]: Word under cursor and if present the word left of it (`None` if not present).
    """
    word, word_index = get_cursor_word(code, cursor_pos)

    segments = code.split(" ")

    relevant = segments[:word_index]
    left_word = next((s for s in relevant[::-1] if not s.strip() == ""), None)
    return word, left_word


def get_cursor_frame(code: str, cursor_pos: int) -> tuple[int, int]:
    """Return start and end index of word under cursor in *code*.

    Args:
        code (str): The user's code.
        cursor_pos (int): The cursor's position in *code*.

    Returns:
        tuple[int, int]: Start end end index of word under cursor.
    """
    word, word_index = get_cursor_word(code, cursor_pos)
    segments = code.replace("\n", " ").split(" ")
    relevant = segments[:word_index]
    start = len(" ".join(relevant))
    start = start if word_index == 0 else start + 1
    end = start + len(word)
    return start, end


def get_first_word(code: str) -> str | None:
    """Return first non-empty word in *code*.

    Args:
        code (str): The user's code.

    Returns:
        str | None: First non-empty word or `None` if not present.
    """
    return code.lstrip().split(" ")[0]


def get_line_start(code: str, cursor_pos: int) -> str | None:
    """Return first non-empty word in the line the cursor is placed in.

    Args:
        code (str): The user's code.
        cursor_pos (int): The cursor's position in *code*.

    Returns:
        str | None: First non-empty word in the line the cursor is placed in or `None` if not present.
    """
    lines = []
    lines = code.split("\n")
    for line in lines:
        if cursor_pos in range(len(line) + 1):
            return line.lstrip().split(" ")[0]
        cursor_pos -= len(line) + 1
    return None
