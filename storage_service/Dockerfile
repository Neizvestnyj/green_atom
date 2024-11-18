FROM python:3.11

WORKDIR /app

COPY ./requirements ./requirements
RUN pip install -r requirements/requirements.txt -r requirements/requirements.test.txt

COPY . .

EXPOSE 8001

CMD ["uvicorn", "storage_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
