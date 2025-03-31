import cv2
import numpy as np
import json
import statistics
from configuration import *

class Fly:
    def __init__(self, x: float, y: float, size: float):
        self.x = x
        self.y = y
        self.size = size
        self.moved = False
        self.contour = None

class Arena:
    def __init__(self):
        self.flies = []
        self.flies_counted = 0
        self.fly_count_error = 0
        self.flies_moved = 0
        self.flies_moved_percentage = 0.0
        self.contours_counted = 0
        self.average_cluster_size = 0.0
        self.median_cluster_size = 0.0
        self.cluster_sizes = []

    def calculate(self):
        self.contours_counted = len(self.flies)
        self.flies_counted = 0

        for fly in self.flies:
            cluster_size = fly.size / EXPECTED_FLY_AREA
            self.cluster_sizes.append(cluster_size)
            self.flies_counted += cluster_size
    
        self.average_cluster_size = statistics.mean(self.cluster_sizes)
        self.median_cluster_size = statistics.median(self.cluster_sizes)

        self.fly_count_error = EXPECTED_FLY_COUNT - self.flies_counted
        self.flies_moved = sum([fly.moved for fly in self.flies])
        self.flies_moved_percentage = self.flies_moved / self.flies_counted if self.flies_counted > 0 else None


class Frame:
    def __init__(self, date, time, image_id):
        self.arenas: Arena = []
        self.flies_counted = 0
        self.fly_count_error = 0
        self.flies_moved = 0
        self.date = date
        self.time = time
        self.image_id = image_id
        self.flies_moved_percentage = 0.0
        self.contours_counted = 0
        self.average_cluster_size = 0.0
        self.median_cluster_size = 0.0

    def calculate(self):
        self.flies_counted = sum([arena.flies_counted for arena in self.arenas])
        self.fly_count_error = (EXPECTED_FLY_COUNT * len(ARENAS) - self.flies_counted)
        self.flies_moved = sum([arena.flies_moved for arena in self.arenas])
        self.flies_moved_percentage = self.flies_moved / self.flies_counted if self.flies_counted > 0 else None
        self.contours_counted = sum([arena.contours_counted for arena in self.arenas])
        self.average_cluster_size = statistics.mean([x for arena in self.arenas for x in arena.cluster_sizes])
        self.median_cluster_size = statistics.median([x for arena in self.arenas for x in arena.cluster_sizes])

class FlyEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

class Processor:
    def __init__(self, background_image, arenas):
        self.background_image = background_image
        self.arenas = arenas

    def setup(self):
        pass

    def process_raw(self, image):
        pass

    def process_image(self, image, image_data):
        pass

    def is_point_in_arena(self, pos:tuple, arena):
        radius = arena.size/2
        return np.pow(pos[0]- arena.pt[0], 2) + np.pow(pos[1] - arena.pt[1], 2) < (radius * radius)

    def find_arena_from_pos(self, pos: tuple):
        for arena in self.arenas:
            if self.is_point_in_arena(pos, arena):
                return self.arenas.index(arena)
        return -1

class ContourProcessor(Processor):
    def __init__(self, background_image, arenas, image_threshold, min_contour_area, max_contour_area):
        Processor.__init__(self, background_image, arenas)
        self.image_threshold = image_threshold
        self.min_contour_area = min_contour_area
        self.max_contour_area = max_contour_area
    
    def getAveragePositionFromContour(self, contour):
        pos = (0, 0)
        for point in contour:
            pos = pos + point[0]
        return (pos / len(contour))
    
    def doesEntireContourFitInArena(self, contour, arena):
        for point in contour:
            if not self.is_point_in_arena(point[0], arena):
                return False
            
        return True
    
    def process_raw(self, image):
        subtracted = cv2.absdiff(self.background_image, image)
        _, binarized = cv2.threshold(cv2.cvtColor(subtracted, cv2.COLOR_RGB2GRAY), self.image_threshold, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binarized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        return contours, binarized


    def process_image(self, data, image_data):
        frame = Frame(image_data[0], image_data[1], image_data[2])

        for arena in self.arenas:
            frame.arenas.append(Arena())

        for contour in data:
            avg_pos = self.getAveragePositionFromContour(contour)
            area = cv2.contourArea(contour)

            if area > self.min_contour_area and area < self.max_contour_area:
                arena = self.find_arena_from_pos(avg_pos)
                if arena != -1 and self.doesEntireContourFitInArena(contour, ARENAS[arena]):
                    fly = Fly(avg_pos[0], avg_pos[1], area)
                    fly.contour = contour
                    frame.arenas[arena].flies.append(fly) 
        
        for arena in frame.arenas:
            arena.calculate()

        frame.calculate()

        return frame

    def perform_last_frame_analysis(self, last_image, image, last: Frame, current: Frame):
        rem_bg_last = cv2.absdiff(self.background_image, last_image)
        rem_bg_curr = cv2.absdiff(self.background_image, image)
        _, binarized_last = cv2.threshold(cv2.cvtColor(rem_bg_last, cv2.COLOR_RGB2GRAY), self.image_threshold, 255, cv2.THRESH_BINARY)
        _, binarized_curr = cv2.threshold(cv2.cvtColor(rem_bg_curr, cv2.COLOR_RGB2GRAY), self.image_threshold, 255, cv2.THRESH_BINARY)
        
        binarized = binarized_last * binarized_curr

        contours, _ = cv2.findContours(binarized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # test = cv2.cvtColor(binarized_last, cv2.COLOR_GRAY2BGR)* (1,0,0)
        # test2 = cv2.cvtColor(binarized_curr, cv2.COLOR_GRAY2BGR)* (0,1,0)


        # cv2.imshow("prev", last_image)
        # cv2.imshow("curr", image)
        # # cv2.imshow("subtr", binarized)
        # # # cv2.waitKey()
        # # # exit()

        # test = cv2.drawContours(cv2.cvtColor(np.copy(binarized), cv2.COLOR_GRAY2BGR), contours, -1, (0,255,255), cv2.FILLED)
        # cv2.imshow("contours found", test)
        # cv2.waitKey()
        # exit()

        contour_data = []
        moved_contours = []

        for contour in contours:
            avg_pos = self.getAveragePositionFromContour(contour)
            contour_data.append((avg_pos[0], avg_pos[1], cv2.contourArea(contour)))

        arena: Arena
        for arena in current.arenas:
            fly: Fly
            for fly in arena.flies:
                fly.moved = True
                for x in range(len(contour_data)):
                    contour = contour_data[x]
                    if isPointClose(fly.x, fly.y, contour[0], contour[1], FLY_MATCH_CI): #and (contour[2] - FLY_MATCH_SIZE_CI < fly.size and contour[2] + FLY_MATCH_CI > fly.size):
                        fly.moved = False
                        break
            arena.calculate()
        current.calculate()

        return moved_contours

def isPointClose(ax, ay, bx, by, error):
    return (ax < bx + error and ax > bx - error and ay < by + error and ay > by - error)