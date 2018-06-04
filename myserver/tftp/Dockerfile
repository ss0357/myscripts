FROM alpine:3.7
RUN export http_proxy=http://proxy.lbs.alcatel-lucent.com:8000
RUN export http_proxy=http://proxy.lbs.alcatel-lucent.com:8000; apk add --no-cache tftp-hpa
VOLUME /tftpboot
EXPOSE 69/udp
ENTRYPOINT ["in.tftpd"]
CMD ["-L", "--secure", "-c", "-v", "-s", "/tftpboot"]