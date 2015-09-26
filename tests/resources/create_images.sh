#!/bin/bash

function create_test_image() {
    local name=$1
    local date_time=$2
    local expected_path=$3
    local event_name=$3

    convert -background white -fill black -font AndaleMono -pointsize 12 label:"$date_time" $name
    exiftool -DateTimeOriginal="$date_time" $name
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
create_test_image image-01.jpeg '2012:05:01 01:00:00' 2012/2012-05/2012-05-01-01-00-00.jpeg 'First event'
create_test_image image-02.jpeg '2012:05:02 02:00:00' 2012/2012-05/2012-05-02-02-00-00.jpeg 'Second event'
create_test_image image-03.jpeg '2013:02:01 03:00:00' 2013/2013-02/2013-02-01-03-00-00.jpeg ''
create_test_image image-04.jpeg '2013:03:01 04:00:00' 2013/2013-03/2013-03-01-04-00-00.jpeg ''
create_test_image image-05.jpeg '2012:05:01 05:00:00' 2012/2012-05/2012-05-01-05-00-00.jpeg 'First event'
create_test_image image-06.jpeg '2015:11:23 06:00:00' 2015/2015-11/2015-11-23-06-00-00.jpeg 'Last event'