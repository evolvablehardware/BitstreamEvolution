def compare_files(path1, path2):
    """
    Reads in the contents of two files as a string list of lines, and returns on the equality of each line
    """
    with open(path1) as f1, open(path2) as f2:
        lines1 = f1.readlines()
        lines2 = f2.readlines()
    assert len(lines1) == len(lines2)
    for i in range(len(lines1)):
        l1 = lines1[i].rstrip()
        l2 = lines2[i].rstrip()
        assert l1 == l2


# Prevent this function from being run as a test
compare_files.__test__ = False
