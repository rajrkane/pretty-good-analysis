#!/usr/bin/env python
"""data.py: Reads CSV files and stores data. Python 2.7."""

import numpy as np
import csv
import analysis
import copy

__author__ = "Raj Kane"
__version__ = "Project 7"
__date__ = "Spring 2018"


class Data:
    def __init__(self, filename=None):
        self.headers = []
        self.types = []
        self.data = None

        self.header2col = {}

        if filename != None:
            self.read(filename)

    def read(self, filename):
        fp = open(filename, "rU")
        csv_reader = csv.reader(fp, delimiter=',', quotechar='|')

        my_matrix = []

        #assign first row to headers, second to types
        self.headers = next(csv_reader)
        self.types = next(csv_reader)

        #remove whitespace in headers and types
        for i in range(0,len(self.headers)):
            self.headers[i] = self.headers[i].strip()
        for i in range(0, len(self.types)):
            self.types[i] = self.types[i].strip()

        #convert data into floats and add to my_matrix
        for line in csv_reader:
            v = []
            for i in range(0,len(self.types)):

                if self.types[i] == 'numeric':
                    line[i] = float(line[i])
                    v.append(line[i])

            my_matrix.append(v)
        self.data = np.matrix(my_matrix)

        #build numeric_headers and numeric_types
        numeric_headers = []
        numeric_types = []
        x = 0
        for i in range(0,len(self.types)):

            if self.types[i] == 'numeric':
                numeric_headers.append(self.headers[i])
                numeric_types.append(self.types[i])
                self.header2col.update({self.headers[i] : x})
                x += 1

        self.headers = numeric_headers
        self.types = numeric_types

    def write(self, filename, headers):
        '''Takes in a filename and an optional list of headers. Writes a
        selected set of headers to a specified file.'''
        f = open(filename, mode='w')
        for h in headers[:-1]:
            f.write(h + ',')
        f.write(headers[-1] + '\n')

        for h in headers[:-1]:
            f.write(self.types[self.header2col[h]] + ',')
        f.write(self.types[self.header2col[headers[-1]]] + '\n')

        for i in range(len(self.data.tolist())):
            for h in headers[:-1]:
                element = self.data.tolist()[i][self.header2col[h]]
                f.write(str(element) + ',')
            f.write(str(self.data.tolist[i][self.header2col[headers[-1]]]) + '\n')

    def addColumn(self, column, h, t):
        '''Takes in a column vector of data, a header, and a type. Adds column
        of data to data matrix.'''
        if len(column) != len(self.data.tolist()):
            print 'Column vector has wrong dimensions'
            return
        self.headers.append(h)
        self.types.append(t)
        self.header2col.update({h : len(self.headers)})

        dataTransposed = self.data.T.tolist()
        dataTransposed.append(column)
        self.data = np.matrix(dataTransposed)
        self.data = self.data.T

    def columns_data(self, columns):
        '''Takes in a list of headers. Returns matrix of data only from desired columns.'''
        matrix2 = self.data[:,self.header2col[columns[0]]] #initialize to first of the desired columns of data

        for column in columns[1:]:
            matrix2 = np.hstack([matrix2, self.data[:, self.header2col[column]]])
        return matrix2


    def get_headers(self):
    	return self.headers

    def get_types(self):
    	return self.types

    def get_num_dimensions(self):
    	return self.data.shape[1] 

    def get_num_points(self):
    	return self.data.shape[0] 

    def get_row(self, rowIndex):
    	return self.data[rowIndex,:]

    def get_value(self, header, rowIndex):
    	headerIndex = self.header2col[header]
    	return self.data[rowIndex, headerIndex]

    def get_dictionary(self, header):
            return self.header2col[header]

def main():
        print('in main loop')
        x = Data(filename = 'natural-gas-production-in-tonnes-1970-2015.csv')


class PCAData(Data):
    def __init__(self, projectedData, eVectors, eVals, means, headers, filename=None):
        Data.__init__(self)
        self.eVals = eVals #np matrix
        self.eVectors = eVectors #np matrix
        self.originalMeans = means #np matrix
        self.originalHeaders = headers #list. holds original headers
        self.finalData = projectedData #np matrix

        #populate all fields of Data class (self.headers,self.types,self.header2col)
        for counter, value in enumerate(headers):
            h = eval("'pca'+str(counter)")
            self.headers.append(h)
            self.types.append('numeric')
            self.header2col.update({h : counter})

        my_matrix = []
        for i in range(self.finalData.shape[0]):
            v = []
            for j in range(0, self.finalData.shape[1]):
                v.append(str(self.finalData[i, j]))
            my_matrix.append(v)
        self.data = np.matrix(my_matrix)

        if filename != None:
            print(filename)
            self.read(filename)

    def get_eigenvalues(self):
        return copy.deepcopy(self.eVals)

    def get_eigenvectors(self):
        return copy.deepcopy(self.eVectors)

    def get_original_means(self):
        return copy.deepcopy(self.originalMeans)

    def get_original_headers(self):
        return copy.deepcopy(self.originalHeaders)

class ClusterData(Data):
    def __init__(self, d, headers, K, codebook, codes, errors, filename=None):
        Data.__init__(self)
        self.K = K
        self.headers = headers
        self.codebook = codebook
        self.codes = codes
        self.errors = errors
        self.finalData = d
        for counter, value in zip(range(len(headers)), headers): # DOING THIS SAME THING WITH ENUMERATE CAUSED AN INFINITE LOOP
            h = headers[counter]
            self.headers.append(h)
            self.types.append('numeric')

            self.header2col.update({h : counter})

        my_matrix = []
        for i in range(self.finalData.shape[0]):
            v = []
            for j in range(0,self.finalData.shape[1]):
                v.append(str(self.finalData[i, j]))
            my_matrix.append(v)
        self.data = np.matrix(my_matrix)

        print self.header2col
        if filename != None:
            print(filename)
            self.read(filename)

    def get_K(self):
        return copy.deepcopy(self.K)

    def get_headers(self):
        return copy.deepcopy(self.headers)

    def get_codebook(self):
        return copy.deepcopy(self.codebook)

    def get_codes(self):
        return copy.deepcopy(self.codes)

    def get_errors(self):
        return copy.deepcopy(self.errors)


if __name__=="__main__":
        main()
