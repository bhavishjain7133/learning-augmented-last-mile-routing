# Data

Dataset files are deliberately excluded from version control.

## Official source

- Registry: https://registry.opendata.aws/amazon-last-mile-challenges/
- S3 prefix: `s3://amazon-last-mile-challenges/almrrc2021/`

The training data contain 6,112 historical routes and the evaluation data
contain 3,072 routes, all from 2018.

## Licence

The dataset is provided under the Creative Commons Attribution-NonCommercial
4.0 International licence. The repository's MIT licence applies to original
code only, not to the dataset.

## Expected local layout

```text
data/raw/
  training/
    actual_sequences.json
    invalid_sequence_scores.json
    route_data.json
    package_data.json
    travel_times.json
  evaluation/
    eval_actual_sequences.json
    eval_invalid_sequence_scores.json
    eval_route_data.json
    eval_package_data.json
    eval_travel_times.json
```

Use `python scripts/download_data.py --bundle core` for the smaller files or
`--bundle training` for all training inputs. The downloader streams files and
does not load them into memory.

## Restrictions

- do not attempt to reverse the geographic obfuscation;
- do not redistribute raw files through GitHub;
- preserve official attribution in reports and derived artifacts;
- use the data only for non-commercial research/education under its licence.

