import six

if six.PY3:
    # This is to silence pyflakes checker.
    unicode = str  # pylint: disable=redefined-builtin
    text_type = str
    binary_type = bytes
else:
    text_type = unicode
    binary_type = str
