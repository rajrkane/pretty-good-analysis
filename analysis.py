#!/usr/bin/env python
"""analysis.py: Incorporates data analysis capabilities into GUI. Python 2.7."""

import numpy as np
import csv
import data
import scipy.stats
import scipy.cluster.vq as vq
import scipy.spatial.distance as distance
import random
import sys

__author__ = "Raj Kane"
__version__ = "Project 7"
__date__ = "Spring 2018"


def data_range(headers, data):
    '''Takes in a Data object and a list of column headers and returns a list of 2-element
    lists with the min and max values for each column. Only deals with numeric types.'''
    cols = []
    for h in headers:
        cols.append(data.header2col[h])
    types = data.get_types()
    for c in cols:
        if (types[c].strip() != 'numeric'):
            print('Only numeric types allowed!')
            return
    D = data.columns_data(headers)
    mins_maxes = []
    for i in range(0,len(headers)):
        element = [float(np.min(D[:, i].astype(np.float))),float(np.max(D[:, i].astype(np.float)))]
        mins_maxes.append(element)
    return mins_maxes

def kmeans_numpy(d, headers, K, whiten=True):
    '''Takes in a Data object, a set of headers, and the number of clusters to create.
    Computes and return the codebook, codes, and representation error.'''
    A = d.columns_data(headers)
    W = vq.whiten(A)
    codebook, bookerror = vq.kmeans(W, K)
    codes, error = vq.vq(W, codebook)
    return codebook, codes, error

def kmeans_init(A, K):
    '''Selects K random rows from the data matrix A and return them as a matrix.'''
    K = int(K)
    num = A.shape[0]
    kMeans = []
    if (num < K):
        print 'Must have at least K data points.'
        return
    for i in range(K):
        kMeans.append(A[np.random.randint(0, num)].tolist())
    return np.matrix(kMeans)


def kmeans_classify(A, means):
    '''Given a data matrix A and a set of means in the codebook, returns a matrix of the
    ID of the closest mean to each point. Returns a matrix of the sum-squared distance
    between the closest mean and each point.'''
    indices = [] #indicates closest cluster mean to each data point
    moduli = []
    d = sys.maxint
    for a in A: #for every vector in A
        index = 0
        means_list = means.tolist()
        for i in range(len(means.tolist())):
                m = means.tolist()[i] #consider each mean
                if (distance.pdist(np.vstack((a, m)), 'euclidean')[0] < d):
                    d = distance.pdist(np.vstack((a, m)), 'euclidean')[0]
                    index = i
        indices.append([index])
        moduli.append([d])
        d = sys.maxint

    return np.matrix(indices), np.matrix(moduli)

def kmeans_algorithm(A, means):
    '''Given a data matrix A and a set of K initial means, compute the optimal cluster
    means for the data and an ID and an error for each data point.'''
    print means
    MIN_CHANGE = 1e-7
    MAX_ITERATIONS = 100
    D = means.shape[1] #number of dimensions
    K = means.shape[0] #number of clusters
    N = A.shape[0] #number of data points

    for i in range(MAX_ITERATIONS):
        codes = kmeans_classify(A, means)[0]
        newmeans = np.zeros_like(means) #new means given the cluster ids for each point
        counts = np.zeros((K, 1)) #how many points get assigned to each mean
        #compute new means
        for j in range(N):
            newmeans[codes[j, 0], :] += A[j, :]
            counts[codes[j, 0], 0] += 1.0
        for j in range(K):
            if counts[j, 0] != 0.0:
                newmeans[j, :] /= counts[j, 0]
            else:
                r = random.randint(0, A.shape[0])
                newmeans[j, :] = A[r, :]

        #test if the change is small enough and exit if it is
        diff = np.sum(np.square(means - newmeans))
        means = newmeans
        if diff < MIN_CHANGE:
            break

    codes, errors = kmeans_classify(A, means)
    return (means, codes, errors)

def kmeans(d, headers, K, whiten=True):
    '''Top-level kmeans function. Takes in a Data object, a set of headers, and 
    the number of clusters to create. Computes and returns the codebook, codes, 
    and representation errors.'''
    A = d.columns_data(headers).astype(float)
    if whiten:
        W = vq.whiten(A)
    else:
        W = A
    codebook = kmeans_init(W, K)
    codebook, codes, errors = kmeans_algorithm(W, codebook)
    return codebook, codes, errors


def kmeans_quality(errors, K):
    '''Takes in a matrix of errors returned by kmeans_algorithm and the number
    of clusters. Computes the description length.'''
    sse = np.dot(errors.T, errors)
    quality = sse + K * 0.5 * np.log2(errors.shape[0])
    return quality

def pca(d, headers, normalize=True):
    '''Takes in a Data object and list of column headers. Returns a data.PCAData object.
    By default, data will be prenormalized before pca analysis.'''
    if (normalize):
        A = normalize_columns_separately(headers, d)
    else:
        A = d.columns_data(headers)
    m = np.mean(A, axis=0)
    D = A - m
    U, S, V = np.linalg.svd(D, full_matrices=False)
    N = A.shape[0]
    eigenVals = (S * S) / (N - 1)
    projectedData = (V * D.T).T
    return data.PCAData(projectedData, V, eigenVals, m, headers)

