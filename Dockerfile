FROM public.ecr.aws/docker/library/python:3.12.2
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

WORKDIR /src
ADD . .
RUN pip install -r src/requirements.txt

CMD ["python", "src/main.py"]
