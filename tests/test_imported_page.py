from pathlib import Path
from xml.etree.ElementTree import Element

import numpy
import pytest

from qurator.eynollah.imported_page import ImportedPage

testdir = Path(__file__).parent.resolve()


@pytest.fixture
def imported_page():
    return ImportedPage(testdir.joinpath('resources', 'DDD_010411958_002.page.xml'))


def test_imported_page(imported_page):
    assert imported_page.tree is not None


def test_get_dimensions(imported_page):
    assert imported_page.get_dimensions()[0] == 1898
    assert imported_page.get_dimensions()[1] == 3188


def test_get_all_regions_as_np_mask(imported_page):
    mask = imported_page.get_all_regions_as_np_mask(1600, 300)

    assert type(mask) == numpy.ndarray
    assert mask.shape == (300, 1600, 3)


def test_get_regions_data(imported_page):
    imported_page.set_regions_data()
    data = imported_page.get_regions_data()

    assert len(data) == 8
    assert data[0]['id'] == 'P2_TB00001'


def test_get_region_trees(imported_page):
    tree_list = imported_page.get_region_trees()
    assert type(tree_list) == list
    assert type(tree_list[0]) == Element


def test_get_metadata_tree(imported_page):
    imported_page.set_metadata()
    metadata = imported_page.get_metadata_tree()
    assert type(metadata) == Element


def test_get_metadata_comments(imported_page):
    comments = imported_page.get_metadata_comments()
    assert comments.endswith('Eynollah')


def test_get_matching_region_from_coords(imported_page):
    region = imported_page.get_matching_region_from_coords('30,35 944,35 944,1575 30,1575')
    assert region['id'] == 'P2_TB00001'

    should_fail = imported_page.get_matching_region_from_coords('50,1500 50,1600 900,1600 900,1600')
    assert should_fail is None


def test_get_coords_as_tuples(imported_page):
    region = imported_page.get_matching_region_from_coords('30,35 944,35 944,1575 30,1575')
    coords = region['coords_as_tuples']
    assert type(coords) == list
    assert type(coords[0]) == tuple
    assert coords == [(30, 35), (944, 35), (944, 1575), (30, 1575)]
