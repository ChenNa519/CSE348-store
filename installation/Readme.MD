# Installation

The game engine is built in Python, using the Pygame and NumPy packages.

This package uses Python 3.7 or above.

# Anaconda

We provide an Anacoda YAML file to provide a clean python environment in which to run the game engine. 

1. Download [miniconda](https://docs.conda.io/projects/miniconda/en/latest/) or [Anaconda](https://www.anaconda.com/)

2. Using the miniconda or Anaconda prompt, run the following in the directory you saved this folder
`conda env create -f environment_gameai_yml.yaml`

3. Start the environment:
`source activate gameai` or `conda activate gameai`

It should change your prompt from `(base)` to `(gameai)`.
You can verify that the version of python is 3+ as specified by the yaml file: `python --version`

# Test the basic game engine

`python runbasic.py`

It should pull open a window showing the game world. 
Your mouse should move the on-screen agent. 