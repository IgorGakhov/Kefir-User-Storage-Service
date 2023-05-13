FROM python:3.8 
 
WORKDIR /app 
 
COPY . . 
 
ENV PYTHONDONTWRITEBYTECODE 1 
ENV PYTHONUNBUFFERED 1 
 
RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt 
 
EXPOSE 8000
