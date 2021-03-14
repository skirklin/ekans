from ekans.snake import Snake
from ekans.window import VirtualWindow
from ekans.segment import Segment


def test_segment_list():
    w = VirtualWindow((20, 20))
    l = Snake(None, w)
    assert list(l) == []

    s = l.new_segment(0, 0)
    l.append(s)

    assert list(l) == [s]

    assert l[0] == s

    s2 = l.new_segment(0, 1)
    l.append(s2)

    assert list(l) == [s, s2]
    assert l[1] == s2

    s3 = l.new_segment(1, 0)

    l.insert(0, s3)

    assert list(l) == [s3, s, s2]
    assert l[0] == s3

    s4 = l.new_segment(2, 0)

    l.insert(1, s4)
    assert list(l) == [s3, s4, s, s2]

    l.remove(1)

    assert list(l) == [s3, s, s2]
