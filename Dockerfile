FROM registry.redhat.io/rhel9/python-39:latest@sha256:a5fc6b41031a5115ada60554027dc2806c1a74c64655f81dfd70b9fb57f47738

# TODO: Add some helpful labels.

COPY . /opt/app-root/src

RUN pip install . && review-rot --help

ENTRYPOINT [ "review-rot" ]
CMD []
