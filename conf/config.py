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


MAIL_CONFIG = parse_cfg_dict(cp.items("mail_config"))
DATABASE = parse_cfg_dict(cp.items("database"))
JWT_CONFIG = parse_cfg_dict(cp.items("jwt_config"))
VERIFY_CONFIG = parse_cfg_dict(cp.items("verify_config"))
CELLXGENE_GATEWAY_CONFIG = parse_cfg_dict(cp.items("cellxgene_gateway"))
MQTT_CONFIG = parse_cfg_dict(cp.items("mqtt_config"))


SMTP_SERVER = MAIL_CONFIG.get("smtp_server")
SMTP_PORT = MAIL_CONFIG.get("smtp_port")
SENDER_EMAIL_ACCOUNT = MAIL_CONFIG.get("send_mail_account")
AUTHORIZATION_CODE = MAIL_CONFIG.get("authorization_code")
SENDER_NAME = MAIL_CONFIG.get("sender_name")
TEST_EMAIL_ADDRESS = MAIL_CONFIG.get("test_email_address")

DATABASE_URL = DATABASE.get("database_url")

JWT_SECRET_KEY = JWT_CONFIG.get("jwt_secret_key")
JWT_VERIFY_EXPIRE_TIME = JWT_CONFIG.get("jwt_verify_expire_time")
JWT_RESET_PASSWORD_EXPIRE_TIME = JWT_CONFIG.get("jwt_reset_password_expire_time")
JWT_LOGIN_EXPIRE_TIME = JWT_CONFIG.get("jwt_login_expire_time")
JWT_ALGORITHMS = JWT_CONFIG.get("jwt_algorithms")

VERIFY_URL = VERIFY_CONFIG.get("verify_url")
RESET_PASSWORD_URL = VERIFY_CONFIG.get("reset_password_url")

CELLXGENE_GATEWAY_URL = CELLXGENE_GATEWAY_CONFIG.get("url")
H5AD_FILE_PATH = CELLXGENE_GATEWAY_CONFIG.get("h5ad_file_path")
META_FILE_PATH = CELLXGENE_GATEWAY_CONFIG.get("meta_file_path")
UPDATE_FILE_PATH = CELLXGENE_GATEWAY_CONFIG.get("update_project_file_path")

MQTT_BROKER_URL = MQTT_CONFIG.get("mqtt_broker_url")
MQTT_BROKER_PORT = MQTT_CONFIG.get("mqtt_broker_port")
MQTT_TOPIC = MQTT_CONFIG.get("mqtt_topic")


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
