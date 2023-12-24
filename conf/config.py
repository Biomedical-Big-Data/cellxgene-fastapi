import os
import configparser

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def parse_cfg_dict(items):
    cfg_dict = {}
    for item in items:
        k, v = item
        if v.isdigit():
            cfg_dict[k] = int(v)
        else:
            cfg_dict[k] = v
    return cfg_dict


cp = configparser.ConfigParser()
branch = (
    os.popen("cd %s; git branch | grep \\* | awk '{print $2}'" % PROJECT_ROOT)
    .read()
    .replace("\n", "")
)

if branch == "master":
    cp.read(os.path.join(PROJECT_ROOT, "conf_master.cfg"), encoding="utf8")
else:
    cp.read(os.path.join(PROJECT_ROOT, "conf_preview.cfg"), encoding="utf8")

MYSQL_USER = os.getenv("mysql_user", "")
MYSQL_PASSWORD = os.getenv("mysql_password", "")
MYSQL_HOST = os.getenv("mysql_host", "")
MYSQL_PORT = os.getenv("mysql_port", "")

SMTP_SERVER = os.getenv("smtp_server", "")
SMTP_PORT = os.getenv("smtp_port", "")
SENDER_EMAIL_ACCOUNT = os.getenv("send_mail_account", "")
AUTHORIZATION_CODE = os.getenv("authorization_code", "")
TEST_EMAIL_ADDRESS = os.getenv("test_email_address", "")

MQTT_BROKER_URL = os.getenv("mqtt_broker_url", "")
MQTT_BROKER_PORT = os.getenv("mqtt_broker_port", "")
MQTT_TOPIC = os.getenv("mqtt_topic", "")

VERIFY_URL = os.getenv("verify_url", "")
RESET_PASSWORD_URL = os.getenv("reset_password_url", "")

CELLXGENE_GATEWAY_URL = os.getenv("url", "")
H5AD_FILE_PATH = os.getenv("h5ad_file_path", "")
META_FILE_PATH = os.getenv("meta_file_path", "")

JWT_CONFIG = parse_cfg_dict(cp.items("jwt_config"))

JWT_SECRET_KEY = JWT_CONFIG.get("jwt_secret_key")
JWT_VERIFY_EXPIRE_TIME = JWT_CONFIG.get("jwt_verify_expire_time")
JWT_RESET_PASSWORD_EXPIRE_TIME = JWT_CONFIG.get("jwt_reset_password_expire_time")
JWT_LOGIN_EXPIRE_TIME = JWT_CONFIG.get("jwt_login_expire_time")
JWT_ALGORITHMS = JWT_CONFIG.get("jwt_algorithms")


class UserStateConfig:
    USER_STATE_VERIFY = 1
    USER_STATE_NOT_VERIFY = 0
    USER_STATE_BLOCK = -1


class UserRole:
    USER_ROLE_FORMAL = 0
    USER_ROLE_ADMIN = 1
    USER_ROLE_SUPER_USER = 2


class ProjectStatus:
    HOMEPAGE_SHOW_PROJECT_LIMIT = 3
    MAX_OTHER_FILE_NUM = 5

    PROJECT_STATUS_DELETE = -1
    PROJECT_STATUS_DRAFT = 0
    PROJECT_STATUS_IS_PUBLISH = 1

    PROJECT_STATUS_PRIVATE = 1
    PROJECT_STATUS_PUBLIC = 0


class FileStatus:
    NORMAL = 1
    DELETE = 0


class NormalUserLimit:
    MAXPROJECTCOUNT = 3
    # MAXFILESIZE = 10
    MAXFILESIZE = 10 * 1024 * 1024 * 1024
