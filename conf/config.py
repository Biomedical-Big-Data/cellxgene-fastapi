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
branch = os.popen("cd %s; git branch | grep \\* | awk '{print $2}'" % PROJECT_ROOT).read().replace('\n', '')
if branch == 'master':
    cp.read(os.path.join(PROJECT_ROOT, 'conf_master.cfg'))
else:
    cp.read(os.path.join(PROJECT_ROOT, 'conf_preview.cfg'))


MAIL_CONFIG = parse_cfg_dict(cp.items('mail_config'))
DATABASE = parse_cfg_dict(cp.items('database'))
JWT_CONFIG = parse_cfg_dict(cp.items('jwt_config'))
VERIFY_CONFIG = parse_cfg_dict(cp.items('verify_config'))


SMTP_SERVER = MAIL_CONFIG.get('smtp_server')
SMTP_PORT = MAIL_CONFIG.get('smtp_port')
SENDER_EMAIL_ACCOUNT = MAIL_CONFIG.get('send_mail_account')
AUTHORIZATION_CODE = MAIL_CONFIG.get("authorization_code")
SENDER_NAME = MAIL_CONFIG.get("sender_name")
TEST_EMAIL_ADDRESS = MAIL_CONFIG.get("test_email_address")

DATABASE_URL = DATABASE.get("database_url")

JWT_SECRET_KEY = JWT_CONFIG.get("jwt_secret_key")

VERIFY_URL = VERIFY_CONFIG.get('verify_url')
USER_STATE_VERIFY = VERIFY_CONFIG.get('user_state_verify')
USER_STATE_NOT_VERIFY = VERIFY_CONFIG.get('user_state_not_verify')
USER_STATE_BLOCK = VERIFY_CONFIG.get('user_state_block')
USER_ROLE_FORMAL = VERIFY_CONFIG.get('user_role_formal')
USER_ROLE_ADMIN = VERIFY_CONFIG.get('user_role_admin')
RESET_PASSWORD_URL = VERIFY_CONFIG.get('reset_password_url')
