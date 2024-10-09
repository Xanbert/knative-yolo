#change constant in here
import os

classesfile = "/home/app/darknet/coco.names"
configfile = "/home/app/darknet/yolov3.cfg"
weightfile = "/home/app/darknet/yolov3.weights"

REDIS_HOST = os.getenv("redis")
REDIS_PORT = "6379"

MONGO_HOST = os.getenv("mongo")
MONGO_PORT = "27017"
