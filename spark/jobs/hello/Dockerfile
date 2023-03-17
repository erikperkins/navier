FROM erikperkins/spark:3.3.2
USER root
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY main.py .
