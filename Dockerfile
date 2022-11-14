FROM python:3.9-alpine3.13

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy project
COPY . /app
COPY ./requirements.txt /requirements.txt



# Set work directory
WORKDIR /app
EXPOSE 8000

# Get linux headers for installing some third party packages
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev \
    && apk add libffi-dev libressl-dev \
    && apk add --no-cache jpeg-dev zlib-dev libjpeg \
    && apk add rust cargo 

# Create new user
RUN adduser --disabled-password --no-create-home app

# Make directories to map static and media root and modify directory ownership
RUN mkdir -p /vol/web/static && \
    mkdir -p /vol/web/media && \
    chown -R app:app /vol && \
    chmod -R 755 /vol 

#Make virtual, upgrade pip and install requirements
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /requirements.txt 

# Set user
USER app

#set path
ENV PATH="/py/bin:$PATH"