FROM python:3
ADD *.py /
ADD config.ini /
ADD news.json /
RUN pip3 install python-telegram-bot
RUN pip3 install pyGitHub
RUN pip3 install requests
# RUN pip install telegram.ext
CMD [ "python", "./main.py" ]