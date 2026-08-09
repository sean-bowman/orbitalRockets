
# -- Validation reference cases -- #

'''

Published hardware data the repository's tools are checked against, with provenance.

The rule this file exists to enforce: a tool that has only been checked against itself has not been
checked. Every class in this repository produces numbers that are internally consistent, and
internal consistency is worth very little on its own. It was internal consistency that let a
placeholder wall heat flux sit in the propulsion hub for three commits while a document asserted
the conclusion it produced.

Every entry carries four things and is not usable without all of them.

    value        the published number
    source       where it came from, specifically enough to find again
    kind         measured, published-specification, derived, or estimate
    note         what the number includes, which is usually the difficult part

The `kind` field is the one that does the work. A published engine specific impulse is not a
measurement of the thrust chamber: it is a whole-engine figure that includes cycle losses, and
comparing it against a thrust chamber calculation is comparing two different quantities. That
distinction is recorded here rather than discovered later.

**Nothing in this file may be adjusted to make a test pass.** If a tool disagrees with a reference,
either the tool is wrong, the comparison is wrong, or the disagreement is real and understood. All
three are recorded outcomes. Editing the reference is not.

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Provenance kinds -- #
# ------------------------------------------------------------------------------------------------ #

# What a reference number actually is, which decides what it can legitimately be compared against.
REFERENCE_KINDS = {
    'measured': 'A directly measured quantity from a test or flight',
    'specification': 'A published engine or component specification. Usually a nominal design '
                     'value rather than a measurement, and usually a whole-system figure',
    'derived': 'Computed by the source from other published values',
    'estimate': 'An order-of-magnitude or typical value. Usable as a sanity bound, not as a check',
}

# ------------------------------------------------------------------------------------------------ #
# -- Liquid rocket engines -- #
# ------------------------------------------------------------------------------------------------ #

# Whole-engine published specifications. The critical caveat, recorded on every entry rather than
# once at the top, is that a published engine specific impulse includes the engine cycle.
#
# A closed cycle engine, staged combustion or expander, puts all of its propellant through the main
# chamber and its published Isp is very nearly a thrust chamber figure. An open cycle engine, gas
# generator, dumps turbine exhaust overboard at a specific impulse far below the main chamber, and
# its published Isp carries that penalty.
#
# The propulsion hub library models the thrust chamber and the nozzle. It does not model the cycle.
# So a closed cycle engine validates it directly and an open cycle engine does not, and the
# difference between the two is roughly the size of the effect being validated.
LIQUID_ENGINES = {

    'RS-25': {
        'source': 'https://en.wikipedia.org/wiki/RS-25, accessed 08 August 2026',
        'kind': 'specification',
        'cycle': 'staged combustion',
        'closedCycle': True,
        'combination': 'LOX/LH2',
        'chamberPressure': 20.64e6,      # [Pa]
        'areaRatio': 78.0,               # [-]
        'mixtureRatio': 6.03,            # [-]
        'vacuumThrust': 2279.0e3,        # [N]
        'seaLevelThrust': 1860.0e3,      # [N]
        'vacuumImpulse': 452.3,          # [s]
        'seaLevelImpulse': 366.0,        # [s]
        'throatDiameter': 0.26,          # [m]
        'note': 'Closed cycle, so the published impulse is very nearly a thrust chamber figure and '
                'this is the cleanest available validation case for the performance library. The '
                'tabulated mixture ratio of 6.03 is leaner than the 5.50 the propellant table '
                'carries, so the comparison inherits that mismatch.'},

    'F-1': {
        'source': 'https://en.wikipedia.org/wiki/Rocketdyne_F-1, accessed 08 August 2026',
        'kind': 'specification',
        'cycle': 'gas generator',
        'closedCycle': False,
        'combination': 'LOX/RP-1',
        'chamberPressure': 7.0e6,        # [Pa]
        'areaRatio': 16.0,               # [-]
        'mixtureRatio': 2.27,            # [-]
        'seaLevelThrust': 6770.0e3,      # [N]
        'vacuumImpulse': 304.0,          # [s]
        'seaLevelImpulse': 263.0,        # [s]
        'note': 'Open cycle. The published impulse includes the gas generator exhaust dumped '
                'overboard, which is a loss the thrust chamber library does not model and cannot '
                'be expected to reproduce. Retained deliberately as the case that shows what the '
                'library does not cover, and it should not be used to tune an efficiency.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Correlation accuracy -- #
# ------------------------------------------------------------------------------------------------ #

# What the literature says about the correlations this repository uses. These are not values to
# check against, they are the tolerance a check is allowed to claim: a tool cannot be validated to
# a tighter band than the correlation underneath it.
CORRELATION_ACCURACY = {

    'bartz': {
        'source': 'Bartz 1957, and the comparisons in NASA TN reviewing it against nozzle test '
                  'data; see also DLR and EUCASS heat transfer correlation comparisons',
        'kind': 'estimate',
        'band': 0.20,
        'bias': 'over',
        'note': 'Plus or minus twenty per cent at best and worse in the convergent section. The '
                'literature consistently reports that the one-dimensional Bartz calculation '
                'overestimates inner wall temperature, because it does not account for boundary '
                'layer thickness variation along the wall. A cooling design that closes on a ten '
                'per cent margin against Bartz has not closed.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Explicitly unvalidated -- #
# ------------------------------------------------------------------------------------------------ #

# The honest register. Every entry here is a calculation the repository performs and cannot
# currently check against anything external, with the reason.
#
# This list existing is more useful than it being short. A reader who wants to know whether to
# trust a number should be able to find out, and 'we could not find data' is an answer.
UNVALIDATED = {

    'chamberHeatLoad': {
        'domain': 'propulsion/combustionDevices',
        'calculation': 'Total wall heat load from Bartz integrated over the chamber and nozzle',
        'reason': 'Published engine data gives coolant flow and sometimes coolant temperature rise '
                  'but rarely both with the geometry needed to close the energy balance. The '
                  'searched sources for RS-25 give the channel count and the coolant path and not '
                  'the heat load.',
        'consequence': 'The 8.13 MW computed for the reference engine is a Bartz result and not a '
                       'validated one. It replaced a hub placeholder that was lower by a factor of '
                       'three, and the direction of that correction is supported by the power base '
                       'argument below, but neither number has an external anchor.',
        'nextStep': 'A published regeneratively cooled engine with coolant flow, inlet and outlet '
                    'temperature, and chamber geometry. Failing that, a textbook worked example '
                    'such as the Huzel and Huang A-1 stage engine, which carries a full cooling '
                    'calculation.'},

    'injectorMixingQuality': {
        'domain': 'propulsion/combustionDevices',
        'calculation': 'The relative mixing quality figures in INJECTOR_ELEMENTS',
        'reason': 'They are a ranking rather than a measurement and no source states them as '
                  'numbers. They exist to order the element types.',
        'consequence': 'They must not be used to predict c* efficiency. The class uses them only '
                       'to rank.',
        'nextStep': 'Either source real c* efficiency data per element type or remove the numbers '
                    'and keep the ordering.'},

    'coolantLimits': {
        'domain': 'propulsion/combustionDevices',
        'calculation': 'The coking and decomposition limits in COOLANT_LIMITS',
        'reason': 'Widely quoted ranges rather than a single sourced value, and the real limit is '
                  'a film temperature that depends on residence time and surface chemistry.',
        'consequence': 'The RP-1 limit of 575 K drives the conclusion that the reference engine '
                       'cannot be regeneratively cooled. That conclusion is sensitive to a number '
                       'quoted as a range.',
        'nextStep': 'A sourced coking limit with its residence time basis.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Derived checks -- #
# ------------------------------------------------------------------------------------------------ #

def impliedEfficiency(publishedImpulse: float, idealImpulse: float) -> float:

    '''

    The combined efficiency a published engine implies against an ideal calculation.

    For a closed cycle engine this is close to a thrust chamber efficiency. For an open cycle
    engine it is a thrust chamber efficiency multiplied by the cycle penalty, and the two cannot be
    separated without knowing the turbine flow fraction.

    '''

    return publishedImpulse / idealImpulse
