#!/bin/bash 
# Copyright 2022 Balacoon

set -e
set -x

usage() {
    cat <<EOF
Usage:
bash $1 [--tag some_tag] [--build-fe] [--no-cache]

Arguments:
tag - tag of docker image, by default "latest"
build-fe - balacoon_frontend package is built from sources (private package)
no-cache - rebuild all docker layers from scratch
EOF
}

docker_image_name="learn_to_normalize"
tag="latest"
build_fe_opt=""
no_cache_opt=""
ssh_keys_opt=""
while [ "$1" != "" ]; do
    case $1 in
        --tag )
            shift
            tag=$1
        ;;
        --build-fe )
            build_fe_opt="--build-arg build_fe=true"
        ;;
        --no-cache )
	    no_cache_opt="--no-cache"
	;;
        -h | --help ) usage $0
            exit
        ;;
        * ) usage $0
            exit 1
    esac
    shift
done

DOCKER_BUILDKIT=1 docker build --ssh default $no_cache_opt \
	-t $docker_image_name:$tag $build_fe_opt \
	--build-arg user_id=$(id -u) --build-arg group_id=$(id -g) \
	-f docker/Dockerfile .

