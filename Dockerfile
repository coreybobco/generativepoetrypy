FROM python:3.7.4

RUN echo 'deb http://ftp.de.debian.org/debian buster main contrib' > /etc/apt/sources.list.d/fonts.list
RUN apt-get update && apt install -y libhunspell-dev ttf-mscorefonts-installer
RUN fc-cache

ADD ./ /usr/src/app/
WORKDIR /usr/src/app/
RUN pip3 install -r requirements.txt
RUN python3 -m nltk.downloader stopwords

CMD sleep infinity