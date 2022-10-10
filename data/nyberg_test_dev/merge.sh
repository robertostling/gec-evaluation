#!/usr/bin/env sh

cat Nyberg.CEFR_A.test.corr.txt \
    Nyberg.CEFR_B.test.corr.txt \
    Nyberg.CEFR_C.test.corr.txt \
    > Nyberg.CEFR_ABC.test.corr.txt

cat Nyberg.CEFR_A.test.orig.txt \
    Nyberg.CEFR_B.test.orig.txt \
    Nyberg.CEFR_C.test.orig.txt \
    > Nyberg.CEFR_ABC.test.orig.txt

