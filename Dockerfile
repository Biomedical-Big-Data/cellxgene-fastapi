FROM python:3.11.4

# image workdir
WORKDIR /data/cellxgene_fastapi/

COPY ./requirements.txt /data/cellxgene_fastapi/

# update the sources list
RUN python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
RUN pip config set global.extra-index-url "https://mirrors.aliyun.com/pypi/simple https://pypi.tuna.tsinghua.edu.cn/simple"
RUN pip install -r requirements.txt

# add project to the image
COPY . /data/cellxgene_fastapi/

ENV mysql_host=
ENV mysql_port=
ENV mysql_user=
ENV mysql_password=

ENV smtp_server=
ENV smtp_port=
ENV send_mail_account=
ENV authorization_code=
ENV test_email_address=

ENV mqtt_broker_url=
ENV mqtt_broker_port=
ENV mqtt_topic=

ENV verify_url=
ENV reset_password_url=

ENV url=
ENV h5ad_file_path=
ENV meta_file_path=

ENV jwt_secret_key=
ENV jwt_verify_expire_time=
ENV jwt_reset_password_expire_time=
ENV jwt_login_expire_time=
ENV jwt_algorithms=


# run server after docker is up
CMD ["python", "/data/cellxgene_fastapi/main.py"]
