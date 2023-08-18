FROM centos:7
RUN yum -y update && \
    yum -y install httpd-tools && \
    yum clean all
ENTRYPOINT ["ab" , "http://google.com/" ]
