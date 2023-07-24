import smtplib
from email.mime.text import MIMEText
from conf import config


# 邮件服务器地址和端口号
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
SENDER_EMAIL_NAME = config.SENDER_EMAIL_NAME
AUTHORIZATION_CODE = config.AUTHORIZATION_CODE
TEST_EMAIL_ADDRESS = config.TEST_EMAIL_ADDRESS


def send_mail(user_name, verify_url, to_list=None):
    if to_list is None:
        to_list = [TEST_EMAIL_ADDRESS]
    mail_template = verify_mail_template(user_name=user_name, verify_url=verify_url)
    message = MIMEText("{}".format(mail_template), "plain", "utf-8")
    message["From"] = SENDER_EMAIL  # 设置发件人昵称
    message["To"] = to_list  # 设置收件人昵称
    message["Subject"] = "账户验证邮件"  # 设置邮件主题
    try:
        smtp_connection = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_connection.login(SENDER_EMAIL, AUTHORIZATION_CODE)
        smtp_connection.sendmail(SENDER_EMAIL, TEST_EMAIL_ADDRESS, message.as_string())
        smtp_connection.quit()
        # print("邮件发送成功！")
        return True

    except Exception as e:
        # print("邮件发送失败：", e)
        return False


def verify_mail_template(user_name, verify_url):
    mail_template = """
                    Hi %s,
                    验证链接：%s
        """ % (
        user_name,
        verify_url,
    )
    return mail_template


if __name__ == "__main__":
    send_mail("www.baidu.com")
