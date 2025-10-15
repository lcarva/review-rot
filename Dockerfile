FROM registry.redhat.io/rhel10/python-312-minimal:latest

# TODO: Add some helpful labels.

COPY . /opt/app-root/src

RUN pip install . && review-rot --help

ENTRYPOINT [ "review-rot" ]
CMD []
