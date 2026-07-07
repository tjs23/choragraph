import argparse
import os
import logging

# Suppress logging warnings before importing tensorflow-bound modules
logging.disable(logging.WARNING)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import numpy as np
from glob import glob
from choragraph import ChoragraphDataSet
from dnn import dnn_model
from general_util import info, warn, plot_training_history

# Global configuration defaults
DEFAULT_NOMIX_ORGANELLES = ['PROTEASOMAL', 'RIBOSOMAL']

def main():
    parser = argparse.ArgumentParser(description="Process multiple Choragraph dataset outputs.")
    
    # Path and pattern configuration (Updated: mandatory with no default)
    parser.add_argument('-d', '--datasets', required=True,
                        help="Glob pattern for input dataset files (e.g., 'datasets/Arabidopsis_*.npz')")
    parser.add_argument('-m', '--models-dir', default='models',
                        help="Directory to store model weights and training plots")
    
    # Execution and hyperparameter configurations
    parser.add_argument('--no-overwrite', action='store_false', dest='overwrite',
                        help="Disable overwriting existing predictions and models")
    parser.set_defaults(overwrite=True)
    
    parser.add_argument('-n', '--n-models', type=int, default=10, help="Number of models to train")
    parser.add_argument('-l', '--nlayers-att', type=int, default=4, help="Number of attention layers")
    parser.add_argument('-b', '--batch-size', type=int, default=64, help="Batch size for training")
    parser.add_argument('-e', '--n-epochs', type=int, default=75, help="Number of epochs to train")
    parser.add_argument('-s', '--n-infer-samples', type=int, default=100, help="Inference samples per model")
    parser.add_argument('-f', '--max-nan-frac', type=float, default=0.35, help="Maximum allowed fraction of NaNs")
    parser.add_argument('-x', '--n-mix', type=int, default=250, help="Number of mixes")
    
    nomix_str = ", ".join(DEFAULT_NOMIX_ORGANELLES)
    parser.add_argument('-n', '--nomix-organelles', nargs='+', default=DEFAULT_NOMIX_ORGANELLES,
                        help=f"Space-separated list of organelles to exclude from mixing. Default: {nomix_str}")

    args = parser.parse_args()

    # Ensure models directory exists
    if not os.path.exists(args.models_dir):
        os.makedirs(args.models_dir)

    data_paths = glob(args.data_pattern)
    if not data_paths:
        print(f"Warning: No files matched the pattern: {args.data_pattern}")
        return

    # Process all paths from glob
    for data_path in data_paths:
        data_set = ChoragraphDataSet(data_path)
        
        if data_set.has_predictions and not args.overwrite:
            info(f'Prediction data already present for {data_path}')
           
        prof_dim = data_set.train_profiles.shape[-1]
     
        if prof_dim > 64:
            ndim_compress = 64
        elif prof_dim > 32:
            ndim_compress = 32
        else:
            ndim_compress = 16
          
        max_nan = int(args.max_nan_frac * prof_dim)    
        
        model_paths = [os.path.join(args.models_dir, f'DNN_Model_v{m:02d}_{data_set.run_tag}.weights.h5') for m in range(args.n_models)]
        
        info(f'Fetching ensemble (size {args.n_models}) test/train data for {data_path}')
        
        valid, idx_chunks, valid_profiles, valid_class_labels = data_set.get_train_test_data(n_chunks=args.n_models, max_nan=max_nan)
        
        n = len(valid)
        m = np.count_nonzero(valid)
        
        marker_klasses = []
        marker_idx = np.zeros(n)
        valid_marker_idx = np.zeros(m)
        
        for m in range(args.n_models):
            test_idx = idx_chunks[m]
            valid_marker_idx[test_idx] = m+1
            marker_klasses.append(f'group_{m+1}')
        
        marker_idx[valid] = valid_marker_idx
        
        data_set.set_marker_data(data_set.train_groups_key, marker_idx, marker_klasses)
        
        class_names = data_set.train_labels
        
        nomix_classes = [class_names.index(x) for x in args.nomix_organelles]
        
        info(f'Not mixing classes : {" ".join(args.nomix_organelles)}')
        
        # Train models
        for m, model_path in enumerate(model_paths):
            if os.path.exists(model_path) and not args.overwrite:
                info(f'Found existing {model_path}')
                continue
                
            test_idx = idx_chunks[m]
            train_idx = np.concatenate(idx_chunks[:m] + idx_chunks[m+1:])    
            
            info(f'Training model {m+1} with {len(train_idx):,} profiles, testing with {len(test_idx):,}')
            
            history = dnn_model.train_model(model_path, test_idx, train_idx, valid_profiles, valid_class_labels,
                                            data_set.replica_cols, n_mix=args.n_mix, nomix_classes=nomix_classes, n_epochs=args.n_epochs,
                                            batch_size=args.batch_size, ndim_compress=ndim_compress, nlayers_att=args.nlayers_att)
        
            info(f'Saved {model_path}')

            history_path = os.path.splitext(model_path)[0] + '_training.png'
     
            plot_training_history(history, file_path=history_path)

        # Make inference for whole proteome for each model
        profiles = data_set.train_profiles 
        klasses = data_set.train_markers
        
        pred_classes = []
        recon_profiles = []
        latent_profiles = []
        
        for m, model_path in enumerate(model_paths):
            info(f'Working on model {m} : {model_path}')
            class_vecs, recon_vecs, latent_vecs = dnn_model.make_inference(model_path, profiles, data_set.replica_cols,
                                                                           klasses, ndim_compress=ndim_compress,
                                                                           nlayers_att=args.nlayers_att, n_rep=args.n_infer_samples)
     
            pred_classes.append(class_vecs)
            recon_profiles.append(recon_vecs)
            latent_profiles.append(latent_vecs)
        
        # Aggregate and store model outputs
        info(f'Aggregating results to {data_path}')
        
        pred_classes = np.concatenate(pred_classes, axis=1)
        recon_profiles = np.concatenate(recon_profiles, axis=1)
        latent_profiles = np.concatenate(latent_profiles, axis=1)
     
        recon_profiles = np.median(recon_profiles, axis=1)
        latent_profiles = latent_profiles.mean(axis=1)
        
        data_set.set_profile_data(data_set.recon_profile_key, recon_profiles)
        data_set.set_profile_data(data_set.latent_profile_key, latent_profiles)
     
        data_set.set_pred_class_data(data_set.class_ensemble_key, pred_classes, data_set.train_markers)

if __name__ == '__main__':
    main()
