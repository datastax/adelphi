FROM golang

ENV GEMINI_URL="https://github.com/scylladb/gemini/releases/download/v1.7.3/gemini_1.7.3_Linux_x86_64.tar.gz"

RUN wget -O - $GEMINI_URL | tar -zxvf -

CMD /go/gemini