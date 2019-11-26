#!/bin/bash

## SCRIPT TO RESET SYSTEM!

# rm all metadata files in the file-system
rm -f server-file-system/metadata*

# rm all public keys associated with all devices
rm -f pukdir/*

# rm all entries from all databases
rm -f databases/*
touch databases/filedevicelinks.txt databases/registereddevices.txt

# create random files with random content for testing
echo "file" > server-file-system/file1.txt
echo "file" > server-file-system/file2.txt
echo "file" > server-file-system/file3.txt
echo "file" > server-file-system/file4.txt
