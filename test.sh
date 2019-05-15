#!/usr/bin/env bash

PATH_PAYTHON_BIN="./python/bin/python3.6"
PATH_SCRIPT="./src/main.py"
PATH_TRAININING_DATA="./dev/small/training.conll"
PATH_DEV_DATA="./dev/small/devel.conll"
PATH_TEST_DATA="./dev/small/test.conll"
PATH_EMBEDDING="./dev/word_embedding/senna.emb.txt"
OUTPUT_DIR="./output"

# training
$PATH_PAYTHON_BIN \
$PATH_SCRIPT  \
--mode train \
--train_data $PATH_TRAININING_DATA \
--dev_data $PATH_DEV_DATA \
--data_type conll05 \
--drop_rate 0.1 \
--reg 0.0001 \
--hidden_dim 300 \
--n_layers 4 \
--halve_lr \
--word_emb $PATH_EMBEDDING \
--save \
--output_dir ${OUTPUT_DIR}

# predicting
$PATH_PAYTHON_BIN \
$PATH_SCRIPT  \
--mode test \
--test_data $PATH_TEST_DATA \
--data_type conll05 \
--drop_rate 0.1 \
--hidden_dim 300 \
--n_layers 4 \
--output_dir ${OUTPUT_DIR} \
--output_fn conll2005.test \
--halve_lr \
--word_emb $PATH_EMBEDDING \
--load_label ${OUTPUT_DIR}/label_ids.txt \
--load_param ${OUTPUT_DIR}/param.epoch-0.pkl.gz \
--search greedy

