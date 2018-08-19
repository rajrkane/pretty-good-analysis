# Stephanie Taylor
# clustering_test2.py
# Spring 2014, updated Spring 2018 for Python3 (Bruce)
import numpy as np
import analysis
import sys

def main(  ):
    mat = np.matrix( [[0.0,1.0],
                      [1.0,0.1],
                      [0.9,1.0],
                      [0.7,0.6]] )
    means = np.matrix( [[0.0,0.1], [0.95,1.0]] )
    N = mat.shape[0]
    F = mat.shape[1]
    k = means.shape[0]

    (cluster_idxs,cluster_distances) = analysis.kmeans_classify( mat, means )
    print( "for data:")
    print( mat)
    print( 'with "means":')
    print( means)
    print( "the indices are :")
    print( cluster_idxs)
    print( "and each point is this distance from the mean of its cluster:")
    print( cluster_distances)

if __name__ == '__main__':
    main()
