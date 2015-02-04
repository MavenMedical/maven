#!/usr/bin/bash

echo server {
if [ "$#" -eq 1 ]; then
    echo "
    listen       443 ssl;
    server_name  localhost_ssl;

    ssl on;
    ssl_certificate      /etc/nginx/conf.d/server.crt;
    ssl_certificate_key  /etc/nginx/conf.d/server.key;

    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout  1h;
    keepalive_timeout 300;

    ssl_ciphers ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS;
    ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
    ssl_prefer_server_ciphers   on;
"
else
    echo "listen       80;
    server_name localhost_web;
"
fi

echo '
    location / {
    	root			/home/devel/maven/app/frontend_web/www_modular;
	index			index.html;
    }

    location /services/ {
        proxy_pass		 http://127.0.0.1:8087/;
    	proxy_redirect	 	 off;
	proxy_set_header 	 Host			$host;
	proxy_set_header 	 X-Real-IP      	$remote_addr;
	proxy_set_header 	 X-Forwarded-For  	$proxy_add_x_forwarded_for;
    }

    location /broadcaster/ {
        proxy_pass               http://127.0.0.1:8092/;
        proxy_redirect           off;
        proxy_set_header         Host                   $host;
        proxy_set_header         X-Real-IP              $remote_addr;
        proxy_set_header         X-Forwarded-For        $proxy_add_x_forwarded_for;
        proxy_cache_bypass       1;
    }

    location /api {
        proxy_pass               http://127.0.0.1:8088;
        proxy_redirect           off;
        proxy_set_header         Host                   $host;
        proxy_set_header         X-Real-IP              $remote_addr;
        proxy_set_header         X-Forwarded-For        $proxy_add_x_forwarded_for;
        proxy_cache_bypass       1;
    }

}
'
