import sys, os, glob
from schisome import ChoragraphDataSet
from matplotlib.colors import LinearSegmentedColormap

#run_tag = 'Aug25v1'
#run_tag = 'Feb26v1'
run_tag = 'Jun26v2'

data_paths = glob.glob(f'datasets/*_PBS+CO3_{run_tag}.npz')
#data_paths = ['/data/choragraph/Arabidopsis_PBS_May26v3.npz']

umap_titles = ['Input', 'Missing-filled', 'Latent']


if not os.path.exists('plots'):
    os.mkdir('plots')

if not os.path.exists('plots/dual'):
    os.mkdir('plots/dual')

if not os.path.exists('tables'):
    os.mkdir('tables')

datasets = []
for data_path in data_paths:
  
  if f'_PBS+CO3_{run_tag}.npz' in data_path:
      name = 'Combined Samples'
      src = 'Arabidopsis_PBS+CO3'
  
  elif f'_CO3_{run_tag}.npz' in data_path:
      name = 'CO3 Samples'
      src = 'Arabidopsis_CO3'
  
  else:
      name = 'Unwashed Samples'
      src = 'Arabidopsis_PBS'
    
  data_set = ChoragraphDataSet(data_path, name=name, source_tag=src)  
  datasets.append(data_set)
  

sparse_classes = ['EXTRACELLULAR','CORTEX','PROTEASOMAL','RIBOSOMAL']

