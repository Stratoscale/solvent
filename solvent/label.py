def label(basename, product, hash, state):
    return "solvent__%(basename)s__%(product)s__%(hash)s__%(state)s" % dict(
        basename=basename, product=product, hash=hash, state=state)
