# line-chart-captioning
This repository is for creating a model that manages to create natural language descriptions from line graphs.


## Dataset
This project uses two pre-existing datasets:
* [FigureQA](https://arxiv.org/abs/1710.07300) ([download link](https://www.microsoft.com/en-us/research/project/figureqa-dataset/))
* [Chart-to-Text](https://arxiv.org/abs/2010.09142) ([github link](https://github.com/JasonObeid/Chart2Text))

The FigureQA dataset is used to generate a synthetic dataset, while Chart-to-Text is used to generate a natural-language dataset.

### Generating synthetic dataset

To generate the synthetic dataset, place the downloaded folders to `data/figureqa` (check the README there), and run 

```python3 src/synthetic/preprocess.py```

Dataset will be placed to `data/processed_synthetic`.

### Generating natural-language dataset

To generate the natural-language dataset, place the downloaded folders to `data/figureqa` (check the README there), and run 

```python3 src/natural/preprocess.py```

Dataset will be placed to `data/processed_natural`.