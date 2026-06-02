import sys, os, glob
from schisome import SchisomeDataSet

#run_tag = 'Aug25v1'
#run_tag = 'Feb26v1'

run_tag = 'May26v2'
data_paths = glob.glob(f'datasets/*_{run_tag}.npz')
umap_titles = ['Input', 'Zero-filled', 'Latent']

if not os.path.exists('plots'):
    os.mkdir('plots')

for data_path in data_paths:
    
  data_set = SchisomeDataSet(data_path)  
 
  tag = data_set.source_tag
  
     
  """
  # # # # # # # # 
  classes = ['ER', 'GOLGI', 'PM', 'TGN']
  data_set.plot_class_restricted_umap_2d(classes, plot_size=8.0, max_missing=0.35, min_score=0.30)
  
  classes = ['CYTOSOL', 'CHLOROPLAST', 'MITOCHONDRION', 'PEROXISOME']
  data_set.plot_class_restricted_umap_2d(classes, plot_size=8.0, max_missing=0.35, min_score=0.30)
  
  classes = ['NUCLEUS', 'ER', 'PM', 'CYTOSOL']
  data_set.plot_class_restricted_umap_2d(classes, plot_size=8.0, max_missing=0.35, min_score=0.30)

  classes = ['EXTRACELLULAR', 'TGN', 'CHLOROPLAST', 'ER','GOLGI']
  data_set.plot_class_restricted_umap_2d(classes, plot_size=8.0, max_missing=0.35, min_score=0.30)
  
  # # # # # # # # 
  """ 
  
  init_key = data_set.train_profile_key
  latent_key = data_set.latent_profile_key
  zfill_key = data_set.zfill_profile_key
  train_key = data_set.train_profile_key
  recon_key = data_set.recon_profile_key
  
  data_set.plot_reconstruction() 
  
  data_set.save_pruned_table(tsv_path=f'{tag}_pruned_list.tsv') 
  data_set.plot_overview() # Ring pie charts 
  
  
  data_set.plot_dual_localisation_overview(save_path=f'plots/{tag}_dual_matrix.png', tsv_path=f'{tag}_duals_list.tsv')  
  data_set.plot_pr_curve()  


  data_set.plot_umap_2d([zfill_key, latent_key], 'pval', ['Missing-reconstructed','Latent'],
                        title=f'UMAP Classification p-value',
                        save_path=f'plots/{tag}_pvalue.png')

  data_set.plot_umap_2d([zfill_key], 'duality', ['Missing-reconstructed'],
                        title=f'UMAP Duality',
                        save_path=f'plots/{tag}_duality.png')

  data_set.plot_umap_2d([zfill_key], 'nzeros', ['Missing-reconstructed'],
                        title=f'UMAP Missing data : zero-content',
                        save_path=f'plots/{tag}_zerocount.png')

  data_set.plot_umap_2d([init_key, zfill_key], 'nzeros', ['Original', 'Missing-reconstructed'],
                        title=f'UMAP Missing data reconstruction',
                        save_path=f'plots/{tag}_compare_zerocount.png')

  data_set.plot_umap_2d([train_key], ['pruned_organelle','training'], ['Removed','Retained'],
                        title=f'UMAP Training Marker Cull',
                        save_path=f'plots/{tag}_marker_prune.png')
                        
  umap_prof_keys = [train_key, zfill_key, latent_key]
  
  for marker_key in (data_set.train_markers_key, 'prediction', data_set.aux_markers_key):
      data_set.plot_umap_2d(umap_prof_keys, [marker_key], umap_titles,
                            title=f'UMAP {tag} {marker_key} classes',
                            save_path=f'plots/{tag}_{marker_key}.png')

  for prof_key in umap_prof_keys:
      data_set.plot_dual_proj_2d(prof_key, title=f'UMAP {prof_key} {tag} : Dual localisation',
                                 save_path=f'plots/{tag}_dual_loc_{prof_key}_{{}}.png')

  data_set.plot_contingency_table(data_set.train_markers_key,
                                  save_path=f'plots/{tag}_confusion_matrix_train.pdf',
                                  marker_title=f'{tag} : Train Class')
                                  
  data_set.plot_contingency_table(data_set.raw_markers_key,
                                  save_path=f'plots/{tag}_confusion_matrix_unfiltered.pdf',
                                  marker_title=f'{tag} : Unfiltered Marker Class')
  
  data_set.plot_contingency_table(data_set.train_markers_key,
                                  data_set.comparison_markers_key,
                                  save_path=f'plots/{tag}_confusion_matrix_comp_method.pdf',
                                  marker_title=f'{tag} : Train Class',
                                  pred_title=f'{tag} : TAGM prediction')
 
  data_set.plot_contingency_table(data_set.comparison_markers_key,
                                  save_path=f'plots/{tag}_confusion_matrix_comp_method.pdf',
                                  marker_title=f'{tag} : TAGM prediction')

  ### Make confusion matrix like plot for duals
  # Given number of pure and mixed
  # Split different p-val thresholds by diagonal 
  
  ### For each pair of organelles
  # Get dual localised
  # Get the top 10 smallest dual P-values
  # Include TAGEM pred
  # Make a table
  
  ### Compare zero-filled and imputed profiles
  # Calc correlation (or maybe other sim metric)
  # Find top most poorly correlating
  # Diagram of worst, superimosed
  # Table of predictions with and without imputation
  # - %top1, %top2, pval 
  
  
  if tag.startswith('Arabidposis'):
      data_set.plot_reconstruction()  
      data_set.plot_l2_loss_distrib()
  
      # Plots illustrating mixing of organelle pairs
 
      data_set.plot_ave_profiles('prediction',  save_paths=f'plots/{tag}_ave_pred_profile_{{}}.pdf')
      data_set.plot_ave_profiles(data_set.train_markers_key, save_paths=f'plots/{tag}_ave_train_profile_{{}}.pdf')
 
      save_paths = f'plots/{tag}_mix_ave_prof_{{}}_{{}}.pdf'
      data_set.plot_mixed_ave_profiles('CYTOSOL', 'MITOCHONDRION', save_paths=save_paths)
      data_set.plot_mixed_ave_profiles('CHLOROPLAST', 'MITOCHONDRION', save_paths=save_paths)
      data_set.plot_mixed_ave_profiles('GOLGI', 'ER', save_paths=save_paths)
      data_set.plot_mixed_ave_profiles('GOLGI', 'TGN', save_paths=save_paths)
      data_set.plot_mixed_ave_profiles('PM', 'TGN', save_paths=save_paths)
      data_set.plot_mixed_ave_profiles('PM', 'ER', save_paths=save_paths)
      data_set.plot_mixed_ave_profiles('CYTOSOL', 'CHLOROPLAST', save_paths=save_paths)
      data_set.plot_mixed_ave_profiles('CYTOSOL', 'NUCLEUS', save_paths=save_paths)

  if tag.startswith('Mouse'):
      data_set.plot_prediction_scatter(save_paths=f'plots/{tag}_DNNscorescatter_TAGEMexemplar.pdf',
                                       protein_ids=['G5E870','Q924C1','Q9WUA2','Q8VDR9'])

  
  
