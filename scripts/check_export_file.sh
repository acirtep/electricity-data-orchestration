#!/bin/bash -l
yesterday=`date -v -1d +%Y-%m-%d`
ls -la /tmp/export_folder/"110AA0187230044-$yesterday*.xlsx"
