#!/bin/sh
apt-ftparchive packages . > Packages
apt-ftparchive packages . | gzip > Packages.gz
