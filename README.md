# Introduction
File Sharing Service

Python project writen in Flask. 
I am not using Flask Sessions but instead I create my own cookies that were stored inside Redis DB. 
Service allowed user to upload then download or share up to 5 files. 
Latest update added support for login from Oauth 2.0 with the Auth0 service. 
Also used Server Sent Events from Node.js server to support notifications on multiple devices at once. 
.ini files are used because Services are running from academic server via uwsgi.
