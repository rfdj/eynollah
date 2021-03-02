from tests.base import main
from qurator.eynollah.utils.counter import EynollahIdCounter

def test_counter_string():
    c = EynollahIdCounter()
    assert c.next_region_id == 'region_0001'
    assert c.next_region_id == 'region_0002'
    assert c.next_line_id == 'region_0002_line_0001'
    assert c.next_region_id == 'region_0003'
    assert c.next_line_id == 'region_0003_line_0001'

def test_counter_init():
    c = EynollahIdCounter(region_idx=2)
    assert c.get('region') == 2

def test_counter_methods():
    c = EynollahIdCounter()
    assert c.get('region') == 0
    c.inc('region', 5)
    assert c.get('region') == 5
    c.set('region', 10)
    assert c.get('region') == 10
    c.inc('region', -9)
    assert c.get('region') == 1

if __name__ == '__main__':
    main(__file__)
