FROM alpine:3.7
RUN export http_proxy=http://proxy.lbs.alcatel-lucent.com:8000; apk add --no-cache ser2net busybox-extras

ENTRYPOINT ["ser2net"]
CMD ["-c", "/etc/ser2net.conf", "-n"]