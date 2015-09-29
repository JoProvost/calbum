#!/bin/bash

function create_test_image() {
    local name=$1
    local date_time=$2
    local expected_path=$3
    local event_name=$4

    convert -background white -fill black -font AndaleMono -pointsize 12 label:"DT: $date_time" $name
    if [ "$date_time" ]; then
        exiftool -DateTimeOriginal="$date_time" $name
        rm -f ${name}_original
    fi
    cat <<EOF >> images.yaml
${name}:
  md5sum: $(md5 -q $name)
  expected_path: ${expected_path}
  date_time: ${date_time}
  event_name: ${event_name}

EOF
}

function create_test_video() {
    local name=$1
    local date_time=$2
    local expected_path=$3
    local event_name=$4

    convert -background white -fill black -font AndaleMono -pointsize 12 label:"$date_time" video.jpeg
    ffmpeg -y -r 15 -i video.jpeg \
      -metadata "Create Date=${date_time}" \
      -metadata "creation_date=${date_time}" \
      -metadata "creation_time=${date_time}" \
      -vcodec mpeg4 $name
    rm video.jpeg
    rm -f ${name}_original
    cat <<EOF >> images.yaml
${name}:
  md5sum: $(md5 -q $name)
  expected_path: ${expected_path}
  date_time: ${date_time}
  event_name: ${event_name}

EOF
}


cd $(dirname $0)
echo "---" > images.yaml

create_test_image image-01.jpeg            '2012:05:01 01:00:00' 2012/2012-05/2012-05-01-01-00-00.jpeg 'First event'
create_test_image image-02.jpg             '2012:05:02 02:00:00' 2012/2012-05/2012-05-02-02-00-00.jpeg 'Second event'
create_test_image image-03.tif             '2013:02:01 03:00:00' 2013/2013-02/2013-02-01-03-00-00.tiff ''
create_test_image image-04.jpeg            '2013:03:01 04:00:00' 2013/2013-03/2013-03-01-04-00-00.jpeg ''
create_test_image image-05.jpeg            '2012:05:01 05:00:00' 2012/2012-05/2012-05-01-05-00-00.jpeg 'First event'
create_test_image image-06.JPG             '2015:11:23 06:00:00' 2015/2015-11/2015-11-23-06-00-00.jpeg 'Last event'
create_test_image IMG_20130302_070000.jpeg ''                    2013/2013-03/2013-03-02-07-00-00.jpeg ''
create_test_video video-01.mp4             '2014-01-01 19:30:00' 2014/2014-01/2014-01-01-19-30-00.mp4  ''
create_test_video video-02.3gp             '2014-02-02 19:30:00' 2014/2014-02/2014-02-02-19-30-00.3gp  ''
