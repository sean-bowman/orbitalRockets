
# -- ProcessComparison Class Definition -- #

'''

Route trade for a given part: buy-to-fly ratio, allowable knockdown, mass, relative cost and lead
time across forged, machined-from-plate, cast, formed and additive routes.

The alloy decision and the process decision are usually made separately and they should not be. The
same alloy through two routes is two materials, because the route sets the allowable knockdown, and
the knockdown often matters more than the difference between two candidate alloys.

A cast part with no qualified process carries a casting factor of 2.0, which halves the allowable.
No alloy substitution recovers that, and qualifying the casting process is cheaper than switching to
titanium. That trade is invisible unless the routes are compared side by side with the knockdowns
attached, which is what this class exists to do.

Buy-to-fly is the second axis and it drives cost far more than the per-kilogram material price does.
A 15:1 forging on a 20x cost alloy is a very different proposition from a 1.4:1 additive part on the
same alloy, and the raw material price alone gets that backwards.

This class is also where the sub-domain libraries earn their place. Every route in the table below
is a sub-domain, and each supplies the numbers for its own row.

See Also:
---------
MaterialSelector : Chooses the alloy. Run it first, then bring the survivors here.
Allowables       : The knockdown factors this class applies come from STANDARD_KNOCKDOWNS
additiveLPBF, castingProcesses, formingProcesses, machiningProcesses, spinCasting : the routes

Theory: docs/ProcessRouteSelection.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import applyInputs, formatReportTable, InvalidInputError, createErrorContext
    from MaterialDatabase import queryMaterial
    from Allowables import STANDARD_KNOCKDOWNS
except ImportError:
    from .utils import applyInputs, formatReportTable, InvalidInputError, createErrorContext
    from .MaterialDatabase import queryMaterial
    from .Allowables import STANDARD_KNOCKDOWNS

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# The routes. Each carries a typical buy-to-fly ratio, the allowable knockdown it imposes, a
# relative process cost multiplier, a lead time adder in weeks, and the geometric limits that
# decide whether the route is available at all.
#
# buyToFly is the mass of stock consumed per unit mass of finished part. It drives raw material
# cost, machining time and scrap value all at once, and on an expensive alloy it dominates.
#
# The knockdown keys resolve through Allowables.STANDARD_KNOCKDOWNS so the factors are defined in
# exactly one place.

PROCESS_ROUTES = {
    'machined from plate': {
        'buyToFly': 8.0, 'knockdowns': [], 'costMultiplier': 1.0, 'leadTimeAdder': 4,
        'minimumWall': 0.0008, 'maximumSize': 2.0, 'toleranceGrade': 'IT7',
        'surfaceRoughness': 1.6e-6,
        'note': 'The default. No process qualification needed and the allowable is the wrought '
                'allowable, but the buy-to-fly is punishing on an expensive alloy and the machining '
                'time scales with the material removed.'},

    'closed die forged and machined': {
        'buyToFly': 4.0, 'knockdowns': [], 'costMultiplier': 1.8, 'leadTimeAdder': 24,
        'minimumWall': 0.0025, 'maximumSize': 1.5, 'toleranceGrade': 'IT7',
        'surfaceRoughness': 1.6e-6,
        'note': 'Grain flow follows the part shape, which is worth real fatigue life on a highly '
                'loaded fitting. The die is the cost and the lead time, so it only pays at quantity '
                'or where the grain flow is genuinely needed.'},

    'ring rolled and machined': {
        'buyToFly': 3.0, 'knockdowns': [], 'costMultiplier': 1.4, 'leadTimeAdder': 18,
        'minimumWall': 0.005, 'maximumSize': 6.0, 'toleranceGrade': 'IT9',
        'surfaceRoughness': 3.2e-6,
        'note': 'For any large ring or flange. Circumferential grain flow, far better buy-to-fly '
                'than machining from plate, and it scales to diameters plate cannot reach.'},

    'flow formed': {
        'buyToFly': 2.5, 'knockdowns': [], 'costMultiplier': 1.0, 'leadTimeAdder': 14,
        'minimumWall': 0.0006, 'maximumSize': 3.0, 'toleranceGrade': 'IT9',
        'surfaceRoughness': 1.6e-6,
        'note': 'Cold work raises the strength of the formed section, and wall thickness control is '
                'excellent. The route for thin walled cylinders and pressure vessel domes. Needs a '
                'mandrel per geometry.'},

    'spun and welded': {
        'buyToFly': 2.0, 'knockdowns': ['weld, electron beam'], 'costMultiplier': 0.9,
        'leadTimeAdder': 12, 'minimumWall': 0.0008, 'maximumSize': 4.0, 'toleranceGrade': 'IT11',
        'surfaceRoughness': 3.2e-6,
        'note': 'Two spun hemispheres and a girth weld. Cheap tooling, good buy-to-fly, and the '
                'weld knockdown applies to the girth only rather than the whole part.'},

    'investment cast': {
        'buyToFly': 1.6, 'knockdowns': ['casting, factor 1.33'], 'costMultiplier': 1.2,
        'leadTimeAdder': 20, 'minimumWall': 0.0015, 'maximumSize': 1.0, 'toleranceGrade': 'IT11',
        'surfaceRoughness': 3.2e-6,
        'note': 'Complex geometry in one piece with an excellent as-cast surface. The casting factor '
                'is the whole trade: 1.0 with a qualified process and full volumetric NDE, 1.33 with '
                'partial, 2.0 by default.'},

    'sand cast': {
        'buyToFly': 1.8, 'knockdowns': ['casting, factor 2.0'], 'costMultiplier': 0.5,
        'leadTimeAdder': 12, 'minimumWall': 0.005, 'maximumSize': 5.0, 'toleranceGrade': 'IT14',
        'surfaceRoughness': 25.0e-6,
        'note': 'Cheap, large, and coarse. The default casting factor of 2.0 halves the allowable, '
                'so it is rarely a flight structure route without a qualification programme.'},

    'centrifugal cast': {
        'buyToFly': 2.2, 'knockdowns': ['casting, factor 1.33'], 'costMultiplier': 0.7,
        'leadTimeAdder': 14, 'minimumWall': 0.004, 'maximumSize': 4.0, 'toleranceGrade': 'IT12',
        'surfaceRoughness': 12.5e-6,
        'note': 'Inherently clean: the centrifugal field drives inclusions and gas to the bore, '
                'which is then machined away. Cylinders and rings only, and the machining allowance '
                'on the bore is set by the segregation depth rather than by tolerance.'},

    'lpbf as-built': {
        'buyToFly': 1.2, 'knockdowns': ['additive, Z direction', 'additive, as-built surface'],
        'costMultiplier': 2.4, 'leadTimeAdder': 6, 'minimumWall': 0.0004, 'maximumSize': 0.4,
        'toleranceGrade': 'IT12', 'surfaceRoughness': 20.0e-6,
        'note': 'Shortest lead time and best buy-to-fly of any route, and the as-built surface '
                'costs a quarter of the fatigue allowable. Internal passages cannot be inspected '
                'except by CT and cannot be finished except by abrasive flow.'},

    'lpbf hip and machined': {
        'buyToFly': 1.4, 'knockdowns': ['additive, Z direction'], 'costMultiplier': 3.2,
        'leadTimeAdder': 10, 'minimumWall': 0.0006, 'maximumSize': 0.4, 'toleranceGrade': 'IT8',
        'surfaceRoughness': 1.6e-6,
        'note': 'HIP closes the porosity that dominates as-built fatigue and machining removes the '
                'rough surface, so only the build direction knockdown survives. This is what an '
                'additive flight part actually looks like.'},

    'wire arc additive and machined': {
        'buyToFly': 2.0, 'knockdowns': ['additive, Z direction'], 'costMultiplier': 1.6,
        'leadTimeAdder': 8, 'minimumWall': 0.006, 'maximumSize': 6.0, 'toleranceGrade': 'IT11',
        'surfaceRoughness': 25.0e-6,
        'note': 'Deposition rate two orders of magnitude above LPBF and no build volume limit worth '
                'mentioning, at the cost of a coarse surface and a thick minimum wall. The route for '
                'large near-net preforms that would otherwise be forgings.'}
}

# ISO 2768 / ISO 286 tolerance grades to a representative tolerance on a 100 mm dimension, so the
# routes can be compared on dimensional capability rather than on a letter code.

TOLERANCE_GRADE_100MM = {
    'IT7': 0.035e-3, 'IT8': 0.054e-3, 'IT9': 0.087e-3, 'IT11': 0.220e-3,
    'IT12': 0.350e-3, 'IT14': 0.870e-3
}

# ------------------------------------------------------------------------------------------------ #

class ProcessComparison:

    '''

    Compare manufacturing routes for one part in one alloy.

    Primary Input Properties:
    -------------------------
    material / condition : str, str
    finishedMass : float
        [kg] of the finished part
    minimumWallThickness : float
        [m] the design requires
    characteristicSize : float
        [m] the largest dimension
    routes : list
        Keys into PROCESS_ROUTES. Empty means every route.
    quantity : int
        Affects whether tooling amortises

    Key Output Properties:
    ----------------------
    comparison : list
        One entry per feasible route, with allowable factor, mass, cost index and lead time
    infeasible : dict
        Route -> why it cannot make this part

    Public Methods:
    ---------------
    setInputs(inputs)             Load a configuration dictionary
    screenRoutes()                Geometric feasibility
    compareRoutes()               The full trade
    selectRoute(objective)        Best by an objective
    generateReport(outputDir)     The comparison table

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Part Definition -- #

        self.material             = 'TI-6AL-4V'   # [case insensitive string]
        self.condition            = 'annealed'    # [case insensitive string]
        self.finishedMass         = 1.0           # [kg]
        self.minimumWallThickness = 0.002         # [m]
        self.characteristicSize   = 0.200         # [m], the largest dimension
        self.requiredTolerance    = 0.100e-3      # [m] on a 100 mm dimension
        self.quantity             = 1             # [-]

        # -- Trade Configuration -- #

        self.routes               = []            # [list of str], empty means all
        self.objective            = 'minimum cost'  # [case insensitive string]

        # -- Results -- #

        self.comparison           = []            # [list of dict]
        self.infeasible           = {}            # [dict], route -> reason
        self.processNotes         = []            # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: material, finishedMass.

        '''

        requiredParams = {
            'material':     'Material not provided.',
            'finishedMass': 'Finished part mass not provided. Buy-to-fly is meaningless without it.'
        }

        optionalParams = ['condition', 'minimumWallThickness', 'characteristicSize',
                          'requiredTolerance', 'quantity', 'routes', 'objective']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def screenRoutes(self) -> dict:

        '''

        Geometric and dimensional feasibility, before any cost is considered.

        A route that cannot hold the wall thickness or fit the part in the machine is not a cheap
        option, it is not an option. Screening first keeps the comparison table honest.

        '''

        candidates = self.routes if self.routes else list(PROCESS_ROUTES.keys())

        feasible        = []
        self.infeasible = {}

        for routeKey in candidates:

            route   = PROCESS_ROUTES.get(routeKey)
            reasons = []

            if route is None:
                raise InvalidInputError(
                    message       = f'Unknown process route \'{routeKey}\'.',
                    parameterName = 'routes', value = routeKey,
                    validRange    = str(sorted(PROCESS_ROUTES.keys()))
                )

            if self.minimumWallThickness < route['minimumWall']:
                reasons.append(
                    f'Minimum wall {route["minimumWall"] * 1000.0:.2f} mm exceeds the required '
                    f'{self.minimumWallThickness * 1000.0:.2f} mm')

            if self.characteristicSize > route['maximumSize']:
                reasons.append(
                    f'Maximum size {route["maximumSize"]:.1f} m below the required '
                    f'{self.characteristicSize:.2f} m')

            achievable = TOLERANCE_GRADE_100MM[route['toleranceGrade']]
            if achievable > self.requiredTolerance:
                reasons.append(
                    f'{route["toleranceGrade"]} holds {achievable * 1.0e6:.0f} um on 100 mm, and '
                    f'{self.requiredTolerance * 1.0e6:.0f} um is required. A finish machining '
                    f'operation would be needed and is not included in this route.')

            if reasons:
                self.infeasible[routeKey] = reasons
            else:
                feasible.append(routeKey)

        if not feasible:
            self.processNotes.append(
                'No route can make this part as specified. The binding constraint is usually the '
                'tolerance, which is normally solved by adding a finish machining operation to a '
                'near-net route rather than by changing route entirely.')

        return {'feasible': feasible, 'infeasible': self.infeasible}

    def compareRoutes(self) -> list:

        '''

        The full trade across every feasible route.

        Each row carries the allowable factor from the compounded knockdowns, the stock mass from
        the buy-to-fly ratio, a relative cost index built from the material cost and the process
        multiplier, and the lead time.

        The allowable factor is the column that changes decisions. A route with an excellent
        buy-to-fly and a 0.5 casting factor is not cheap; it is a part that needs twice the wall.

        '''

        screening  = self.screenRoutes()
        properties = queryMaterial(self.material, self.condition, 293.15)

        self.comparison = []

        for routeKey in screening['feasible']:

            route = PROCESS_ROUTES[routeKey]

            allowableFactor = 1.0
            knockdownDetail = []
            for knockdownKey in route['knockdowns']:
                entry = STANDARD_KNOCKDOWNS[knockdownKey]
                allowableFactor *= entry['factor']
                knockdownDetail.append(f'{knockdownKey} ({entry["factor"]:.2f})')

            stockMass = self.finishedMass * route['buyToFly']

            # Relative cost: stock material plus a process multiplier applied to the finished mass.
            # Both are indexed to 316L bar, so the number is comparable across alloys and routes and
            # is never a currency amount.
            materialCost = stockMass * properties['relativeCost']
            processCost  = self.finishedMass * route['costMultiplier'] * 3.0
            relativeCost = materialCost + processCost

            leadTimes = properties.get('leadTimeWeeks', {})
            stockLead = min(leadTimes.values()) if leadTimes else 12
            totalLead = stockLead + route['leadTimeAdder']

            # A part whose allowable is knocked down needs more material to carry the same load, so
            # the mass penalty and the allowable factor are the same number for a membrane.
            massPenalty = 1.0 / allowableFactor

            self.comparison.append({
                'route': routeKey,
                'buyToFly': route['buyToFly'],
                'stockMass': stockMass,
                'allowableFactor': allowableFactor,
                'knockdowns': knockdownDetail or ['none'],
                'massPenalty': massPenalty,
                'effectiveMass': self.finishedMass * massPenalty,
                'materialCostIndex': materialCost,
                'processCostIndex': processCost,
                'relativeCost': relativeCost,
                'leadTimeWeeks': totalLead,
                'toleranceGrade': route['toleranceGrade'],
                'surfaceRoughness': route['surfaceRoughness'],
                'note': route['note']})

        if not self.comparison:
            return []

        bestCost = min(entry['relativeCost'] for entry in self.comparison)
        bestMass = min(entry['effectiveMass'] for entry in self.comparison)
        bestLead = min(entry['leadTimeWeeks'] for entry in self.comparison)

        for entry in self.comparison:
            entry['costRatio'] = entry['relativeCost'] / bestCost
            entry['massRatio'] = entry['effectiveMass'] / bestMass
            entry['leadRatio'] = entry['leadTimeWeeks'] / bestLead

        self.comparison.sort(key = lambda entry: entry['relativeCost'])

        # -- The finding that makes this class worth running -- #

        knockedDown = [entry for entry in self.comparison if entry['allowableFactor'] < 0.9]
        if knockedDown:
            worst = min(knockedDown, key = lambda entry: entry['allowableFactor'])
            self.processNotes.append(
                f'The {worst["route"]} route carries an allowable factor of '
                f'{worst["allowableFactor"]:.2f} from {", ".join(worst["knockdowns"])}, so the part '
                f'needs {worst["massPenalty"]:.2f} times the material to carry the same load. That '
                f'knockdown is usually larger than the difference between two candidate alloys, '
                f'which is why the alloy and the route should not be chosen separately.')

        castingRoutes = [entry for entry in self.comparison if 'cast' in entry['route']]
        if castingRoutes:
            self.processNotes.append(
                'Every casting factor in this table is the un-qualified or partly qualified value. '
                'A fully qualified casting process with 100 percent volumetric NDE and three sample '
                'lots earns a factor of 1.0 and removes the knockdown entirely. Qualifying the '
                'process is frequently cheaper than the mass the factor costs.')

        return self.comparison

    def selectRoute(self, objective: str = None) -> dict:

        '''

        Best route by a stated objective, with the runner up and the reason for the gap.

        '''

        if not self.comparison:
            self.compareRoutes()

        if not self.comparison:
            raise InvalidInputError(
                message       = 'No feasible route to select from.',
                parameterName = 'routes', value = self.routes,
                validRange    = 'At least one geometrically feasible route'
            )

        objective = (objective or self.objective).strip().lower()

        keys = {'minimum cost': 'relativeCost', 'minimum mass': 'effectiveMass',
                'minimum lead time': 'leadTimeWeeks', 'maximum allowable': 'allowableFactor'}

        if objective not in keys:
            raise InvalidInputError(
                message       = f'Unknown objective \'{objective}\'.',
                parameterName = 'objective', value = objective, validRange = str(sorted(keys.keys()))
            )

        reverse = objective == 'maximum allowable'
        ordered = sorted(self.comparison, key = lambda entry: entry[keys[objective]],
                         reverse = reverse)

        best     = ordered[0]
        runnerUp = ordered[1] if len(ordered) > 1 else None

        result = {'objective': objective, 'selected': best['route'], 'entry': best}

        if runnerUp is not None:
            gap = abs(best[keys[objective]] - runnerUp[keys[objective]]) / \
                  max(abs(runnerUp[keys[objective]]), 1.0e-12)
            result['runnerUp'] = runnerUp['route']
            result['gap']      = gap
            if gap < 0.10:
                self.processNotes.append(
                    f'{best["route"]} and {runnerUp["route"]} are within {gap * 100.0:.1f} percent '
                    f'on {objective}. That is inside the accuracy of these estimates, so the choice '
                    f'should be made on something this table does not capture: supplier capability, '
                    f'inspectability, or an existing qualification.')

        return result

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build the route comparison table.

        '''

        if not self.comparison:
            self.compareRoutes()

        properties = queryMaterial(self.material, self.condition, 293.15)

        headerRows = [
            ['Material',        f'{properties["commonName"]} ({self.condition})'],
            ['Finished mass',   f'{self.finishedMass:.3f} kg'],
            ['Minimum wall',    f'{self.minimumWallThickness * 1000.0:.2f} mm'],
            ['Characteristic size', f'{self.characteristicSize * 1000.0:.0f} mm'],
            ['Required tolerance', f'{self.requiredTolerance * 1.0e6:.0f} um on 100 mm'],
            ['Quantity',        f'{self.quantity}'],
            ['Routes feasible', f'{len(self.comparison)} of {len(PROCESS_ROUTES)}']
        ]

        report = formatReportTable(headerRows, ['Quantity', 'Value'],
                                   title = 'PROCESS ROUTE COMPARISON')

        if self.comparison:
            rows = [[entry['route'],
                     f'{entry["buyToFly"]:.1f}:1',
                     f'{entry["allowableFactor"]:.2f}',
                     f'{entry["effectiveMass"]:.3f}',
                     f'{entry["relativeCost"]:.1f}',
                     f'{entry["leadTimeWeeks"]:.0f}',
                     f'{entry["surfaceRoughness"] * 1.0e6:.1f}']
                    for entry in self.comparison]
            report += '\n\n' + formatReportTable(
                rows,
                ['Route', 'Buy-to-fly', 'Allowable', 'Eff mass [kg]', 'Rel cost', 'Lead wk',
                 'Ra [um]'],
                title = 'ROUTES, CHEAPEST FIRST')

        if self.infeasible:
            report += f'\n\nNOT FEASIBLE ({len(self.infeasible)})\n{"-" * 70}\n'
            for routeKey, reasons in sorted(self.infeasible.items()):
                report += f'  {routeKey}\n'
                for reason in reasons:
                    report += f'      {reason}\n'

        report += (f'\nCost figures are indexed to 316L bar = 1.0 and combine stock material with a '
                   f'process multiplier. They are for comparing routes against each other, not for '
                   f'quoting.\n')

        for note in self.processNotes:
            report += f'\nNOTE: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'processComparison.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.finishedMass <= 0.0:
            raise InvalidInputError(
                message       = 'Finished mass must be positive.',
                parameterName = 'finishedMass', value = self.finishedMass,
                validRange    = 'Greater than 0 kg'
            )

        if self.minimumWallThickness <= 0.0:
            raise InvalidInputError(
                message       = 'Minimum wall thickness must be positive.',
                parameterName = 'minimumWallThickness', value = self.minimumWallThickness,
                validRange    = 'Greater than 0 m'
            )

        for routeKey in self.routes:
            if routeKey not in PROCESS_ROUTES:
                raise InvalidInputError(
                    message       = f'Unknown process route \'{routeKey}\'.',
                    parameterName = 'routes', value = routeKey,
                    validRange    = str(sorted(PROCESS_ROUTES.keys()))
                )
