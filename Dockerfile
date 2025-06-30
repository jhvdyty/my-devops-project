FROM python:3.13.1
WORKDIR /app
COPY /test.py /app/python_name_ganirator.py 
ENTRYPOINT ["python", "python_name_ganirator.py"]