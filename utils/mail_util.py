import smtplib
from email.mime.text import MIMEText
from conf import config


# 邮件服务器地址和端口号
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL_ACCOUNT
SENDER_EMAIL_NAME = config.SENDER_NAME
AUTHORIZATION_CODE = config.AUTHORIZATION_CODE
TEST_EMAIL_ADDRESS = config.TEST_EMAIL_ADDRESS


def send_mail(mail_template: str, subject: str, to_list: str | None):
    if to_list is None:
        to_list = [TEST_EMAIL_ADDRESS]
    message = MIMEText("{}".format(mail_template), "plain", "utf-8")
    message["From"] = SENDER_EMAIL  # 设置发件人昵称
    message["To"] = to_list  # 设置收件人昵称
    message["Subject"] = subject  # 设置邮件主题
    try:
        smtp_connection = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_connection.login(SENDER_EMAIL, AUTHORIZATION_CODE)
        smtp_connection.sendmail(SENDER_EMAIL, to_list, message.as_string())
        smtp_connection.quit()
        # print("邮件发送成功！")
        return True

    except Exception as e:
        print("邮件发送失败：", e)
        return False


def verify_mail_template(user_name: str, verify_url: str):
    mail_template = """
                    Hi %s,
                    验证链接：%s
        """ % (
        user_name,
        verify_url,
    )
    return mail_template


def reset_password_mail_template(user_name: str, reset_password_url: str):
    mail_template = """
                    Hi %s,
                    重置密码链接：%s
        """ % (
        user_name,
        reset_password_url,
    )
    return mail_template


if __name__ == "__main__":
    send_mail("www.baidu.com")
