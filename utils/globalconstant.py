#change constant in here
import os

darknet_dir = "./darknet"
classesfile = darknet_dir + "/coco.names"
configfile = darknet_dir + "/yolov3.cfg"
weightfile = darknet_dir + "/yolov3.weights"

REDIS_HOST = os.getenv("redis")
REDIS_PORT = "6379"

MONGO_HOST = os.getenv("mongo")
MONGO_PORT = "27017"
