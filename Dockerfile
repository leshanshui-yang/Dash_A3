FROM python:3.7

USER root

RUN pip install pandas
RUN pip install dash==1.13.3
RUN pip install dash_bootstrap_components

COPY . /
WORKDIR /

EXPOSE 8051

CMD ['python', 'app.py']
