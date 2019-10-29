# Persian-Sentence-Augmenter
Persian Sentence Augmenter

Sentence Augmentation for persian language based on EMNLP-IJCNLP paper: Easy data augmentation techniques for boosting performance on text classification tasks. https://arxiv.org/abs/1901.11196


## How to
```python
from augment import Augment

augmenter = Augment(farsnet_userkey='''<YOUR FARSNET USER KEY HERE>''')
augmenter.augment_sent('<YOUR PERSIAN INPUT SENTENCE HERE>'))
```


### NOTES:
compatible with python 3.6 +
