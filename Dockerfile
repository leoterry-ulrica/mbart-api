# Use the official Python 3.10 image as a parent image
FROM python:3.10-slim

# Set environment variables
ENV MODEL_PATH /data/models

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
# 设置为阿里镜像源
RUN pip install --no-cache-dir  -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run on container start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
