FROM python:3.8.5
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY . .

EXPOSE 5000

CMD ["python3","app.py"]