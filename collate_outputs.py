from glob import glob
import os
from schisome import SchisomeDataSet

run_tag = 'May26v2'
data_paths = glob(f'datasets/*_{run_tag}.npz')

## ## Add Miguel's experimental lists

for data_path in data_paths:
   data_set = SchisomeDataSet(data_path, aux_marker_key='suborganelle')
   data_set.info(f'Finalising {data_path}')  
   
   tagm_path = 'markers/Arabidopsis_PBS_May26v1_nonnan_profiles_TAGM_MCMC_predictions.csv'
   mkey = data_set.comparison_markers_key
   data_set.add_scored_markers(mkey, tagm_path, id_col=1, class_col=3, score_col=4, score_thresh=0.95)
   
   #data_set.reset_2d_proj()
   
   if not data_set.has_predictions:
       data_set.warn(f'Dataset at {data_path} has no mixed class and reconstruction predictions. The DNN workflow should be run first.')
       continue
   
   if not data_set.has_array_key('pval'):
       data_set.info(f'Calculating p-values for {data_path}')
       data_set.make_pvalues()

   if not data_set.has_array_key('prediction'):
       data_set.info(f'Making class predictions for {data_path}')
       data_set.make_class_predictions()
           
   if not data_set.has_profile_key('zfill'):
       data_set.info(f'Reconstructing profiles for {data_path}')
       data_set.make_profile_predictions(max_missing=0.5)

   plot_args = dict(min_nonzero=0.5, spot_size=16)
   #data_set.plot_umap_2d('zfill', ['training', 'prediction', 'prediction2'], ['Train', 'Pred', 'Duals'], **plot_args)
   #data_set.plot_umap_2d('recon', ['training', 'prediction', 'prediction2'], ['Train', 'Pred', 'Duals'], **plot_args)

   file_root = os.path.splitext(data_path)[0]
   sqlite_path = file_root + '.sqlite' 
   data_set.info(f'Making SQLite3 database {sqlite_path}')  
   data_set.write_database(sqlite_path, max_missing=0.5)

   profile_tsv_path = file_root + '_profiles.tsv'    
   data_set.write_profile_tsv(profile_tsv_path, profiles=['init','zfill','latent'],
                              markers=['training','prediction','suborganelle'])
