ENVIRONMENT VARIABLE
	ENV mysql_host= mysql host
	ENV mysql_port= mysql port
	ENV mysql_user= mysql username
	ENV mysql_password= mysql password
	
	ENV smtp_server= smtp server host
	ENV smtp_port= smtp port(465) SMTP SSL MODE
	ENV send_mail_account= mail account(your smtp mail account)
	ENV authorization_code= smtp authorization code or smtp mail account password
	ENV test_email_address= ""(no need)
	
	ENV mqtt_broker_url= mqtt host
	ENV mqtt_broker_port= mqtt port(1883)
	ENV mqtt_topic= mqtt subscribe topic
	
	ENV verify_url= verfify your register email url(http://{your web host}/#/user/active?token=)
	ENV reset_password_url= reset your password url(http(https)://{your web host}/#/user/reset?token=)
	
	ENV cellxgene_gateway_url= your cellxgene-gateway url()
	ENV h5ad_file_path= save h5ad file path(like /data/files)
	ENV meta_file_path= save update meta file(like /data/meta_file)
	
	ENV jwt_secret_key= jwt secret key
	ENV jwt_verify_expire_time= verify register email expire time
	ENV jwt_reset_password_expire_time= reset password expire time
	ENV jwt_login_expire_time= user login exprire time
	ENV jwt_algorithms= jwt algorithms
