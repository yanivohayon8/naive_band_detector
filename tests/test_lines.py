import unittest
from src.bands import hough,two_points
from src.geometry import PolygonWrapper
import cv2
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import MultiPoint,Point
from src.loader import RdpDataloader


class TestHoughSimpleExamples(unittest.TestCase):

    simple_img_path = "data/images/simple_example.png"

    def test_lines_toy_example(self):
        img = cv2.imread(self.simple_img_path)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        edge_map = cv2.Canny(img,70,150)
        lines = hough.detect_hough_lines(edge_map,minimum_votes=75)

        assert len(lines) == 3

        for line in lines:
            points = line.sample_two_points(img.shape[:2])
            cv2.line(img,points[0],points[1],(0,0,255))

        plt.imshow(img)
        plt.close()
        pass

    def test_lines_randomly_toy_example(self):
        img = cv2.imread(self.simple_img_path)
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        edge_map = cv2.Canny(img,70,150)
        lines = hough.detect_hough_lines_randomly(edge_map,minimum_votes=75)
        
        for line in lines:
            cv2.line(img,line[0],line[1],(0,0,255))
            # point1,point2 = line.sample_two_points(distance=50)
            # cv2.line(img,point1,point2,(0,0,255))

        plt.imshow(img)
        plt.close()


    def test_lines_rpf_00333_bamboo(self):
        img = cv2.imread("data/images/RPf_00333_opposite_mesh_normals.png")
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        edge_map = cv2.Canny(img,150,300)

        #plt.imshow(edge_map,cmap="gray")
        lines = hough.detect_hough_lines(edge_map,minimum_votes=150)


        for line in lines:
            points = line.sample_two_points(img.shape)
            cv2.line(img,points[0],points[1],(0,255,0),thickness=2)

        fig, (ax1,ax2) = plt.subplots(1,2)
        ax1.imshow(edge_map,cmap="gray")
        ax2.imshow(img)
        plt.show()
        plt.close()

    def test_bands(self):
        img = cv2.imread(self.simple_img_path,0)
        lines = hough.detect_hough_lines(img,minimum_votes=400)
        band = hough.HoughBand(lines[0],lines[1])
        print(repr(band))
        print(band.get_width())

    def test_band_width(self):
        band = hough.HoughBand([
            hough.HoughLine(100,10),
            hough.HoughLine(100.01,20),
            hough.HoughLine(99.01,30),
        ])

        assert band.get_width() == 20




class TestTwoPointsLinesSimpleExamples(unittest.TestCase):
    simple_img_path = "data/images/simple_example.png"

    def run_toy_example(self,line_coords,polygon_coords):
        line = two_points.TwoPointsLine(line_coords[0],line_coords[1])
        polygon = PolygonWrapper(polygon_coords)

        # fig, (ax1,ax2) = plt.subplots(1,2)
        ax1 = plt.subplot()
        ax1.set_aspect('equal',adjustable="box")
        line.plot(ax1)
        polygon.plot(ax1)

        intersection = polygon.find_intersection(line.line_string)

        if isinstance(intersection,MultiPoint):
            intersection_points = [vertex for vertex in list(intersection.geoms)]
            intersection_x = [coord.x for coord in intersection_points]
            intersection_y = [coord.y for coord in intersection_points]
        if isinstance(intersection,Point):
            intersection_x,intersection_y = intersection.xy
        ax1.scatter(intersection_x, intersection_y, color='green', label='Intersection Points')
        
        edges = polygon.find_edges_touching_points(intersection)
        closest_x = []
        closest_y  = []

        for edge in edges:
            x,y = edge.xy
            closest_x= closest_x + x.tolist()
            closest_y= closest_y + y.tolist()

        ax1.scatter(closest_x, closest_y, color='purple', label='closest vertices')

        ax1.legend()
        print("Edges of polygon involved:")
        [print(edge,end=",  ") for edge in edges]
        print()
        print("Intersection: ",intersection)

        convex_hull = polygon.polygon.convex_hull
        convex_hull_x,convex_hull_y = convex_hull.exterior.xy
        convex_hull_x = convex_hull_x.tolist()
        convex_hull_y = convex_hull_y.tolist()
        plt.plot(convex_hull_x+[convex_hull_x[0]],convex_hull_y+[convex_hull_y[0]],color="blue",label="Convex Hull")

        plt.show()
        plt.close()

        return len(edges),len(intersection.geoms)

    def test_square_1(self):
        line_coords = [(600, 600), (-200, -100)]
        polygon_coords = [(0, 0), (0, 200), (200, 200), (200, 0)]
        self.run_toy_example(line_coords,polygon_coords)

    def test_square_2(self):
        line_coords = [(500, 600), (-200, -600)]
        polygon_coords = [(0, 0), (0, 200), (200, 200), (200, 0)]
        self.run_toy_example(line_coords,polygon_coords)

    def test_RPf_00368(self):
        csv_path = "data/rdp_segments/group_45/csv/RPf_00368_intact_mesh_rdp_10.csv"
        loader = RdpDataloader(csv_path)
        loader.load()
        polygon_coords = loader.get_polygon_coords()
        line_coords = [(0, 0), (1950, 2000)]
        self.run_toy_example(line_coords,polygon_coords)



if __name__ == "__main__":
    unittest.main()