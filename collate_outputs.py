import argparse
import os
from glob import glob
from choragraph import ChoragraphDataSet

def main():
    parser = argparse.ArgumentParser(description="Finalize Choragraph datasets; calculate p-values, make best-class predictions and construct filled-in profiles.")
    
    # Mandatory pattern argument with no default
    parser.add_argument('-d', '--datasets', required=True,
                        help="Glob pattern for input dataset files (e.g., 'datasets/Arabidopsis_*.npz')")
    
    # Optional arguments with short and long variants
    parser.add_argument('-m', '--comparison-markers', default=None,
                        help="Path to external comparison markers CSV file (optional)")
    parser.add_argument('--id-col', type=int, default=1, help="ID column index in external CSV")
    parser.add_argument('--class-col', type=int, default=3, help="Class column index in external CSV")
    parser.add_argument('--score-col', type=int, default=4, help="Score column index in external CSV")
    parser.add_argument('-t', '--score-thresh', type=float, default=0.9999, help="Score threshold for external markers")
    parser.add_argument('-f', '--max-missing', type=float, default=0.5, help="Maximum missing data fraction allowed in a profile")
    
    # Boolean flag for resetting 2D projections
    parser.add_argument('--no-reset', action='store_false', dest='reset_2d_projections',
                        help="Disable resetting 2D projections")
    parser.set_defaults(reset_2d_projections=True)

    args = parser.parse_args()

    data_paths = glob(args.data_pattern)
    if not data_paths:
        print(f"Warning: No files matched the pattern: {args.data_pattern}")
        return

    for data_path in data_paths:
        # Reload .npz data into Python 
        data_set = ChoragraphDataSet(data_path, aux_marker_key='suborganelle')
        data_set.info(f'Finalising {data_path}')  
       
        # Add external set of markers to compare with if provided
        if args.comparison_markers:
            mkey = data_set.comparison_markers_key
            data_set.add_scored_markers(mkey, args.comparison_markers, id_col=args.id_col, class_col=args.class_col,
                                        score_col=args.score_col, score_thresh=args.score_thresh)
       
        if args.reset_2d_projections:
            data_set.reset_2d_proj()
       
        if not data_set.has_predictions:
            data_set.warn(f'Dataset at {data_path} has no mixed class and reconstruction predictions. The dnn_workflow.py script should be run first.')
            continue
       
        if not data_set.has_array_key('pval'):
            data_set.info(f'Calculating p-values for {data_path}')
            data_set.make_pvalues()

        if not data_set.has_array_key('prediction'):
            data_set.info(f'Making class predictions for {data_path}')
            data_set.make_class_predictions()
               
        if not data_set.has_profile_key('zfill'):
            data_set.info(f'Reconstructing profiles for {data_path}')
            data_set.make_profile_predictions(max_missing=args.max_missing)

        file_root = os.path.splitext(data_path)[0]
        sqlite_path = file_root + '.sqlite' 
        data_set.info(f'Making SQLite3 database {sqlite_path}')  
        data_set.write_database(sqlite_path, max_missing=args.max_missing)

        profile_tsv_path = file_root + '_profiles.tsv'    
        data_set.write_profile_tsv(profile_tsv_path, profiles=['init','zfill','recon'],
                                  markers=['training','prediction','suborganelle'])

if __name__ == '__main__':
    main()
