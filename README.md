# line-chart-captioning
This repository is for creating a model that manages to create natural language descriptions from line graphs.


## Dataset
This project uses two pre-existing datasets:
* [FigureQA](https://arxiv.org/abs/1710.07300) ([download link](https://www.microsoft.com/en-us/research/project/figureqa-dataset/))
* [Chart-to-Text](https://arxiv.org/abs/2010.09142) ([github link](https://github.com/JasonObeid/Chart2Text))

The FigureQA dataset is used to generate a synthetic dataset, while Chart-to-Text is used to generate a natural-language dataset.

### Generating synthetic dataset

To generate the synthetic dataset, place the downloaded folders to `data/figureqa` (check the README there), and run 

```python3 src/synthetic/preprocess.py data/fiqureqa/X```

Flags you can provide:
* `--unroll-descriptions`: By default, if a plot/figure/graph has more than 1 description, they are concatenated. 
This flag unrolls the descriptions, to create `n` rows in `captions.csv` if there are `n > 1` descriptions for a given graph.
* `--replace-subjects`: Replaces subjects in descriptions. For example `Red is greater than Blue` becomes `<A> is greater than <B>`.
This flag also adds `subject_map` column to `captions.csv`, so for every plot there is a JSON blob string that maps replacements to original subjects.
* `--description-limit N`: Limits description length in sentences. Cannot be present together with `--unroll-descriptions`
* `--synthetic-config FILE`: Provide a config file for custom question templates and desired question types. An example file is provided (`synthetic.default.json`). For correct forms, check `question_to_description` in `src/synthetic/preprocess.py`. For question IDs, check keys in `question_type_to_id`

Dataset will be placed to `data/processed_synthetic/X`.

### Generating natural-language dataset

To generate the natural-language dataset, place the downloaded folders to `data/charttotext` (check the README there), and run 

```python3 src/natural/preprocess.py```

Dataset will be placed to `data/processed_natural`.
