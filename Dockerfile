FROM resin/rpi-raspbian:jessie
# Install Python.
RUN apt-get update \
    && apt-get install -y python python-pip \
    # Remove package lists to free up space
    && rm -rf /var/lib/apt/lists/*

RUN pip install stomp.py==4.0.16

ADD . /app

CMD ["python", "/app/substation.py"]