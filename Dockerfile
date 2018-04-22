FROM python:3-alpine
WORKDIR /app
ADD requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
ADD . .
CMD /app/app.py
