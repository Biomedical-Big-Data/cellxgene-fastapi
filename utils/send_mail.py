import smtplib
from email.mime.text import MIMEText
from conf import config


# 邮件服务器地址和端口号
SMTP_SERVER = config.SMTP_SERVER
SMTP_PORT = config.SMTP_PORT
SENDER_EMAIL = config.SENDER_EMAIL
AUTHORIZATION_CODE = config.AUTHORIZATION_CODE
TEST_EMAIL_ADDRESS = config.TEST_EMAIL_ADDRESS


# 创建一封邮件，文本内容为 "Hello, World!"
message = MIMEText("This is test! Hello, World!", "plain", "utf-8")
message["From"] = SENDER_EMAIL  # 设置发件人昵称
message["To"] = TEST_EMAIL_ADDRESS  # 设置收件人昵称
message["Subject"] = "test"  # 设置邮件主题


def send_mail():
    try:
        smtp_connection = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        smtp_connection.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp_connection.sendmail(SENDER_EMAIL, TEST_EMAIL_ADDRESS, message.as_string())
        smtp_connection.quit()
        print("邮件发送成功！")

    except Exception as e:
        print("邮件发送失败：", e)


if __name__ == "__main__":
    send_mail()
