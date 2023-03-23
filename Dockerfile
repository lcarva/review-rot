FROM registry.redhat.io/rhel9/python-39:latest

# TODO: Add some helpful labels.

COPY . /opt/app-root/src

RUN pip install . && review-rot --help

ENTRYPOINT [ "review-rot" ]
CMD []
