FROM python

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True


# Copy local code to the container image.
ENV APP_HOME=/app
WORKDIR $APP_HOME
COPY . ./

RUN pip install -r requirements.txt

RUN mkdir darknet
RUN wget https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names -P darknet \
  && wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg -P darknet \
  && wget -q https://pjreddie.com/media/files/yolov3.weights -P darknet

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 app:app
