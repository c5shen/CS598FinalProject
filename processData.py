import numpy as np
import os, sys, re
import pandas as pd

batch = [1, 2, 3]
ver = ['a', 'b', 'c', 'd']
sample_sizes = [10, 20, 40, 100]

skips = ['sim1a']

for b in batch:
    for v in ver:
        path = './sim{}{}'.format(b, v)
        if not os.path.isdir(path):
            continue
        
        if 'sim{}{}'.format(b, v) in skips:
            continue
        
        scs_path = path + '/SCS'
        
        # there exists 100 replicates, each contains 10000 SC sequencing data
        # 1) read in each replicate
        # 2) subsample to 100 SCS
        # 3) index it with cell ID (current missing)

        for i in range(1, 101):
            print("On {}".format(i), flush=True, end='\r')
            scs_file = scs_path + '/n7_S{}_k1_FN0.00_p0_SCS.csv'.format(i)
            df = pd.read_csv(scs_file, header=0)
            
            # random subsample of df
            random_state = 2170 + i * 123
            
            for sample_size in sample_sizes:
                outdir = scs_path + '/n={}/0'.format(sample_size)
                if not os.path.isdir(outdir):
                    os.system('mkdir -p {}'.format(outdir))

                sub_df = df.sample(n=sample_size, axis=0, random_state=random_state)
                
                # should be of shape (sample_size, 7)
                # add a new column, indicating cell ID
                num_mut = sub_df.shape[1]
                cell_id = ['cell' + str(x) for x in range(sample_size)]
                sub_df['cellID/mutID'] = cell_id

                # rename columns to ['cellID', 'mut0', 'mut1', ...]
                col_names = ['mut' + str(x) for x in range(num_mut)] \
                        + ['cellID/mutID'] 
                col_names_ordered = ['cellID/mutID'] \
                        + ['mut' + str(x) for x in range(num_mut)]
                sub_df.columns = col_names
                sub_df = sub_df[col_names_ordered]

                # save to local as tab separated version
                sub_df.to_csv(outdir + '/rep{}.tsv'.format(i), sep='\t',
                        index=False)

                ################# random sample of 12.5%/25%/50% of mutations
                ################# to be masked as '?'
                for frac in [0.125, 0.25, 0.5]:
                    outdir = scs_path + '/n={}/{}'.format(sample_size, frac)
                    if not os.path.isdir(outdir):
                        os.system('mkdir -p {}'.format(outdir))

                    masked_sub_df = sub_df.copy(deep=True)
                    
                    for row in range(masked_sub_df.shape[0]):
                        for col in range(1, masked_sub_df.shape[1]):
                            change = np.random.binomial(n=1, p=frac)
                            if change:
                                masked_sub_df.iloc[row, col] = '?'
                    masked_sub_df.to_csv(outdir + '/rep{}.tsv'.format(i),
                            sep='\t', index=False)
