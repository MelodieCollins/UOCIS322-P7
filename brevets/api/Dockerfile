FROM python:3.8
LABEL maintainer="mcolli11@uoregon.edu"
RUN mkdir /api
WORKDIR /api
COPY requirements.txt /api/requirements.txt
RUN pip install -r requirements.txt
COPY . /api
CMD ["python", "api.py"]
