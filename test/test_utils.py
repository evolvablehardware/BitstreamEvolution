def compare_files(path1, path2):
    '''
    Reads in the contents of two files as a string list of lines, and returns on the equality of each line
    '''
    f1 = open(path1, 'r')
    f2 = open(path2, 'r')
    lines1 = f1.readlines()
    lines2 = f2.readlines()
    f1.close()
    f2.close()
    assert len(lines1) == len(lines2)
    for i in range(len(lines1)):
        l1 = lines1[i].rstrip()
        l2 = lines2[i].rstrip()
        assert l1 == l2

# Prevent this function from being run as a test
compare_files.__test__ = False