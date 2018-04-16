FROM python:3.6-alpine

# Copying requirements separately allows us to avoid pip install if
# our requirements.txt didn't update.
COPY app/requirements.txt /opt/app/requirements.txt
RUN pip install -r /opt/app/requirements.txt

COPY app /opt/app

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD [ "/usr/local/bin/python3.6", "/opt/app/healthcheck.py" ]

CMD ["/usr/local/bin/python3.6", "/opt/app/app.py"]