"""Assorted helper methods"""
from collections import Iterable
from .small_classes import Strings, Quantity


def try_str_without(item, excluded):
    "Try to call item.str_without(excluded); fall back to str(item)"
    if hasattr(item, "str_without"):
        return item.str_without(excluded)
    else:
        return str(item)


def veckeyed(key):
    "Return a veckey version of a VarKey"
    vecdescr = dict(key.descr)
    del vecdescr["idx"]
    vecdescr.pop("value", None)
    return key.__class__(**vecdescr)


def listify(item):
    "Make sure an item is in a list"
    if isinstance(item, Iterable):
        return list(item)
    else:
        return [item]


def mag(c):
    "Return magnitude of a Number or Quantity"
    if isinstance(c, Quantity):
        return c.magnitude
    else:
        return c


def unitstr(units, into="%s", options="~", dimless='-'):
    "Returns the unitstr of a given object."
    if hasattr(units, "descr") and hasattr(units.descr, "get"):
        units = units.descr.get("units", dimless)
    if units and not isinstance(units, Strings):
        try:
            rawstr = ("{:%s}" % options).format(units)
            if str(units)[-5:] == "count":
            # TODO remove this conditional when pint issue 356 is resolved
                rawstr = "1.0 count"
        except ValueError:
            rawstr = "1.0 " + str(units.units)
        units = "".join(rawstr.replace("dimensionless", dimless).split()[1:])
    if units:
        return into % units
    else:
        return ""


def nomial_latex_helper(c, pos_vars, neg_vars):
    """Combines (varlatex, exponent) tuples,
    separated by positive vs negative exponent,
    into a single latex string"""
    # TODO this is awkward due to sensitivity_map, which needs a refactor
    pvarstrs = ['%s^{%.2g}' % (varl, x) if "%.2g" % x != "1" else varl
                for (varl, x) in pos_vars]
    nvarstrs = ['%s^{%.2g}' % (varl, -x)
                if "%.2g" % -x != "1" else varl
                for (varl, x) in neg_vars]
    pvarstrs.sort()
    nvarstrs.sort()
    pvarstr = ' '.join(pvarstrs)
    nvarstr = ' '.join(nvarstrs)
    c = mag(c)
    cstr = "%.2g" % c
    if pos_vars and (cstr == "1" or cstr == "-1"):
        cstr = cstr[:-1]
    else:
        cstr = latex_num(c)

    if not pos_vars and not neg_vars:
        mstr = "%s" % cstr
    elif pos_vars and not neg_vars:
        mstr = "%s%s" % (cstr, pvarstr)
    elif neg_vars and not pos_vars:
        mstr = "\\frac{%s}{%s}" % (cstr, nvarstr)
    elif pos_vars and neg_vars:
        mstr = "%s\\frac{%s}{%s}" % (cstr, pvarstr, nvarstr)

    return mstr


def is_sweepvar(sub):
    "Determines if a given substitution indicates a sweep."
    try:
        if sub[0] == "sweep":
            if isinstance(sub[1], Iterable) or hasattr(sub[1], "__call__"):
                return True
    except (TypeError, IndexError):
        return False


def latex_num(c):
    "Returns latex string of numbers, potentially using exponential notation."
    cstr = "%.4g" % c
    if 'e' in cstr:
        idx = cstr.index('e')
        cstr = "%s \\times 10^{%i}" % (cstr[:idx], int(cstr[idx+1:]))
    return cstr


def flatten(ible, classes):
    """Flatten an iterable that contains other iterables

    Arguments
    ---------
    l : Iterable
        Top-level container

    Returns
    -------
    out : list
        List of all objects found in the nested iterables

    Raises
    ------
    TypeError
        If an object is found whose class was not in classes
    """
    out = []
    for el in ible:
        if isinstance(el, classes):
            out.append(el)
        elif isinstance(el, Iterable):
            for elel in flatten(el, classes):
                out.append(elel)
        else:
            raise TypeError("Iterable %s contains element '%s'"
                            " of invalid class %s." % (ible, el, el.__class__))
    return out
