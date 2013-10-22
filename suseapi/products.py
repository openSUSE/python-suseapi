'''
Helper class for various namings used at SUSE.
'''


def codestream_name(name):
    '''
    Converts codestream name into standard form (as used by SMASH).
    '''
    # Standard replacing magic
    dist = name.upper().replace(
        'SLE11', 'SLE-11'
    ).replace(
        'SLE10', 'SLE-10'
    ).replace(
        'SLE9', 'SLE-9'
    ).replace(
        'SLED9', 'SLE-9'
    ).replace(
        'SLED10', 'SLE-10'
    ).replace(
        'SLED11', 'SLE-11'
    ).replace(
        'SLES9', 'SLE-9'
    ).replace(
        'SLES10', 'SLE-10'
    ).replace(
        'SLES11', 'SLE-11'
    ).replace(
        'OES11', 'OES-11'
    ).replace(
        'OES2', 'OES-2'
    ).replace(
        '-UPDATE', ''
    )
    if dist == 'SMT11-SP2':
        return 'SLE-11-SP2-PRODUCTS'

    if dist == 'SLEPOS10':
        return 'SLE-10-SP4'

    if '-' in dist:
        base, end = dist.rsplit('-', 1)
        if end.startswith('PL') or end.startswith('HWREFRESH'):
            dist = '%s-HWRefresh' % base

    return dist
