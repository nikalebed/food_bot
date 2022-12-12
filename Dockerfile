FROM python:3-onbuild

EXPOSE 8888

COPY ./ ./

RUN pip install -r ./requirements.txt
ENV PYTHONPATH .

CMD ["python3","./bot/main.py"]