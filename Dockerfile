# Base image using Red Hat's universal base image (rhel 8) for python
FROM registry.access.redhat.com/ubi8/python-36:latest

# copy the app code into the container
COPY . /opt/flask-url-shortener
# set the root directory for subsequent commands
WORKDIR /opt/flask-url-shortener

# install python package requirements
RUN pip install -r requirements.txt

# set the application name so flask can find it
ENV FLASK_APP=app
# turn on development mode
ENV FLASK_ENV=development

# expose the http port so we can connect to the container externally
EXPOSE 5000

# allow us to write to the database
# we need to temporarily become root
USER 0
RUN chmod a+rw instance instance/*
# revert back to a non-root user. best practice
USER 1001

# initialize the database and run the app
ENTRYPOINT flask init-db; flask run --host=0.0.0.0
