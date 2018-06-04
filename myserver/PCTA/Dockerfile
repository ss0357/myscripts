FROM centos:7.4.1708

COPY ./PCTA /root/PCTA
RUN echo proxy=http://proxy.lbs.alcatel-lucent.com:8000 >> /etc/yum.conf \
    && yum clean all \
    && yum makecache \
    && yum install -y net-tools sysvinit-tools tcpdump \
    && yum install glibc.i686 libX11.i686 ncurses-libs.i686 libgcc.i686 -y --setopt=protected_multilib=false \
    && yum clean all \
    && rm -rf /var/cache/yum/*

#RUN yum install net-tools -y
#RUN yum install glibc.i686 libX11.i686 ncurses-libs.i686 libgcc.i686 -y --setopt=protected_multilib=false
#RUN yum install sysvinit-tools wireshark tcpdump -y
WORKDIR /root/PCTA
CMD ./pcta.exe