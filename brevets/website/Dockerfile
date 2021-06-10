FROM python:3.8
LABEL maintainer="mcolli11@uoregon.edu"
RUN mkdir /website
WORKDIR /website
COPY requirements.txt /website/requirements.txt
RUN pip install -r requirements.txt
COPY . /website
CMD ["python", "website.py"]