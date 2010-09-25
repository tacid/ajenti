#!/bin/sh
apt-ftparchive packages repo > repo/Packages
apt-ftparchive packages repo | gzip > repo/Packages.gz
