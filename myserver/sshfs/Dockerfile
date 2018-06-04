FROM alpine:3.7

RUN export http_proxy=http://proxy.lbs.alcatel-lucent.com:8000; apk update && apk add sshfs sshpass
#RUN sshpass -p "alcatel01"  sshfs -o allow_other -oauto_cache,reconnect atxuser@135.252.240.91:/repo/songsonl  /repo/songsonl