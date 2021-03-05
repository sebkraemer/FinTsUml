import pytest
from fints_uml import filter_hbci

ESCAPE_CHAR = b'.'

def __int_to_binary_char__(char_as_ord):
    """converts ordinal char represenation to binary string, e.g. b'x'.
    It is used for parametrized test because the chars are passed as integers.
    """
    return chr(char_as_ord).encode()

def test_whitespace_unchanged():
    whitspace_chars = b'\r\n'
    assert filter_hbci(whitspace_chars) == whitspace_chars

@pytest.mark.parametrize(
    "alphanumeric_char",
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
)
def test_alphanumeric_valid(alphanumeric_char):
    alphanumeric_char_b = alphanumeric_char.encode()
    assert filter_hbci(alphanumeric_char_b) == alphanumeric_char_b

@pytest.mark.parametrize(
    "special_char",
    b'!"#$%&()*+,-./[\\]^_\x7B\x7D\xA7',
)
def test_valid_special_signs(special_char):
    the_char = __int_to_binary_char__(special_char)
    assert filter_hbci(the_char) == the_char

def test_umlauts_valid():
    umlaut_chars = b'\xC4\xE4\xD6\xF6\xDC\xFC\xDF' # äÄüÜöÖß
    assert filter_hbci(umlaut_chars) == umlaut_chars

@pytest.mark.skip(reason="not implemented")
def test_pipe_invalid():
    assert filter_hbci(b'|') == ESCAPE_CHAR


@pytest.mark.skip(reason="not implemented")
def test_tilde_invalid():
    assert filter_hbci(b'~') == ESCAPE_CHAR
