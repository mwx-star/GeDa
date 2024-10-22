# GeDa
## Requirements
* python==3.9.0
* openai==0.27.8
* transformers==4.15.0
## Synthetic Data Generation
```
cd data_generation
python chatgpt.py
python handle_file.py
```
## Characteristic-Driven Iterative Strategy
```
cd select
python myselect
```
Note: Please encode the validation set and synthetic candidates with the characteristic-aware model beforehand, and save the results in the corresponding folder, such as ```./select/14lap/val_triplets_embed.txt``` and ```./select/14lap/chatgpt_synthetic_candidates_embed.txt```.
