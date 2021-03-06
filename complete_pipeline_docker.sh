#!/bin/bash

echo 'Pipeline started.'
### Preperation ###
mkdir -p /data/results

### Creation ###
echo '### Creation ###'
cd ./dataset/creation
echo '# Generating'
python main.py -i ../styleCrawling/resources/urls_us -o /data/results -t 3 -b -v -z -s cg

### Recognition ###
echo '### Recognition ###'

## Localisation
echo '## Localisation'
cd ../../recognition/localisation/
./build/localiser /data/results/dataset /data/results/dataset_tesseract_localised

## Determination on ideal
echo '## Determination on ideal'
cd ../determination/
./build/determiner /data/results/dataset /data/results/dataset /data/results/dataset_tesseract_determiner

## Determination on localised (complete)
echo '## Determination on localised (complete)'
./build/determiner /data/results/dataset /data/results/dataset_tesseract_localised /data/results/dataset_tesseract_complete

## Evaluation
echo '## Evaluation'
cd ../../evaluation
# echo '# Determination'
# python evaluation.py /data/results/dataset /data/results/dataset_tesseract_determiner/ -cp 0.9 -lt 2 -o /data/results/evaluation_determiner
# echo '# Localised (complete)'
# python evaluation.py /data/results/dataset /data/results/dataset_tesseract_complete/ -cp 0.9 -lt 2 -o /data/results/evaluation_complete

echo '# Determination'
pipenv run python evaluate_combinations.py ../data/results/dataset ../data/results/dataset_tesseract_determiner/ -o ../data/results/evaluation_determiner
echo '# Localised (complete)'
pipenv run python evaluate_combinations.py ../data/results/dataset ../data/results/dataset_tesseract_complete/ -o ../data/results/evaluation_complete
