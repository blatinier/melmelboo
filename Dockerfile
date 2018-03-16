FROM python:3.6

WORKDIR /usr/src/melmelboo

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD ["gunicorn", "main:application"]
