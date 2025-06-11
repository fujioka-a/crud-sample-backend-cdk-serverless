FROM public.ecr.aws/docker/library/python:3.13.2
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.9.1 /lambda-adapter /opt/extensions/lambda-adapter

WORKDIR /workspace

COPY src/requirements.txt /workspace/requirements.txt
COPY src /workspace/src

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main.py"]
