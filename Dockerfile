FROM python:3.6

WORKDIR /usr/src/melmelboo

COPY requirements.freeze.txt reqs.txt
RUN pip install -r reqs.txt

CMD ["gunicorn", "main:application"]
