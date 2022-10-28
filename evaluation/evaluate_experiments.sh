#!/bin/bash

GLEU="python3 evaluation/compute_gleu.py"
DATA=./data

echo "== DEVELOPMENT SET RESULTS =="
for target in `ls data/experiments/Nyberg.CEFR_ABC.dev.*`; do
    if [[ -e $target && ! $target =~ \.log$ ]]; then
        ref1=$DATA/nyberg_test_dev/Nyberg.CEFR_ABC.dev.corr.txt
        src=$DATA/nyberg_test_dev/Nyberg.CEFR_ABC.dev.orig.txt
        $GLEU \
            -r "$ref1" -s "$src" -o "$target" --tokenizer sv_core_news_sm
    fi
done

echo '---- BASELINE ----'
ref1=$DATA/nyberg_test_dev/Nyberg.CEFR_ABC.dev.corr.txt
src=$DATA/nyberg_test_dev/Nyberg.CEFR_ABC.dev.orig.txt
$GLEU -r "$ref1" -s "$src" -o "$src" --tokenizer sv_core_news_sm
echo '------------------'

echo "== FULL TEST SET RESULTS =="
for level in A B C ABC; do
    for target in `ls data/experiments/Nyberg.CEFR_"$level".test.*`; do
        if [[ -e $target && ! $target =~ \.log$ ]]; then
            ref1=$DATA/nyberg_test_dev/Nyberg.CEFR_"$level".test.corr.txt
            src=$DATA/nyberg_test_dev/Nyberg.CEFR_"$level".test.orig.txt
            $GLEU \
                -r "$ref1" -s "$src" -o "$target" --tokenizer sv_core_news_sm
        fi
    done
done

echo "== MANUAL TEST SET RESULTS =="
for level in A B C; do
    for target in `ls data/experiments/Nyberg.CEFR_"$level".manual_test.*`; do
        if [[ ! $target =~ \.log$ ]]; then
            ref1=$DATA/nyberg_test_dev/Nyberg.CEFR_"$level".manual_test.corr.txt
            ref2=$DATA/experiments/Nyberg.CEFR_"$level".manual_test.robert
            src=$DATA/nyberg_test_dev/Nyberg.CEFR_"$level".manual_test.orig.txt
            
            #echo `basename $target`
            $GLEU \
                -r "$ref1" -s "$src" -o "$target" --tokenizer sv_core_news_sm
            if [ -e "$ref2" ]; then
                echo "  With reference `basename $ref2`"
                echo -n "  "
                $GLEU \
                    -r "$ref2" -s "$src" -o "$target" \
                    --tokenizer sv_core_news_sm \
                    --tokenize-reference
            fi
            if [[ $target =~ -corr$ ]]; then
                orig=`echo $target | sed 's/-corr//g'`
                echo "  Comparing system output with its corrected version"
                echo -n "  "
                # NOTE: misleading variable names below since we are doing
                # things a bit backwards here
                $GLEU \
                    -r "$target" -s "$orig" -o "$orig" \
                    --tokenizer sv_core_news_sm \
                    --tokenize-reference
            fi
        fi
    done
    echo '---- BASELINE ----'
    $GLEU \
        -r data/nyberg_test_dev/Nyberg.CEFR_"$level".manual_test.corr.txt \
        -s data/nyberg_test_dev/Nyberg.CEFR_"$level".manual_test.orig.txt \
        -o data/nyberg_test_dev/Nyberg.CEFR_"$level".manual_test.orig.txt \
        --tokenizer sv_core_news_sm
    echo '------------------'
done

