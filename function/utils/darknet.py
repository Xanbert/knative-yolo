#https://github.com/pjreddie/darknet/wiki/YOLO:-Real-Time-Object-Detection
#https://www.arunponnusamy.com/yolo-object-detection-opencv-python.html

#adopt from : https://github.com/arunponnusamy/object-detection-opencv/blob/master/yolo_opencv.py
import cv2
import numpy as np

#classesfile = "coco.names" #https://github.com/pjreddie/darknet/blob/master/data/coco.names
#configfile = "yolov3.cfg" #https://github.com/pjreddie/darknet/tree/master/cfg/yolov3.cfg
#weightfile = "yolov3.weights" #wget https://pjreddie.com/media/files/yolov3.weights

scale = 0.00392
conf_threshold = 0.5
nms_threshold = 0.4

class Yolov3:
    def __init__(self,classesfile,configfile,weightfile):
        self.classes = None
        with open(classesfile , 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]
        self.COLORS = np.random.uniform(0, 255, size=(len(self.classes), 3))
        self.net = cv2.dnn.readNet(weightfile, configfile)

    def get_output_layers(self,net):
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return output_layers


    def draw_prediction(self,img, class_id, confidence, x, y, x_plus_w, y_plus_h):
        label = str(self.classes[class_id])
        color = self.COLORS[class_id]
        cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
        cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def detectImagefile(self,imagefile,outfile):
        image = cv2.imread(imagefile)
        Width = image.shape[1]
        Height = image.shape[0]
        outimage = self.detect(image,Width,Height)
        cv2.imwrite(outfile, outimage)

    #https://www.pyimagesearch.com/2018/02/26/face-detection-with-opencv-and-deep-learning/
    def detectFrame(self,frame):
        (Height, Width) = frame.shape[:2]
        return self.detect(frame,Width,Height)

    def detect(self,image,Width,Height):
        blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.get_output_layers(self.net))

        class_ids = []
        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])
        
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

        for i in indices:
            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            self.draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
        return image
