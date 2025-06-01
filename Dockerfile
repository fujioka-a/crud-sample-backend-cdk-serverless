FROM public.ecr.aws/lambda/python:3.13
COPY --from=public.ecr.aws/awsguru/aws-lambda-adapter:0.7.1 /lambda-adapter /opt/extensions/lambda-adapter

# 依存関係のインストールなど（省略）

ENTRYPOINT ["uvicorn"]
CMD [ "main:app", "--host", "0.0.0.0", "--port", "8080"]
