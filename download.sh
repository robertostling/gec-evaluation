#!/usr/bin/env bash

mkdir -p data
curl -s "https://www.cl.cam.ac.uk/research/nl/bea2019st/data/wi+locness_v2.1.bea19.tar.gz" | tar xvz -C data
