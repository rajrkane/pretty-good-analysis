# Bruce A. Maxwell
# Spring 2015 updated Spring 2018 for Python3
# CS 251 Project 7
#
# Test file for kmeans_numpy function
# Expected output is below
#
# Codebook
#
# [[ 4.059737    4.08785958]
#  [ 2.03991735  2.06976598]]
#
# Codes
#
# [1 1 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0]


import sys
import data
import analysis as an

def main(argv):
    if len(argv) < 2:
        print( 'Usage: python %s <all numeric CSV file>' % (argv[0]))
        exit(-1)

    try:
        d = data.Data( argv[1] )
    except:
        print( 'Unable to open %s' % (argv[1]))
        exit(-1)

    codebook, codes, errors = an.kmeans_numpy( d, d.get_headers(), 2 )

    print( "\nCodebook\n")
    print( codebook)

    print( "\nCodes\n")
    print( codes)

if __name__ == "__main__":
    main(sys.argv)    
        
