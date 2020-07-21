FROM python:3.7

USER root

RUN pip install pandas
RUN pip install dash==1.13.3

COPY . /
WORKDIR /

EXPOSE 8051

CMD['python', 'app.py']
