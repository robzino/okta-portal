FROM python:3.7-alpine

COPY requirements.txt ./
RUN pip3 install -r requirements.txt
RUN pip3 install requests flask-session Flask
RUN pip3 install --force-reinstall itsdangerous==2.0.1

# Create app directory
WORKDIR /app
COPY static static/
COPY templates templates/
COPY app.py app.py
COPY functions.py functions.py
COPY client_secrets.json client_secrets.json

EXPOSE 5000
ENTRYPOINT ["python3"]

# debug dev server
#CMD ["app.py"]

#  spawn 2 worker processes
#  log levels: 'debug' 'info' 'warning' 'error' 'critical'

CMD ["/usr/local/bin/gunicorn", "app:app", "-w 2", "--log-level=info", "-b", "0.0.0.0:5000"]

#ENTRYPOINT ["tail", "-f", "/dev/null"]
