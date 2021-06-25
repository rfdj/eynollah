from xml.etree import ElementTree

import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon


class ImportedPage:
    """
    The ImportedPage is a PAGE-xml file that contains text region data from a previous processing step.
    In Eynollah the regions are then used as boundaries for the text line detection. The results of that detection are
    merged with this region data already available in the imported page.
    """

    regions_data = {}
    metadata = {}

    def __init__(self, xml_uri):
        self.xml_uri = xml_uri
        self.tree = ElementTree.parse(self.xml_uri)

        self.set_regions_data()
        self.page_width, self.page_height = self.get_dimensions()
        self.set_metadata()

    def get_all_regions_as_np_mask(self, width, height):
        """
        Returns an np array of a mask consisting of all text regions on the page.
        """
        img = Image.new('L', (self.page_width, self.page_height), 0).convert('RGB')

        for region in self.regions_data:
            coords_list = region['coords_as_tuples']
            ImageDraw.Draw(img).polygon(coords_list, outline=1, fill=1)

        img = img.resize((width, height))

        mask = np.asarray(img)
        mask = mask.copy()

        return mask

    def get_dimensions(self):
        width = self.tree.find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Page').attrib[
            'imageWidth']
        height = self.tree.find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Page').attrib[
            'imageHeight']
        return int(width), int(height)

    def set_regions_data(self):
        region_trees = self.get_region_trees()
        all_data = []
        for region in region_trees:
            data = {
                'id': region.attrib['id'],
                'coords': get_coords_tree(region),
                'coords_as_tuples': get_coords_as_tuples_from_region(region),
                'type': region.attrib['type'],
                'textEquiv': get_text_equiv_unicode(region),
                'tree': region
            }
            all_data.append(data)

        self.regions_data = all_data

    def get_regions_data(self):
        return self.regions_data

    def get_region_trees(self):
        return self.tree.findall('*//{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextRegion')

    def set_metadata(self):
        metadata_orig = self.tree.find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Metadata')
        comments = metadata_orig.find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Comments')
        comments.text = comments.text + '\n\t\t\tReading order and text line analyses: Eynollah'
        self.metadata = metadata_orig

    def get_metadata_tree(self):
        return self.metadata

    def get_metadata_comments(self):
        return self.get_metadata_tree().find(
            '{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Comments').text

    def get_matching_region_from_coords(self, coords):

        for region in self.get_regions_data():
            coords_list = coords.split(' ')
            region_coords_list = region['coords_as_tuples']

            is_matching_region = check_if_coords_match_with_region_coords(coords_list, region_coords_list)

            if is_matching_region:
                return region

        return None


def check_if_coords_match_with_region_coords(coords_list, region_coords_list):
    coords_polygon = Polygon([tuple([int(x) for x in coord.split(',')]) for coord in coords_list])
    region_polygon = Polygon(region_coords_list)

    return coords_polygon.intersection(region_polygon).area / coords_polygon.area > 0.95


def get_coords_tree(region):
    return region.find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Coords')


def get_coords_as_tuples_from_region(region):
    points = get_coords_tree(region).attrib['points']
    coords_list = [tuple([int(coord) for coord in xy.split(',')]) for xy in points.split(' ')]
    return coords_list


def get_text_equiv_unicode(region):
    text_equiv = region.find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}TextEquiv')
    return text_equiv.find('{http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15}Unicode')
