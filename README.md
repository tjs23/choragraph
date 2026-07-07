# Choragraph

Choragraph is a deep-learning based approach to the spatial mapping and analysis of subcellular proteomics. Choragraph uses an ensemble of deep neural network models to provide context-dependent reconstruction of missing proteomic values, and prediction of a protein's subcellular localisation in a manner that is innately aware of multi-localisation. 


## Collating input data

Initially proteomic profiles, stored in TSV or CSV files, are combined with training marker lists (classified proteins) to create a dataset:

`python3 collate_inputs.py -r RUN_NAME -d OUTPUT_DIR -p 'profiles/data_replicate*.tsv' -o markers/organelle_markers.csv -u markers/suborganelle_markers.csv`


This will create a Choragraph dataset in a RUN_NAME.npz file.

## Running DNN training

Given one or more collated input datasets, DNN training may be run via:

`python3 dnn_workflow.py -d datasets*.npz -m out_models_dir`

## Finalising output

After the DNN has run, datasets must be finalised to calculate p-values, make best-class predictions and construct filled-in profiles. Optionally comparison predictions are added from an external method. Then the data is output as an SQLITE3 database file and as a TSV format table.

`python3 collate_outputs.py -d datasets*.npz` 
