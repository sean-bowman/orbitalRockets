
# -- LoadFactorSet Class Definition -- #

'''

Quasi-static load factors by flight event, their combination, and the limit to ultimate ladder.

A quasi-static load factor is the whole dynamic environment collapsed into a single acceleration
that a structure can be sized against without a transient analysis. It is a convenience and it is
an approximation, and knowing which parts of it are which is the point of this class.

The factor is not just the rigid body acceleration. It is:

    quasi-static factor = steady acceleration + dynamic amplification of the transient

so a 3 g liftoff event with a dynamic component can present as 5 g to the structure. Treating the
trajectory acceleration as the load factor understates it, and that error is invisible because
both numbers are plausible.

Two things this class exists to make explicit:

**Load factors are direction dependent and they combine.** Axial and lateral do not occur
independently, and the governing combination is rarely the maximum of either. An elliptical or
vector combination is closer to reality than taking the worst of each.

**The load factor is a payload-level quantity.** It applies to the centre of mass of an item and
it does not describe what a component mounted on a flexible panel sees. That is what the random
vibration environment is for, and conflating the two is a real source of under-test.

See Also:
---------
RandomVibrationSpec : The high frequency environment the load factor does not describe
aerospaceStructures LoadCase : Consumes these factors to size structure

Theory: docs/StaticAndQuasiStaticLoads.md

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from environmentsUtils import (applyInputs, formatReportTable,
                                   InvalidInputError, DerivationError, createErrorContext)
except ImportError:
    from .environmentsUtils import (applyInputs, formatReportTable,
                                    InvalidInputError, DerivationError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# NASA-STD-5001 factors, shared with aerospaceStructures. Stated here rather than imported because
# the two domains must not depend on each other's internals, and a drift test asserts they agree.
YIELD_FACTOR    = 1.10    # [-]
ULTIMATE_FACTOR = 1.40    # [-]

# Representative flight events. The axial and lateral values are limit load factors including
# dynamic amplification, which is what distinguishes them from trajectory accelerations. The
# dynamic entry is the part of the axial factor that comes from the transient rather than from
# steady acceleration, so it is always a component of the axial value and never exceeds it.
FLIGHT_EVENTS = {
    'ground handling':  {'axial': 1.2, 'lateral': 0.5, 'dynamic': 0.2,
                         'note': 'crane, transport, erection. Unpressurized'},
    'liftoff':          {'axial': 3.0, 'lateral': 1.0, 'dynamic': 1.8,
                         'note': 'hold-down release transient dominates the dynamic part'},
    'max-Q':            {'axial': 2.5, 'lateral': 2.2, 'dynamic': 1.2,
                         'note': 'gust and buffet. Highest lateral'},
    'max acceleration': {'axial': 6.0, 'lateral': 0.3, 'dynamic': 0.3,
                         'note': 'end of first stage burn, lowest mass'},
    'staging':          {'axial': 1.7, 'lateral': 0.6, 'dynamic': 1.5,
                         'note': 'near freefall plus a large separation transient'},
    'landing':          {'axial': 4.0, 'lateral': 1.5, 'dynamic': 2.5,
                         'note': 'reusable stages. Touchdown transient'},
}

# How axial and lateral are combined. The vector sum is the physical answer for a single event; the
# elliptical form is used where the two peaks do not occur simultaneously.
COMBINATION_METHODS = {
    'vector':      {'note': 'sqrt(axial^2 + lateral^2). Correct when both peak together'},
    'elliptical':  {'note': '(a/A)^2 + (l/L)^2 <= 1. Used when the peaks are not simultaneous'},
    'algebraic':   {'note': 'axial + lateral. Very conservative, rarely justified'},
}

# Above this ratio of dynamic to steady acceleration, a quasi-static factor is a poor
# representation and a transient analysis is needed instead.
DYNAMIC_DOMINANCE_RATIO = 1.0    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- LoadFactorSet -- #
# ------------------------------------------------------------------------------------------------ #

class LoadFactorSet:

    '''

    Quasi-static load factor definition and combination.

    Usage:
    ------
        factors = LoadFactorSet()
        factors.setInputs({'mass': 500.0})
        factors.addStandardEvents()
        result = factors.identifyGoverning()

    '''

    def __init__(self):

        # -- Item -- #

        self.mass            = np.nan  # [kg], the item the factors apply to
        self.description     = ''      # [-]

        # -- Events -- #

        self.events          = {}      # [-], name -> factor dictionary

        # -- Combination -- #

        self.combinationMethod = 'vector'   # key into COMBINATION_METHODS

        # -- Factors -- #

        self.yieldFactor     = YIELD_FACTOR      # [-]
        self.ultimateFactor  = ULTIMATE_FACTOR   # [-]

        # -- Results -- #

        self.findings        = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: mass.

        '''

        requiredParams = {'mass': (int, float)}

        optionalParams = {'description':       str,
                          'events':            dict,
                          'combinationMethod': str,
                          'yieldFactor':       (int, float),
                          'ultimateFactor':    (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.combinationMethod not in COMBINATION_METHODS:
            raise InvalidInputError(
                f'Unknown combination method \'{self.combinationMethod}\'. '
                f'Known: {sorted(COMBINATION_METHODS)}.',
                context = createErrorContext(component = 'LoadFactorSet'))

    # -------------------------------------------------------------------------------------------- #

    def addEvent(self, name: str, axial: float, lateral: float,
                 dynamic: float = 0.0, note: str = '') -> None:

        '''

        Add a flight event. Values are limit load factors in g, including dynamic amplification.

        The dynamic component is carried separately so the split between steady acceleration and
        transient amplification stays visible. A factor that is mostly dynamic is a warning that a
        quasi-static representation may not be adequate.

        '''

        if not np.isfinite(self.mass):
            raise InvalidInputError('Set the mass before adding events.',
                                    context = createErrorContext(component = 'LoadFactorSet'))

        # the dynamic part is a component of the axial factor, so it cannot exceed it. A table
        # where it does produces a negative steady acceleration and a dynamic share above 100 %.
        if abs(dynamic) > abs(axial) + 1.0e-12:
            raise InvalidInputError(
                f'Event \'{name}\' has a dynamic component of {dynamic:.2f} g exceeding its '
                f'axial factor of {axial:.2f} g. The dynamic part is included in the axial value, '
                f'so it cannot be larger.',
                context = createErrorContext(component = 'LoadFactorSet'))

        gravity = 9.80665

        self.events[name] = {'axial':        float(axial),
                             'lateral':      float(lateral),
                             'dynamic':      float(dynamic),
                             'steadyAxial':  float(axial) - float(dynamic),
                             'axialForce':   float(axial) * self.mass * gravity,
                             'lateralForce': float(lateral) * self.mass * gravity,
                             'note':         note}

    def addStandardEvents(self, events: list = None) -> None:

        '''
        Populate from the representative event table.
        '''

        for name in (events if events is not None else list(FLIGHT_EVENTS)):
            if name not in FLIGHT_EVENTS:
                raise InvalidInputError(
                    f'Unknown event \'{name}\'. Known: {sorted(FLIGHT_EVENTS)}.',
                    context = createErrorContext(component = 'LoadFactorSet'))
            entry = FLIGHT_EVENTS[name]
            self.addEvent(name, axial = entry['axial'], lateral = entry['lateral'],
                          dynamic = entry['dynamic'], note = entry['note'])

    # -------------------------------------------------------------------------------------------- #

    def combineEvent(self, name: str) -> dict:

        '''

        Combined load factor for one event, by the chosen method.

        '''

        if name not in self.events:
            raise InvalidInputError(f'No event named \'{name}\'.',
                                    context = createErrorContext(component = 'LoadFactorSet'))

        event   = self.events[name]
        axial   = abs(event['axial'])
        lateral = abs(event['lateral'])

        if self.combinationMethod == 'vector':
            combined = np.sqrt(axial ** 2 + lateral ** 2)
        elif self.combinationMethod == 'algebraic':
            combined = axial + lateral
        else:
            # elliptical: report the resultant that satisfies the interaction at unit utilisation
            combined = np.sqrt(axial ** 2 + lateral ** 2)

        return {'event':          name,
                'axial':          axial,
                'lateral':        lateral,
                'combined':       combined,
                'method':         self.combinationMethod,
                'dynamicShare':   (event['dynamic'] / axial if axial > 0.0 else 0.0),
                'combinedForce':  combined * self.mass * 9.80665}

    # -------------------------------------------------------------------------------------------- #

    def identifyGoverning(self) -> dict:

        '''

        Which event governs by each measure, and whether they agree.

        The largest axial event is rarely the governing combination, which is the reason this class
        reports both rather than one.

        '''

        if not self.events:
            raise DerivationError('No events have been added.',
                                  context = createErrorContext(component = 'LoadFactorSet'))

        combined = {name: self.combineEvent(name) for name in self.events}

        byAxial    = max(self.events, key = lambda name: abs(self.events[name]['axial']))
        byLateral  = max(self.events, key = lambda name: abs(self.events[name]['lateral']))
        byCombined = max(combined, key = lambda name: combined[name]['combined'])

        self.findings = []

        self.findings.append(
            f'By axial factor alone \'{byAxial}\' governs. By the {self.combinationMethod} '
            f'combination \'{byCombined}\' does.')

        if byAxial != byCombined:
            self.findings.append(
                f'These disagree, which is the normal case. \'{byCombined}\' is not the largest '
                f'axial event and it is the worst combination.')

        for name, entry in combined.items():
            if entry['dynamicShare'] > DYNAMIC_DOMINANCE_RATIO:
                self.findings.append(
                    f'\'{name}\' is {entry["dynamicShare"] * 100.0:.0f} % dynamic. A quasi-static '
                    f'factor represents it poorly and a transient analysis is more appropriate.')

        self.findings.append(
            'These factors apply at the centre of mass of the item. They do not describe what a '
            'component on a flexible panel sees, which is what the random vibration environment '
            'is for.')

        return {'combined':          combined,
                'governingByAxial':  byAxial,
                'governingByLateral': byLateral,
                'governingByCombined': byCombined,
                'agree':             bool(byAxial == byCombined),
                'maximumCombined':   combined[byCombined]['combined'],
                'findings':          self.findings}

    # -------------------------------------------------------------------------------------------- #

    def factoredFactors(self, level: str = 'ultimate') -> dict:

        '''

        Every event at the requested factor level.

        '''

        if level not in ('limit', 'yield', 'ultimate'):
            raise InvalidInputError(
                f'level must be \'limit\', \'yield\' or \'ultimate\', got \'{level}\'.',
                context = createErrorContext(component = 'LoadFactorSet'))

        factor = {'limit': 1.0, 'yield': self.yieldFactor,
                  'ultimate': self.ultimateFactor}[level]

        return {'level':  level,
                'factor': factor,
                'events': {name: {'axial':   entry['axial'] * factor,
                                  'lateral': entry['lateral'] * factor,
                                  'axialForce':   entry['axialForce'] * factor,
                                  'lateralForce': entry['lateralForce'] * factor}
                           for name, entry in self.events.items()}}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable load factor matrix.
        '''

        result = self.identifyGoverning()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  QUASI-STATIC LOAD FACTORS: {self.mass:.0f} kg '
                     f'{self.description or "item"}')
        lines.append('=' * 96)
        lines.append('')

        rows = []
        for name, entry in self.events.items():
            combined = result['combined'][name]
            rows.append([name,
                         f'{entry["axial"]:.2f}',
                         f'{entry["lateral"]:.2f}',
                         f'{combined["combined"]:.2f}',
                         f'{combined["dynamicShare"] * 100.0:.0f}',
                         'GOVERNS' if name == result['governingByCombined'] else ''])

        lines.append(formatReportTable(
            rows, ['Event', 'Axial [g]', 'Lateral [g]', 'Combined [g]', 'Dynamic [%]', ''],
            title = f'Limit load factors, {self.combinationMethod} combination'))

        lines.append('')
        factorRows = [['Yield',    f'{self.yieldFactor:.2f}'],
                      ['Ultimate', f'{self.ultimateFactor:.2f}']]
        lines.append(formatReportTable(factorRows, ['Factor', 'Value'],
                                       title = 'Factors of safety'))

        if self.findings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in self.findings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'loadFactors.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the item mass is physical.
        '''

        context = createErrorContext(component = 'LoadFactorSet')

        if not np.isfinite(self.mass) or self.mass <= 0.0:
            raise InvalidInputError('Mass must be positive.', context = context)

        if self.ultimateFactor < self.yieldFactor:
            raise InvalidInputError(
                f'The ultimate factor {self.ultimateFactor:.2f} is below the yield factor '
                f'{self.yieldFactor:.2f}, which inverts the ladder.', context = context)
