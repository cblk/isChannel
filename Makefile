build:
	docker build --build-arg http_proxy=http://172.17.0.1:8123 --build-arg https_proxy=http://172.17.0.1:8123 -t registry.cn-shanghai.aliyuncs.com/ybase/list-detector:dev .
push:
	docker push registry.cn-shanghai.aliyuncs.com/ybase/list-detector:dev
rm_none:
	docker images | grep none | awk '{print $3}' | xargs docker rmi -f