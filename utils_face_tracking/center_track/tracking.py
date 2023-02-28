# import the necessary packages
from pickle import TRUE
from scipy.spatial import distance as dist
from collections import OrderedDict
from utils_face_tracking.center_track.face_obj import Face
import numpy as np
from utils import feature_extraction
from utils import crop_face
import math
from config.config import MAX_DISSAPPEARED, MIN_DISTANCE_RATIO, MIN_SIM_TO_SAVE

class CentroidTracker():
    def __init__(self, landmark_model, extract_model, out_size):
        self.width = None
        self.height = None
        self.frame = None
        # initialize the next unique object ID
        self.nextObjectID = 0
        #  {ID: (center_x, center_y)}
        self.trackedObjects = OrderedDict()
        # {ID: times_disappeared}
        self.disappeared = OrderedDict()
        # Maximum consecutive frames a given object is allowed
        self.maxDisappeared = MAX_DISSAPPEARED
        # Create faces object
        self.faces = {}
        self.roi_para = None
        self.landmark_model = landmark_model
        self.extract_model = extract_model
        self.out_size = out_size

    def allocate_face(self, rect):
        cropped, new_bbox = crop_face(self.frame, rect)
        face = Face()
        face.best_img, face.feature = feature_extraction(self.frame, cropped, new_bbox, self.landmark_model, self.extract_model, self.out_size)
        return face

    # Add new centroid to the objects dictionary using the next available object ID
    def register(self, centroid, rect):
        if self.nextObjectID >= 1e4:
            self.nextObjectID = 0
        self.trackedObjects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        self.faces[self.nextObjectID] = self.allocate_face(rect)
        self.nextObjectID += 1

    # Deletes the objectID in both the objects and disappeared dictionaries
    def deregister(self, objectID):
        del self.trackedObjects[objectID]
        del self.disappeared[objectID]
        del self.faces[objectID]

    # update
    def update(self, rects):
        # If no face detected
        if len(rects) == 0:
            # mark existing tracked objects as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                # if we have reached a maximum number of consecutive frames deregister it
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
            # return early as there are no centroids or tracking info to update
            return self.trackedObjects

        # If had faces detected
        # initialize an array of input centroids for the CURRENT FRAME
        inputCentroids = np.zeros((len(rects), 2), dtype="int")
        meanWhs = np.zeros((len(rects), 1), dtype="int")

        # loop over the bounding box rectangles
        for (i, (startX, startY, endX, endY)) in enumerate(rects):
            # use the bounding box coordinates to derive the centroid
            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)
            inputCentroids[i] = (cX, cY)
            meanWhs[i] = ((endX - startX) + (endY - startY))//MIN_DISTANCE_RATIO

        # if we are currently not tracking any objects take the input centroids and register each of them
        if len(self.trackedObjects) == 0:
            for i in range(0, len(inputCentroids)):
                self.register(inputCentroids[i], rects[i])
        # match the input centroids to existing object centroids
        else:
            # current object IDs and centroids
            trackedIDs = list(self.trackedObjects.keys())
            trackedCentroids = list(self.trackedObjects.values())
            # compute the distance between each pair of object centroids and input centroids
            D = dist.cdist(np.array(trackedCentroids), inputCentroids)
            # in order to perform this matching we must (1) find the
            # smallest value in each row and then (2) sort the row
            # indexes based on their minimum values so that the row
            # with the smallest value is at the *front* of the index
            # list
            rows = D.min(axis=1).argsort()
            # next, we perform a similar process on the columns by
            # finding the smallest value in each column and then
            # sorting using the previously computed row index list
            cols = D.argmin(axis=1)[rows]

            usedRows = set()
            usedCols = set()
            # loop over the combination of the (row, column) index
            # tuples
            for (row, col) in zip(rows, cols):
                # if we have already examined either the row or
                # column value before, ignore it
                # val
                if row in usedRows or col in usedCols:
                    continue
                # otherwise, grab the object ID for the current row,
                # set its new centroid, and reset the disappeared
                # counter
                if not D[row][col] < meanWhs[col]:
                    print("Not same face", trackedIDs[row])
                    continue
                objectID = trackedIDs[row]
                self.trackedObjects[objectID] = inputCentroids[col]
                self.disappeared[objectID] = 0
                # if self.faces[objectID].best_img is None:
                if not self.faces[objectID].is_processed:
                    cropped, new_bbox = crop_face(self.frame, rects[col])
                    best_img, feature = feature_extraction(self.frame, cropped, new_bbox, self.landmark_model, self.extract_model, self.out_size)
                    # distance = 1
                    # if self.faces[objectID].feature is not None:
                    #     distance = np.sum((self.faces[objectID].feature - feature)**2)
                    #     self.faces[objectID].change = False
                    #     if distance >= MIN_SIM_TO_SAVE:
                    #         self.faces[objectID].best_img, self.faces[objectID].feature = best_img, feature
                    #         self.faces[objectID].change = True
                    # else:
                    self.faces[objectID].best_img, self.faces[objectID].feature = best_img, feature

                self.faces[objectID].center_y = inputCentroids[col][1]
                # indicate that we have examined each of the row and
                # column indexes, respectively
                usedRows.add(row)
                usedCols.add(col)
    
            # compute both the row and column index we have NOT yet
            # examined
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)
            
            # in the event that the number of object centroids is
            # equal or greater than the number of input centroids
            # we need to check and see if some of these objects have
            # potentially disappeared
            # if D.shape[0] >= D.shape[1]:
            # loop over the unused row indexes
            for row in unusedRows:
                # grab the object ID for the corresponding row
                # index and increment the disappeared counter
                objectID = trackedIDs[row]
                self.disappeared[objectID] += 1
                # check to see if the number of consecutive
                # frames the object has been marked "disappeared"
                # for warrants deregistering the object
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)

            # otherwise, if the number of input centroids is greater
            # than the number of existing object centroids we need to
            # register each new input centroid as a trackable object
            # else:
            for col in unusedCols:
                self.register(inputCentroids[col], rects[col])


        # return the set of trackable objects
        return self.trackedObjects
