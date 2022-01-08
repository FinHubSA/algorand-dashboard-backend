FROM python:3.9.9
# a non-null PYTHONUNBUFFERED ensures that python 
# output is sent straight to the terminal without 
# being buffered. It helps in debugging.
ENV PYTHONUNBUFFERED 1

# the frontend will be in /app/frontend
WORKDIR /app/backend
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . ./
EXPOSE 8000