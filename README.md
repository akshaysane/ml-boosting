# Boosting Classifier

This classifier was part of a [project](http://www.ccs.neu.edu/home/jaa/CS6140.11F/Homeworks/hw.04.html) for my Fall 2011 [machine learning class](http://www.ccs.neu.edu/home/jaa/CS6140.11F/).

To run, put *spambase.data* from the UCI [spambase dataset](http://archive.ics.uci.edu/ml/datasets/Spambase) into the same directory as *homework4.py*.

    $ python2 homework4.py --beststump

This will create up to ''''4140 * 57 = 236037'''' decision stumps and boost with the optimal one until a convergence criterion is met, using folds 2..10 to train and fold 1 to test. Data for a ROC curve is written on exit.

#### Options:

    homework4.py
        --folds    NUM # How many folds to make from the dataset (default: 10).
        --testfold NUM # Which fold index to use for testing (default: 0).
        --rounds   NUM # How many rounds to run for (default: until convergence).
        --beststump    # Choose the optimal decision stump (default: random choice).

See [my analysis](https://docs.google.com/document/d/1PBH77j165_xkoVMOm9Dscf_z7RMGv4OM5PpaXmeXiNY/edit) for a discussion of the results.

-- [PLR](http://f06mote.com)
