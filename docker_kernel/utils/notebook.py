def get_cursor_word(code: str, cursor_pos: int) -> tuple[str, int]:
    """Return word under cursor as well as its index in a split list of the code

    Parameters
    ----------
    code: str
        Code of the cell
    cursor_pos: int
        Position of cursor in code

    Returns
    -------
    tuple[word: str, word_index: int]
    """
    word_end = 0
    segments = code.split(" ")
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
    """Return relevant information regarding the cursor and its environment

    Parameters
    ----------
    code: str
        Code of the cell
    cursor_pos: int
        Position of cursor in code

    Returns
    -------
    tuple[word: str, left_word: str]

    word
        The word under the cursor
    left_word
        The next word left of the cursor word that not empty
    """
    word, word_index = get_cursor_word(code, cursor_pos)

    segments = code.split(" ")

    relevant = segments[:word_index]
    left_word = next((s for s in relevant[::-1] if not s.strip() == ""), None)
    return word, left_word

def get_cursor_frame(code: str, cursor_pos: int) -> tuple[int, int]:
    """Return start and end index of word under cursor

    Parameters
    ----------
    code: str
        Code of the cell
    cursor_pos: int
        Position of cursor in code

    Returns
    -------
    tuple[word: str, left_word: str]

    word
        The word under the cursor
    left_word
        The next word left of the cursor word that not empty
    """
    word, word_index = get_cursor_word(code, cursor_pos)

    segments = code.split(" ")
    relevant = segments[:word_index]
    start = len(" ".join(relevant))
    start = start if word_index == 0 else start + 1
    end = start + len(word)
    return start, end