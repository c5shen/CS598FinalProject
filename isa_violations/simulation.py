import sys, os
sys.path.append('../')
from compareTree import Node, readTree
import numpy as np
import pandas as pd

if not os.path.isdir('SCS'):
    os.mkdir('SCS')

# first read in the simulation tree and simulate 10000 cells from the
# tree nodes
num_cells = 10000
rep = 6
k = 7   # 7 mutations

for i in range(1, rep+1):
    print("On rep", i)
    sim_tree = readTree('SIM_TREES/rep{}.all.tre'.format(i))
    nodes = sim_tree.getAllNodes()

    # np.random.choice with replacement
    np.random.seed(2170 * i + 1234)
    chosen_nodes = np.random.choice(nodes, size=num_cells, replace=True)

    df_list = []
    columns = ['cellID/mutID'] + ['mut' + str(x) for x in range(k)]
    cell_ind = 0
    # generate the matrix based on chosen nodes (cells)
    for cell in chosen_nodes:
        row = ['cell' + str(cell_ind)] + [0] * k
        for label in cell.label:
            row[int(label)+1] = 1
        df_list.append(row)
        cell_ind += 1

    df = pd.DataFrame(df_list, columns=columns)
    
    df.to_csv('SCS/n=10000_k=7_rep{}.tsv'.format(i), sep='\t', index=False)


# create cases for testing
ns = [10, 20, 40, 100]
missing_rates = [0, 0.125, 0.25, 0.5]
beta = [0, 0.2, 0.4]

for n in ns:
    for b in beta:
        for m in missing_rates:
            outdir = 'SCS/n={}/b={}/{}'.format(n, b, m)
            if not os.path.isdir(outdir):
                os.system('mkdir -p {}'.format(outdir))
            for i in range(1, rep+1):
                scs_file = 'SCS/n=10000_k=7_rep{}.tsv'.format(i)
                df = pd.read_csv(scs_file, sep='\t', header=0)

                # random state
                random_state = 2170 * (i+7) + 1234
                sub_df = df.sample(n=n, axis=0, random_state=random_state)

                # missing rate/FN introduction
                masked_sub_df = sub_df.copy(deep=True)
                masked_sub_df['cellID/mutID'] = ['cell' + str(x) 
                        for x in range(n)]

                for row in range(masked_sub_df.shape[0]):
                    # FN changes - from 1 to 0
                    fn_changes = np.random.binomial(n=1, p=b, size=k)
                    fn_index = np.flatnonzero(fn_changes) + 1
                    masked_sub_df.iloc[row, list(fn_index)] = 0

                    # missing rate changes - from 1/0 to '?'
                    missing_changes = np.random.binomial(n=1, p=m, size=k)
                    m_index = np.flatnonzero(missing_changes) + 1
                    masked_sub_df.iloc[row, list(m_index)] = '?'
                
                masked_sub_df.to_csv(outdir + '/rep{}.tsv'.format(i),
                        sep='\t', index=False)