def single_linear_regression(dataObj, indVar, depVar):
    '''Takes in a Data object, a singleton list of independent headers, and a singleton
    list of dependent headers. Returns single linear regression information, including
    slope, y intercept, r value, p value, standard error, range of independent data,
    and range of dependent data.'''
    columns = dataObj.columns_data([indVar[0], depVar[0]])
    (slope, yInt, rVal, pVal, stdErr) = scipy.stats.linregress(columns)
    indRange = data_range(indVar, dataObj)
    depRange = data_range(depVar, dataObj)
    return (slope, yInt, rVal, pVal, stdErr, indRange, depRange)

def linear_regression(dataObj,indHeaders,depVar):
    '''Takes in a Data object, a list of independent headers, and a dependent variable.
    Returns multiple linear regression information.'''
    y = np.matrix(dataObj.columns_data([depVar]))
    A = np.matrix(dataObj.columns_data(indHeaders))
    ones = np.ones((A.shape[0], 1))
    A = np.hstack((A, ones))
    AAinv = np.linalg.inv(np.dot(A.T, A))
    x = np.linalg.lstsq(A, y, rcond=None)
    b = x[0]
    N = y.shape[0]
    C = b.shape[0]
    df_e = N - C
    error = y - np.dot(A, b)
    sse = np.dot(error.T, error) / df_e
    stderr = np.sqrt(np.diagonal(sse[0, 0] * AAinv))
    t = b.T / stderr
    p = 2 * (1 - scipy.stats.t.cdf(abs(t), df_e))
    r2 = 1 - error.var() / y.var()
    b = [b.item(0), b.item(1), b.item(2)]
    sse = sse.item(0)
    t = [t.item(0), t.item(1), t.item(2)]
    p = [p.item(0), p.item(1), p.item(2)]
    return (b, sse, r2, t, p)

def mean(headers, data):
    '''Takes in a data object and list of headers. Returns the mean of appropriate data.'''
    cols = []
    for h in headers:
        cols.append(data.header2col[h])
    types = data.get_types()
    for c in cols:
        if (types[c].strip() != 'numeric'):
            print('Only numeric types allowed!')
            return

    D = data.columns_data(headers) #this is a np matrix
    means = []
    for i in range(0,len(headers)):
        element = np.mean(D[:, i].astype(np.float))
        means.append(element)
    return means

def median(headers, data):
    '''Takes in a data object and list of headers. Returns the median of appropriate data.'''
    cols = []
    for h in headers:
        cols.append(data.header2col[h])
    types = data.get_types()
    for c in cols:
        if (types[c].strip() != 'numeric'):
            print('Only numeric types allowed!')
            return

    D = data.columns_data(headers)
    medians = []
    for i in range(0,len(headers)):
        element = np.median(D[:, i].astype(np.float))
        medians.append(element)
    return medians

def stdev(headers, data):
    '''Take in a data object and list of headers. Returns the standard deviation of
    appropriate data.'''
    cols = []
    for h in headers:
        cols.append(data.header2col[h])
    types = data.get_types()
    for c in cols:
        if (types[c].strip() != 'numeric'):
            print('Only numeric types allowed!')
            return
    D = data.columns_data(headers) # this is a np matrix
    deviations = []
    for i in range(0,len(headers)):
        element = np.std(D[:, i].astype(np.float))
        deviations.append(element)
    return deviations

def normalize_columns_separately(headers, data):
    '''Takes in a Data object and a list of headers. Returns a matrix with each columns normalized
    so that the min is mapped to 0 and the max is mapped to 1.'''
    cols = []
    for h in headers:
        cols.append(data.header2col[h])
    types = data.get_types()
    for c in cols:
        if (types[c].strip() != 'numeric'):
            print('Only numeric types allowed!')
            return
    D = data.columns_data(headers)
    normcols_sep = D.copy()
    DR = data_range(headers,data)
    for i in range(0, len(DR)):
        a = DR[i][0] #min
        b = DR[i][1] #max
        r = b - a
        normcols_sep[:, i] = (D[:, i].astype(np.float) - a) / r
    return normcols_sep

def normalize_columns_together(headers, data):
    '''Takes in a Data object and a list of headers. Returns a matrix with columns normalized
    so that the min across columns is mapped to 0 and the max across columns is mapped to 1.'''
    cols = []
    for h in headers:
        cols.append(data.header2col[h])
    types = data.get_types()
    for c in cols:
        if (types[c].strip() != 'numeric'):
            print('Only numeric types allowed!')
            return
    D = data.columns_data(headers)
    normcols_tog = D.copy()
    DR = data_range(headers, data)
    mins = []
    maxes = []
    for twople in DR:
        mins.append(twople[0])
        maxes.append(twople[1])
    verymin = min(mins)
    verymax = max(maxes)
    R = verymax - verymin
    normcols_tog[:, :] = (D[:, :].astype(np.float) - verymin) / R
    return normcols_tog

def main(argv):
    if len(argv) < 4:
        print("Usage: python %s <data file> <independent header> <dependent header>")
        exit(-1)
    data_obj = data.Data( argv[1] )
    ind_header1 = argv[2]
    ind_header2 = argv[3]
    dep_header = argv[4]
    ind_headers = [ind_header1,ind_header2]

    results = linear_regression( data_obj, ind_headers, dep_header)

    # print 'b is ', results[0]
    # print 'sse is ', results[1]
    # print 'r2 is ', results[2]
    # print 't is ', results[3]
    # print 'p is ', results[4]

if __name__ == "__main__":
    main(sys.argv)
