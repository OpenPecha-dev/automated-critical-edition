# automated-critical-edition

## Options Ranking

1. First create config file
```bash
cp src/config-example.ini src/config.ini
```

2. Then rank the options
```python

from rank_options import OptionRanker

ranker = OptionsRanker()

# for config.lm_type = lstm
ranks = ranker.rank(
  options=["འི", "གི", "དི"],
  left_context=["བདེ་ཆེན་", "པདྨ་",  "འཁྱིལ་བ"], # context should be list of words
  right_context=["ཕོ་བྲང་", "ན"]
)

print(ranks)
# [('འི', 1.3756102224075983e-39), ('གི', 3.8162690334265747e-51), ('དི', 7.808966806052166e-57)]

# for config.lm_type = roberta
ranks = ranker.rank(
    options=["འི", "གི", "དི"],
    left_context="བདེ་ཆེན་པདྨ་འཁྱིལ་བ",
    right_context="ཕོ་བྲང་ན"
)
print(ranks)
# [('འི', 5.318869), ('གི', 5.860524), ('དི', 7.019289)]
```
