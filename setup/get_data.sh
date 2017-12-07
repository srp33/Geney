#!/bin/bash

set -euo pipefail

function download {
  osfID="$1"

  if [ ! -f $osfID.tar.gz ]
  then 
    url="https://osf.io/${osfID}/download?version=1"
    wget -O data/$osfID.tar.gz "$url"
    tar -zxvf data/$osfID.tar.gz -C data/
    rm data/$osfID.tar.gz
  fi
}

download zqmsc
