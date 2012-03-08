def parse(argfmt, argv):
    '''Load arguments from an argument vector.

    Supports long-style optional arguments with optional options. For example,
    these optional arguments:
        --quiet     (boolean, default false)
        --width 10  (integer, default 20)
    Would be specified by:
        fmt = [('quiet', False, None),
               ('width', 20, int)]
    And given "--quiet --width 10" would result in:
        {'quiet':True,
         'width':10}
    Or given "" would result in:
        {'quiet':False,
         'width':20}

    Required arguments and positional arguments aren't supported.

    '''
    a = {}
    for name, default, coercion in argfmt:
        try:
            i = argv.index('--{}'.format(name))
            argv.pop(i)
            if coercion:
                a[name] = coercion(argv.pop(i))
            else:
                a[name] = not default
        except ValueError:
            a[name] = default
    return a