for data_set in datasets:

  #data_set.reset_2d_proj()
  
  tag = data_set.source_tag
  
  #tagm_path = 'markers/Arabidopsis_PBS_Jun26v3_nonnan_profiles_TAGM_MCMC_predictions.csv'
  #mkey = data_set.comparison_markers_key
  #data_set.add_scored_markers(mkey, tagm_path, id_col=1, class_col=3, score_col=4, score_thresh=0.9999)
  
  #print(data_set.marker_keys)
    
  ## General & overview  
  
  #data_set.plot_overview(save_path=f'plots/{tag}_classification_overview.pdf') # Ring pie charts
  #data_set.plot_l2_loss_distrib()
  #data_set.plot_ave_profiles('prediction',  save_path=f'plots/{tag}_ave_pred_profiles.pdf')  
  #data_set.plot_ave_profiles(data_set.train_markers_key, save_path=f'plots/{tag}_ave_train_profiles.pdf')
  #data_set.plot_prediction_scatter(save_paths=f'plots/{tag}_DNNscorescatters.pdf',
  #                                 protein_ids=['F4IFM7','Q0WVR7','Q9LMK6','Q67ZU1'])
    
    
  # # Reconstruction
  #data_set.reconstruction_overview(tag)
  #data_set.plot_reconstruction(save_path=f'plots/{tag}_profile_reconstruction_{{}}.pdf', ncols=3) 
  
  ## Plot denoise vs original 
  
  cmap = LinearSegmentedColormap.from_list(name='CMAP01', colors=['#DDDDDD', '#FF8000', '#FF0000','#000000'], N=25)
  #data_set.plot_umap_2d([data_set.train_profile_key, data_set.zfill_profile_key], 'completeness', ['Original', 'Missing-filled'],
  #                      title=f'{data_set.name} UMAP Missing data reconstruction', spot_size=10,
  #                      save_path=f'plots/{tag}_compare_zerocount.pdf', cmap=cmap)

  #data_set.plot_umap_2d([data_set.latent_profile_key], ['completeness','training'], ['Latent : completeness', 'Latent : training compartment'],
  #                      title=f'{data_set.name} UMAP Missing data reconstruction', spot_size=10,
  #                      save_path=f'plots/{tag}_latent_zerocount.pdf', cmap=cmap)
  
  # # Dual localisaton
  #data_set.plot_duality_vs_completeness(save_path=f'plots/{tag}_duality_vs_completeness.pdf')
  # # data_set.plot_dual_localisation_overview(save_path=f'plots/{tag}_dual_matrix.png',
  # #                                          tsv_path=f'tables/{tag}_duals_list.tsv')  
  
  #data_set.plot_duals_analysis(tag, save_path=f'plots/{tag}_dual_count_matrix.pdf',
  #                             table_path=f'tables/{tag}_dual_candidates.tsv', alt_method='TAGM')
  
  cmap1 = LinearSegmentedColormap.from_list(name='CMAP01', colors=['#DDDDDD', '#FF0000', '#000000'], N=25)
  cmap2 = LinearSegmentedColormap.from_list(name='CMAP02', colors=['#DDDDDD', '#8080FF', '#0000FF'], N=25)
  
  #data_set.plot_umap_2d([data_set.recon_profile_key], ['singularity','duality','log_pval2'],
  #                      ['Singleness','Dualness','2-class log10(p-value)'],
  #                      title=f'{data_set.name} UMAP', #legend_title='Singleness',
  #                      save_path=f'plots/{tag}_singleness_dualness.pdf',
  #                      cmap=[cmap1, cmap1, cmap2], spot_size=10)
  
  #classes = ['ER', 'GOLGI', 'PM', 'TGN', 'EXTRACELLULAR', 'NUCLEUS']
  #data_set.plot_class_restricted_umap_2d(classes, plot_size=7.0, max_missing=0.35, min_score=0.30, title='Secretory System',
  #                                       save_path=f'plots/{tag}_UMAP_secretory_mixing.pdf')
  
  # # These are very detailed Dual localisation plots
  data_set.plot_dual_proj_2d(data_set.recon_profile_key, title=f'UMAP Denoised {data_set.name} : Dual localisation',
                             save_path=f'plots/dual/{tag}_dual_loc_denoised_{{}}.pdf')
                             
  # # Marker pruning 
  #data_set.save_pruned_table(tsv_path=f'tables/{tag}_pruned_list.tsv') 
  
  #data_set.plot_umap_2d([data_set.train_profile_key], ['pruned_organelle','training'], ['Markers Removed','Markers Used'],
  #                      title=f'Input Data UMAP : Training Marker Cull', spot_size=16, min_nonzero=0.8,
  #                      save_path=f'plots/{tag}_marker_prune.pdf')
  
  
  
  # # Metrics & asessment
  #data_set.plot_confusion_matrix(data_set.train_markers_key,
  #                               save_path=f'plots/{tag}_confusion_matrix_train.pdf',
  #                               marker_title=f'{data_set.name} : Train Class')
                                
  #data_set.plot_confusion_matrix(data_set.raw_markers_key,
  #                               save_path=f'plots/{tag}_confusion_matrix_unfiltered.pdf',
  #                               marker_title=f'{data_set.name} : Unfiltered Marker Class')
  
  #data_set.plot_pr_curve(tag, use_svm=True, save_path=f'plots/{tag}_SVM_PRcurves_IncPruned.png')
  #data_set.plot_pr_curve(tag, use_svm=False, save_path=f'plots/{tag}_PRcurves_IncPruned.pdf')
  
  #data_set.plot_umap_2d([data_set.recon_profile_key], ['prediction','svm_prediction', data_set.comparison_markers_key],
  #                      ['Choragraph DNN','SVM','TAGM'],
  #                      title=f'{data_set.name} UMAP', #legend_title='Singleness',
  #                      cmap=[cmap1, cmap1, cmap2], spot_size=10,
  #                      save_path=f'plots/{tag}_UMAP_prediction_method_comp.pdf')
  


  #data_set.plot_contingency_table('prediction', 'svm_prediction', use_undef=True,
  #                                save_path=f'plots/{tag}_comparison_matrix_SVM.pdf',
  #                                marker_title=f'{data_set.name} : DNN prediction',
  #                                pred_title=f'{data_set.name} : SVM prediction')

  #data_set.plot_confusion_matrix(data_set.raw_markers_key, use_svm=True,
  #                               save_path=f'plots/{tag}_confusion_matrix_SVM.pdf',
  #                               marker_title=f'{data_set.name} : Train class',
  #                               pred_title=f'{data_set.name} : SVM prediction')
  
  #data_set.make_class_predictions()
  #data_set.svm_fit_predict(prob_thresh=0.8)
  #data_set.plot_duals_contingency_table(data_set.comparison_markers_key, use_undef=True,
  #                                     save_path=f'plots/{tag}_duals_TAGM_pred.pdf',
  #                                     marker_title=f'DNN prediction',
  #                                     pred_title=f'TAGM prediction')

  #data_set.plot_duals_contingency_table('svm_prediction', use_undef=True,
  #                                      save_path=f'plots/{tag}_duals_SVM_pred.pdf',
  #                                      marker_title=f'DNN prediction',
  #                                      pred_title=f'SVM prediction')
                                        
  #data_set.plot_dual_proj_2d(data_set.recon_profile_key, title=f'UMAP Denoised {data_set.name} : Dual localisation',
  #                           save_path=f'plots/dual/{tag}_dual_loc_denoised_{{}}.png')
                             


  #data_set.plot_contingency_table('prediction',
  #                                data_set.comparison_markers_key, use_undef=True,
  #                                save_path=f'plots/{tag}_confusion_matrix_comp_method.pdf',
  #                                marker_title=f'{data_set.name} : DNN prediction',
  #                                pred_title=f'{data_set.name} : TAGM prediction')  
  
  #data_set.plot_umap_2d([data_set.recon_profile_key], ['prediction',data_set.comparison_markers_key],
  #                      ['Choragraph DNN','TAGM'],
  #                      title=f'{data_set.name} UMAP', #legend_title='Singleness',
  #                      cmap=[cmap1, cmap1, cmap2], spot_size=10,
  #                      save_path=f'plots/{tag}_UMAP_TAGM_method_comp.pdf')
                        
  # # Prediction assessment
  
  ##data_set.make_class_predictions()
  

  #marker_keys = [data_set.train_markers_key, 'prediction', 'log_pval1'] #, data_set.aux_markers_key]  
  #umap_titles = ['Training classes', 'Single prediction classes', '1-Class log10(p-value)'] # , 'Suborganelle']  
  #cmap = LinearSegmentedColormap.from_list(name='CMAP01', colors=['#000000', '#0088FF','#FF0000'], N=25)
  
  #data_set.reset_2d_proj()
  #data_set.plot_umap_2d(data_set.recon_profile_key, marker_keys, umap_titles,
  #                      title=f'{data_set.name} Denoised UMAP', cmap=cmap,
  #                      save_path=f'plots/{tag}_classes_reconstructed.pdf')
                       
  #data_set.plot_umap_2d(data_set.latent_profile_key, marker_keys, umap_titles,
  #                      title=f'{data_set.name} Latent UMAP', cmap=cmap,
  #                      save_path=f'plots/{tag}_classes_latent.pdf')

  #data_set.plot_umap_2d(data_set.train_profile_key, marker_keys, umap_titles,
  #                      title=f'{data_set.name} Original UMAP', cmap=cmap,
  #                      save_path=f'plots/{tag}_classes_latent.pdf')

  #data_set.plot_umap_2d(data_set.zfill_profile_key, marker_keys, umap_titles,
  #                      title=f'{data_set.name} Reconstructed UMAP', cmap=cmap,
  #                      save_path=f'plots/{tag}_classes_latent.pdf')
  
  
  
   
  
  
  #classes = ['CYTOSOL', 'CHLOROPLAST', 'MITOCHONDRION', 'PEROXISOME']
  #data_set.plot_class_restricted_umap_2d(classes, plot_size=8.0, max_missing=0.35, min_score=0.30)
  
  #classes = ['NUCLEUS', 'ER', 'PM', 'CYTOSOL']
  #data_set.plot_class_restricted_umap_2d(classes, plot_size=8.0, max_missing=0.35, min_score=0.30)

  #classes = ['EXTRACELLULAR', 'TGN', 'CHLOROPLAST', 'ER','GOLGI']
  #data_set.plot_class_restricted_umap_2d(classes, plot_size=8.0, max_missing=0.35, min_score=0.30)
                        
  continue

  """                             
  data_set.plot_mixed_ave_profiles('CYTOSOL', 'MITOCHONDRION', save_paths=save_paths)
  data_set.plot_mixed_ave_profiles('CHLOROPLAST', 'MITOCHONDRION', save_paths=save_paths)
  data_set.plot_mixed_ave_profiles('GOLGI', 'TGN', save_paths=save_paths)
  data_set.plot_mixed_ave_profiles('PM', 'TGN', save_paths=save_paths)
  data_set.plot_mixed_ave_profiles('PM', 'ER', save_paths=save_paths)
  data_set.plot_mixed_ave_profiles('CYTOSOL', 'CHLOROPLAST', save_paths=save_paths)
  data_set.plot_mixed_ave_profiles('CYTOSOL', 'NUCLEUS', save_paths=save_paths)
  """

  
