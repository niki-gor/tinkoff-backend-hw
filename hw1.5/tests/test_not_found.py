import os


expected = """Not found
"""


def test_not_found(capfd):
    os.system('python -m tv_program.py asdfas  dlkfja  slkdfja')
    out, err = capfd.readouterr()

    assert out == expected


def test_empty(capfd):
    os.system('python -m tv_program.py')
    out, err = capfd.readouterr()

    assert out == expected
