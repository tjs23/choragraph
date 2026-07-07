import argparse
import os
from glob import glob
from schisome import ChoragraphDataSet

# Global configuration defaults
DEFAULT_SPARSE_CLASSES = ['EXTRACELLULAR', 'CORTEX', 'PROTEASOMAL', 'RIBOSOMAL']

def main():
    parser = argparse.ArgumentParser(description="ofiles into Choragraph data sets from the command line.")
    
    # Required arguments with short and long variants
    parser.add_argument('-r', '--run-tag', required=True, 
                        help="Identifier for the current run (e.g., Arabidopsis_Jun26)")
    parser.add_argument('-p', '--profile-pattern', required=True, 
                        help="Glob pattern for profile TSV files (e.g., 'profiles/*_replica[0-7].tsv')")
    parser.add_argument('-o', '--organelle-markers', required=True, 
                        help="Path to the organelle markers CSV file")
    parser.add_argument('-u', '--suborganelle-markers', required=True, 
                        help="Path to the suborganelle markers CSV file")
    
    # Optional arguments with short and long variants
    sparse_classes_str = ", ".join(DEFAULT_SPARSE_CLASSES)
    parser.add_argument('-c', '--sparse-classes', nargs='+', default=DEFAULT_SPARSE_CLASSES,
                        help=f"Space-separated list of sparse classes to prune. Default: {sparse_classes_str}")
    parser.add_argument('-d', '--output-dir', default='datasets', 
                        help="Directory where output files will be saved")

    args = parser.parse_args()

    # Ensure output directory exists
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # Find profile paths using the provided glob pattern
    profile_paths = glob(args.profile_pattern)
    if not profile_paths:
        print(f"Warning: No files matched the pattern: {args.profile_pattern}")

    # Construct the base data path
    data_path = os.path.join(args.output_dir, f'{args.run_tag}.npz')

    # Initialize dataset with fixed 'suborganelle' label
    dataset = ChoragraphDataSet(data_path, args.run_tag, aux_marker_key='suborganelle')
    dataset.add_raw_profiles(profile_paths)
    
    # Add markers with fixed 'organelle' and 'suborganelle' keys
    dataset.add_markers('organelle', args.organelle_markers)
    dataset.add_markers('suborganelle', args.suborganelle_markers)

    # Always prune using 'organelle' and 'training' inputs
    dataset.prune_markers('organelle', 'training', sparse_classes=args.sparse_classes)

    # Export profile TSVs
    profile_tsv_path = os.path.join(args.output_dir, f'{args.run_tag}_profiles.tsv')   
    dataset.write_profile_tsv(profile_tsv_path, profiles=['init'], markers=['training'])

    nonnan_profile_tsv_path = os.path.join(args.output_dir, f'{args.run_tag}_nonnan_profiles.tsv')   
    dataset.write_profile_tsv(nonnan_profile_tsv_path, profiles=['init'], markers=['training'], max_nan=0)   
    
    print(f"Info: Wrote dataset to {data_path}")
    
if __name__ == '__main__':
    main()
