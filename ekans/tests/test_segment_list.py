from ..snake import Snake
from ..segment import Segment

def test_segment_list():
    l = Snake(None)
    assert list(l) == []

    s = Segment(0, 0)
    l.append(s)

    assert list(l) == [s]

    assert l[0] == s

    s2 = Segment(0, 1)
    l.append(s2)

    assert list(l) == [s, s2]
    assert l[1] == s2

    s3 = Segment(1, 0)

    l.insert(0, s3)

    assert list(l) == [s3, s, s2]
    assert l[0] == s3

    s4 = Segment(2, 0)

    l.insert(1, s4)
    assert list(l) == [s3, s4, s, s2]

    l.remove(1)
    
    assert list(l) == [s3, s, s2]