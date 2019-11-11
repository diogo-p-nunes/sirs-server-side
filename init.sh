#!/bin/bash

rm -f server-file-system/metadata*

rm -f pukdir/*

rm -f databases/*
touch databases/filedevicelinks.txt databases/registereddevices.txt

echo "file" > server-file-system/file1.txt
echo "file" > server-file-system/file2.txt
echo "file" > server-file-system/file3.txt
echo "file" > server-file-system/file4.txt
