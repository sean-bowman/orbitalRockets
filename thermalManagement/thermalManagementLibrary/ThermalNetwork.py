
# -- ThermalNetwork Class Definition -- #

'''

Multi-node resistance network, solved at steady state and marched through a transient.

A thermal model is a set of lumps connected by resistances. That is the whole idea, and its value
is that it is honest about what it does not know: every resistance is a number somebody estimated,
and the network makes it obvious which one the answer depends on.

The two solves answer different questions and the transient one is the one that matters on a launch
vehicle:

    steady state    where does it end up, given infinite time
    transient       what does it do during the event, and for how long afterwards

**Nothing on an ascent reaches steady state.** A launch vehicle is in the atmosphere for two
minutes, and the structures with the largest heat loads are precisely those with enough mass that
they cannot respond in two minutes. A steady state answer is not conservative in that case, it is
simply the wrong question: it reports a temperature the hardware never reaches while missing the
one it does.

**Soakback is why the transient is not optional.** After the heating stops, the heat already in the
surface keeps moving inward, and an interior node frequently peaks well after the event ended. A
model run only during the heat pulse misses the maximum entirely, and that is a recurring cause of
hardware that passed analysis and failed test.

Contact conductance is usually the dominant resistance and the least well known number. The class
therefore reports which resistance the answer is most sensitive to, because in practice that is the
useful output: refining a well known resistance changes nothing.

See Also:
---------
AblativeTPS    : What to do when the surface temperature is beyond any material
ThermalControl : The heater sizing that a network's cold case produces
Insulation     : (fluidSystems) the cryogenic heat leak case of the same physics

Theory: docs/ConductionAndResistance.md

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from thermalUtils import (applyInputs, formatReportTable, biotNumber, fourierNumber,
                              thermalDiffusivity, conductionResistance, contactResistance,
                              convectionResistance, radiationResistance,
                              LUMPED_CAPACITANCE_BIOT_LIMIT, CONTACT_CONDUCTANCE,
                              InvalidInputError, ThermalNetworkError, createErrorContext)
except ImportError:
    from .thermalUtils import (applyInputs, formatReportTable, biotNumber, fourierNumber,
                               thermalDiffusivity, conductionResistance, contactResistance,
                               convectionResistance, radiationResistance,
                               LUMPED_CAPACITANCE_BIOT_LIMIT, CONTACT_CONDUCTANCE,
                               InvalidInputError, ThermalNetworkError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# An explicit time march is stable only below this Fourier-like ratio. The class uses an implicit
# scheme instead, which is unconditionally stable, but the number is reported so the physical
# timescale of the smallest node is visible.
EXPLICIT_STABILITY_LIMIT = 0.5    # [-]

# A node with no capacitance is an arithmetic node: it has no thermal mass and simply balances the
# heat arriving at it. Useful for surfaces and interfaces, and it must not appear in a transient
# march without care.
MASSLESS_NODE_CAPACITANCE = 0.0    # [J/K]

# Below this fraction of the total network resistance, refining a resistance cannot move the answer
# meaningfully and effort is better spent elsewhere.
SENSITIVITY_REPORTING_THRESHOLD = 0.05    # [-]

# A radiative link is linearised about the temperatures at its two ends, so a steady state solve has
# to iterate: solve, re-linearise about the answer, solve again, until the temperatures stop moving.
# A tenth of a millikelvin is far below anything that matters physically and is reached in a handful
# of iterations for any network that converges at all.
RADIATION_CONVERGENCE_TOLERANCE = 1.0e-4    # [K]

# If Picard iteration has not settled by here the network is oscillating rather than converging,
# which happens when a radiative link swings a node further each pass than the last.
RADIATION_MAXIMUM_ITERATIONS = 200    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- ThermalNetwork -- #
# ------------------------------------------------------------------------------------------------ #

class ThermalNetwork:

    '''

    Lumped-capacitance thermal network.

    Usage:
    ------
        network = ThermalNetwork()
        network.setInputs({})
        network.addNode('skin', capacitance = 2000.0, temperature = 293.15)
        network.addNode('space', temperature = 4.0, boundary = True)
        network.addResistance('skin', 'space', 0.05)
        result = network.solveSteadyState()

    '''

    def __init__(self):

        # -- Network -- #

        self.nodes        = {}     # [-], name -> node dictionary
        self.resistances  = {}     # [-], (nodeA, nodeB) -> resistance [K/W]

        # -- Transient -- #

        self.timeStep     = 1.0    # [s]
        self.endTime      = 100.0  # [s]

        # -- Results -- #

        self.history      = None   # [-], transient solution
        self.findings     = []     # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        '''

        requiredParams = {}

        optionalParams = {'timeStep': (int, float),
                          'endTime':  (int, float),
                          'nodes':    dict,
                          'resistances': dict}

        applyInputs(self, inputs, requiredParams, optionalParams)

    # -------------------------------------------------------------------------------------------- #

    def addNode(self, name: str, capacitance: float = MASSLESS_NODE_CAPACITANCE,
                temperature: float = 293.15, heatLoad: float = 0.0,
                boundary: bool = False, note: str = '') -> None:

        '''

        Add a node.

        A boundary node is held at its temperature regardless of the heat crossing it, which is how
        space, a fluid bulk or a controlled interface is represented. A node with zero capacitance
        is an arithmetic node: it balances heat instantly and has no thermal mass.

        '''

        if capacitance < 0.0:
            raise InvalidInputError(f'Node \'{name}\' has a negative capacitance.',
                                    context = createErrorContext(component = 'ThermalNetwork'))

        if temperature <= 0.0:
            raise InvalidInputError(
                f'Node \'{name}\' temperature must be absolute and positive, got {temperature}.',
                context = createErrorContext(component = 'ThermalNetwork'))

        self.nodes[name] = {'capacitance': float(capacitance),
                            'temperature': float(temperature),
                            'heatLoad':    float(heatLoad),
                            'boundary':    bool(boundary),
                            'note':        note}

    def addNodeFromMass(self, name: str, mass: float, specificHeat: float,
                        temperature: float = 293.15, heatLoad: float = 0.0,
                        note: str = '') -> None:

        '''

        Add a node whose capacitance comes from its mass, C = m cp.

        '''

        if mass <= 0.0 or specificHeat <= 0.0:
            raise InvalidInputError('Mass and specific heat must be positive.',
                                    context = createErrorContext(component = 'ThermalNetwork'))

        self.addNode(name, capacitance = mass * specificHeat, temperature = temperature,
                     heatLoad = heatLoad, note = note)

    # -------------------------------------------------------------------------------------------- #

    def addResistance(self, nodeA: str, nodeB: str, resistance: float, note: str = '') -> None:

        '''

        Connect two nodes with a thermal resistance in K/W.

        '''

        for name in (nodeA, nodeB):
            if name not in self.nodes:
                raise ThermalNetworkError(
                    f'Node \'{name}\' does not exist. Add it before connecting it.',
                    context = createErrorContext(component = 'ThermalNetwork'))

        if nodeA == nodeB:
            raise ThermalNetworkError(f'Cannot connect node \'{nodeA}\' to itself.',
                                      context = createErrorContext(component = 'ThermalNetwork'))

        if resistance <= 0.0:
            raise ThermalNetworkError(
                f'Resistance between \'{nodeA}\' and \'{nodeB}\' must be positive, got '
                f'{resistance}.', context = createErrorContext(component = 'ThermalNetwork'))

        self.resistances[tuple(sorted((nodeA, nodeB)))] = {'resistance': float(resistance),
                                                           'note': note}

    def addConduction(self, nodeA: str, nodeB: str, length: float,
                      conductivity: float, area: float) -> None:

        '''
        Connect two nodes by plane wall conduction.
        '''

        self.addResistance(nodeA, nodeB, conductionResistance(length, conductivity, area),
                           note = f'conduction, {length * 1000.0:.1f} mm')

    def addContact(self, nodeA: str, nodeB: str, area: float,
                   jointType: str = 'bolted, bare, vacuum') -> None:

        '''
        Connect two nodes across a mechanical interface.
        '''

        self.addResistance(nodeA, nodeB, contactResistance(area, jointType = jointType),
                           note = f'contact, {jointType}')

    def addRadiation(self, nodeA: str, nodeB: str, emissivity: float, area: float) -> None:

        '''

        Connect two nodes by radiation.

        The link is stored with its emissivity and area rather than as a fixed resistance, because
        the linearised conductance depends on the temperatures at both ends and those move. Both
        solvers re-form it: the steady state solve iterates until the linearisation is consistent
        with the answer it produced, and the transient re-forms it at every step.

        Freezing it at the temperatures that happened to be set when the link was added makes the
        answer depend on the initial guess, which is not a property a steady state solution is
        allowed to have.

        '''

        resistance = radiationResistance(emissivity, area,
                                         self.nodes[nodeA]['temperature'],
                                         self.nodes[nodeB]['temperature'])

        self.addResistance(nodeA, nodeB, resistance,
                           note = f'radiation, eps {emissivity:.2f}, linearised')

        self.resistances[tuple(sorted((nodeA, nodeB)))]['radiation'] = {
            'emissivity': float(emissivity), 'area': float(area)}

    # -------------------------------------------------------------------------------------------- #

    def _relinearise(self, temperatures: dict = None) -> None:

        '''

        Re-form every radiative link about the supplied temperatures.

        `temperatures` maps node name to temperature; nodes absent from it keep their stored value,
        which is how boundary nodes are handled without special casing them.

        '''

        if not any('radiation' in entry for entry in self.resistances.values()):
            return

        lookup = dict(temperatures) if temperatures else {}

        for (nodeA, nodeB), entry in self.resistances.items():

            if 'radiation' not in entry:
                continue

            hot  = lookup.get(nodeA, self.nodes[nodeA]['temperature'])
            cold = lookup.get(nodeB, self.nodes[nodeB]['temperature'])

            entry['resistance'] = radiationResistance(entry['radiation']['emissivity'],
                                                      entry['radiation']['area'], hot, cold)

    # -------------------------------------------------------------------------------------------- #

    def _assemble(self) -> tuple:

        '''

        Build the conductance matrix and the heat load vector for the free nodes.

        '''

        self._validateNetwork()

        free = [name for name, node in self.nodes.items() if not node['boundary']]
        index = {name: position for position, name in enumerate(free)}

        count = len(free)
        conductance = np.zeros((count, count))
        loads = np.zeros(count)

        for name in free:
            loads[index[name]] += self.nodes[name]['heatLoad']

        for (nodeA, nodeB), entry in self.resistances.items():

            value = 1.0 / entry['resistance']

            freeA = nodeA in index
            freeB = nodeB in index

            if freeA and freeB:
                conductance[index[nodeA], index[nodeA]] += value
                conductance[index[nodeB], index[nodeB]] += value
                conductance[index[nodeA], index[nodeB]] -= value
                conductance[index[nodeB], index[nodeA]] -= value
            elif freeA:
                conductance[index[nodeA], index[nodeA]] += value
                loads[index[nodeA]] += value * self.nodes[nodeB]['temperature']
            elif freeB:
                conductance[index[nodeB], index[nodeB]] += value
                loads[index[nodeB]] += value * self.nodes[nodeA]['temperature']

        return free, index, conductance, loads

    # -------------------------------------------------------------------------------------------- #

    def solveSteadyState(self) -> dict:

        '''

        Solve for the equilibrium temperatures.

        This answers where the network ends up given infinite time, which on a launch vehicle is
        frequently not the question. Nothing reaches steady state during an ascent.

        Radiative links are nonlinear, so the solve is a Picard iteration: linearise about the
        current temperatures, solve, re-linearise about the answer, repeat. Without it the result
        depends on whatever temperatures the nodes happened to be initialised with, which for a
        radiation dominated network is an error of tens of kelvin and no warning.

        '''

        free, index, conductance, loads = self._assemble()

        if not free:
            raise ThermalNetworkError(
                'Every node is a boundary node, so there is nothing to solve for.',
                context = createErrorContext(component = 'ThermalNetwork'))

        radiative = any('radiation' in entry for entry in self.resistances.values())

        temperatures = None
        iterations   = 0
        residual     = 0.0

        for iterations in range(1, RADIATION_MAXIMUM_ITERATIONS + 1):

            try:
                updated = np.linalg.solve(conductance, loads)
            except np.linalg.LinAlgError as error:
                raise ThermalNetworkError(
                    f'The conductance matrix is singular: {error}. A node is probably disconnected '
                    f'from every boundary, so its temperature is undetermined.',
                    context = createErrorContext(component = 'ThermalNetwork')) from error

            if np.any(updated <= 0.0):
                raise ThermalNetworkError(
                    'The steady state solution contains a temperature at or below absolute zero, '
                    'which means the network has a heat load or a boundary that is not physical.',
                    context = createErrorContext(component = 'ThermalNetwork'))

            residual     = 0.0 if temperatures is None else float(np.max(np.abs(updated
                                                                                - temperatures)))
            temperatures = updated

            if not radiative:
                break

            self._relinearise({name: float(temperatures[index[name]]) for name in free})
            free, index, conductance, loads = self._assemble()

            if iterations > 1 and residual < RADIATION_CONVERGENCE_TOLERANCE:
                break

        else:
            raise ThermalNetworkError(
                f'The radiative linearisation did not converge in {RADIATION_MAXIMUM_ITERATIONS} '
                f'iterations, with {residual:.3f} K still moving between passes. The network is '
                f'oscillating rather than settling.',
                context = createErrorContext(component = 'ThermalNetwork'))

        for name in free:
            self.nodes[name]['temperature'] = float(temperatures[index[name]])

        self.findings = []

        if radiative:
            self.findings.append(
                f'The radiative links were re-linearised to convergence in {iterations} '
                f'iterations, settling to within {residual:.2e} K.')

        hottest = max(self.nodes, key = lambda name: self.nodes[name]['temperature'])
        coldest = min(self.nodes, key = lambda name: self.nodes[name]['temperature'])

        self.findings.append(
            f'Steady state spans {self.nodes[coldest]["temperature"]:.1f} K at \'{coldest}\' to '
            f'{self.nodes[hottest]["temperature"]:.1f} K at \'{hottest}\'.')

        self.findings.append(
            'This is the infinite-time answer. Nothing on an ascent reaches it, and where the '
            'event is short the transient peak is the number that matters.')

        return {'temperatures': {name: self.nodes[name]['temperature'] for name in self.nodes},
                'freeNodes':    free,
                'hottest':      hottest,
                'coldest':      coldest,
                'findings':     self.findings}

    # -------------------------------------------------------------------------------------------- #

    def solveTransient(self, heatLoadSchedule: dict = None) -> dict:

        '''

        March the network through time with an implicit scheme.

        `heatLoadSchedule` maps a node name to a callable of time returning its heat load in watts,
        which is how a heat pulse is applied. Nodes not in the schedule keep their constant load.

        The scheme is backward Euler, which is unconditionally stable. An explicit march would be
        limited by the smallest node's time constant, and on a network mixing a thin skin with a
        heavy structure that limit is punitive.

        Radiative links are re-linearised at every step about the temperatures at the end of the
        previous one. That is a lagged linearisation rather than a fully implicit treatment of the
        fourth power, which is the standard compromise: it costs one matrix assembly per step and it
        removes the error that comes from holding a conductance fixed across a transient that moves
        hundreds of kelvin. A soakback case is exactly that transient.

        '''

        free, index, conductance, baseLoads = self._assemble()

        if not free:
            raise ThermalNetworkError('Every node is a boundary node.',
                                      context = createErrorContext(component = 'ThermalNetwork'))

        capacitances = np.array([self.nodes[name]['capacitance'] for name in free])

        if np.any(capacitances <= 0.0):
            massless = [name for name in free if self.nodes[name]['capacitance'] <= 0.0]
            raise ThermalNetworkError(
                f'Nodes {massless} have no capacitance, so they cannot be marched in time. Give '
                f'them a thermal mass or make them boundary nodes.',
                context = createErrorContext(component = 'ThermalNetwork'))

        steps = int(np.ceil(self.endTime / self.timeStep))
        times = np.linspace(0.0, steps * self.timeStep, steps + 1)

        temperatures = np.array([self.nodes[name]['temperature'] for name in free])
        history = np.zeros((steps + 1, len(free)))
        history[0, :] = temperatures

        capacitanceMatrix = np.diag(capacitances / self.timeStep)

        radiative = any('radiation' in entry for entry in self.resistances.values())

        for step in range(1, steps + 1):

            if radiative and step > 1:
                self._relinearise({name: float(temperatures[index[name]]) for name in free})
                _, _, conductance, baseLoads = self._assemble()

            time = times[step]
            loads = baseLoads.copy()

            if heatLoadSchedule:
                for name, schedule in heatLoadSchedule.items():
                    if name in index:
                        loads[index[name]] += float(schedule(time))
                    elif name not in self.nodes:
                        raise ThermalNetworkError(
                            f'Heat load scheduled on unknown node \'{name}\'.',
                            context = createErrorContext(component = 'ThermalNetwork'))

            # backward Euler: (C/dt + K) T_new = C/dt T_old + Q
            leftHand  = capacitanceMatrix + conductance
            rightHand = capacitanceMatrix @ temperatures + loads

            temperatures = np.linalg.solve(leftHand, rightHand)
            history[step, :] = temperatures

        for name in free:
            self.nodes[name]['temperature'] = float(temperatures[index[name]])

        self.history = {'time': times,
                        'nodes': free,
                        'temperatures': history}

        return self._analyseTransient(times, free, history)

    # -------------------------------------------------------------------------------------------- #

    def _analyseTransient(self, times: np.ndarray, free: list,
                          history: np.ndarray) -> dict:

        '''

        Extract the peaks and, importantly, when each one occurred.

        '''

        self.findings = []

        peaks = {}
        for position, name in enumerate(free):
            trace = history[:, position]
            peakIndex = int(np.argmax(trace))
            peaks[name] = {'peakTemperature': float(trace[peakIndex]),
                           'peakTime':        float(times[peakIndex]),
                           'finalTemperature': float(trace[-1]),
                           'initialTemperature': float(trace[0]),
                           'rise':            float(trace[peakIndex] - trace[0])}

        # soakback: a node whose peak occurs meaningfully after the start is being fed by heat
        # that was already in the structure when the event ended
        soakedBack = {name: entry for name, entry in peaks.items()
                      if entry['peakTime'] > times[1] and entry['rise'] > 1.0}

        latest = max(peaks, key = lambda name: peaks[name]['peakTime'])

        if peaks[latest]['peakTime'] > 0.0:
            self.findings.append(
                f'The latest peak is \'{latest}\' at {peaks[latest]["peakTemperature"]:.1f} K, '
                f'{peaks[latest]["peakTime"]:.0f} s into the run.')

        hottest = max(peaks, key = lambda name: peaks[name]['peakTemperature'])
        self.findings.append(
            f'The hottest node is \'{hottest}\' at {peaks[hottest]["peakTemperature"]:.1f} K, '
            f'peaking at {peaks[hottest]["peakTime"]:.0f} s.')

        # A peak at the final time step is not a peak. The node was still rising when the run
        # stopped, so the reported maximum is a truncation artefact and the real one is higher.
        # This is easy to miss precisely because the number looks like an answer.
        stillRising = [name for name, entry in peaks.items()
                       if np.isclose(entry['peakTime'], times[-1]) and entry['rise'] > 0.0]

        if stillRising:
            self.findings.append(
                f'{sorted(stillRising)} peak at the last time step, which means they were still '
                f'rising when the run ended. Those are not peaks, they are truncation artefacts, '
                f'and the real maxima are higher. Extend endTime past {times[-1]:.0f} s.')

        return {'time':        times,
                'stillRising': sorted(stillRising),
                'truncated':   bool(stillRising),
                'nodes':       free,
                'temperatures': history,
                'peaks':       peaks,
                'soakedBack':  soakedBack,
                'latestPeak':  latest,
                'hottestNode': hottest,
                'findings':    self.findings}

    # -------------------------------------------------------------------------------------------- #

    def findSoakback(self, eventEndTime: float) -> dict:

        '''

        Which nodes peak after the heating event ended, and by how much.

        This is the reason a transient solve is run at all. After the heat input stops, the energy
        already in the surface keeps moving inward, and interior nodes frequently reach their
        maximum well after the event. A model run only for the duration of the pulse misses the
        peak entirely.

        '''

        if self.history is None:
            raise ThermalNetworkError('Run solveTransient before looking for soakback.',
                                      context = createErrorContext(component = 'ThermalNetwork'))

        times = self.history['time']
        free  = self.history['nodes']
        history = self.history['temperatures']

        if eventEndTime >= times[-1]:
            raise InvalidInputError(
                f'The event ends at {eventEndTime:.1f} s and the run stops at {times[-1]:.1f} s, '
                f'so there is no post-event period to examine. Extend endTime.',
                context = createErrorContext(component = 'ThermalNetwork'))

        endIndex = int(np.searchsorted(times, eventEndTime))

        results = {}
        for position, name in enumerate(free):

            trace = history[:, position]

            duringPeak = float(np.max(trace[:endIndex + 1]))
            afterPeak  = float(np.max(trace[endIndex:]))
            peakIndex  = int(np.argmax(trace))

            results[name] = {'peakDuringEvent': duringPeak,
                             'peakAfterEvent':  afterPeak,
                             'overallPeak':     float(trace[peakIndex]),
                             'peakTime':        float(times[peakIndex]),
                             'soaksBack':       bool(times[peakIndex] > eventEndTime),
                             'soakbackRise':    afterPeak - duringPeak}

        soaking = {name: entry for name, entry in results.items() if entry['soaksBack']}

        findings = []

        if soaking:
            worst = max(soaking, key = lambda name: soaking[name]['soakbackRise'])
            findings.append(
                f'{len(soaking)} node(s) peak after the event ends at {eventEndTime:.0f} s. The '
                f'worst is \'{worst}\', which reaches {soaking[worst]["overallPeak"]:.1f} K at '
                f'{soaking[worst]["peakTime"]:.0f} s, '
                f'{soaking[worst]["soakbackRise"]:.1f} K above its peak during the event.')
            findings.append(
                'A model stopped at the end of the heat pulse would have reported the lower '
                'number. This is the recurring cause of hardware that passes analysis and fails '
                'test.')
        else:
            findings.append(
                f'No node peaks after {eventEndTime:.0f} s, so soakback is not governing here. '
                f'That is worth confirming rather than assuming.')

        return {'eventEndTime': eventEndTime,
                'nodes':        results,
                'soakingNodes': sorted(soaking),
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def checkLumpedCapacitance(self, node: str, coefficient: float,
                               characteristicLength: float, conductivity: float) -> dict:

        '''

        Whether a node can honestly be represented as a single lump.

        Above a Biot number of 0.1 there is a real internal gradient, and a one-node model
        understates the surface temperature. That is the unconservative direction for anything
        whose surface is the thing at risk.

        '''

        if node not in self.nodes:
            raise InvalidInputError(f'No node named \'{node}\'.',
                                    context = createErrorContext(component = 'ThermalNetwork'))

        biot = biotNumber(coefficient, characteristicLength, conductivity)
        valid = biot < LUMPED_CAPACITANCE_BIOT_LIMIT

        findings = []
        if not valid:
            findings.append(
                f'Biot number {biot:.3f} exceeds {LUMPED_CAPACITANCE_BIOT_LIMIT:.1f}, so '
                f'\'{node}\' has a real internal gradient. A single node understates its surface '
                f'temperature, which is the unconservative direction. Subdivide it.')

        return {'node':        node,
                'biotNumber':  biot,
                'limit':       LUMPED_CAPACITANCE_BIOT_LIMIT,
                'lumpedValid': bool(valid),
                'suggestedNodes': max(1, int(np.ceil(biot / LUMPED_CAPACITANCE_BIOT_LIMIT))),
                'findings':    findings}

    # -------------------------------------------------------------------------------------------- #

    def resistanceSensitivity(self) -> dict:

        '''

        Which resistance the answer depends on most.

        In practice this is the useful output of a network. Contact conductance is usually the
        dominant resistance and the least well known number in the model, and refining a resistance
        that carries five percent of the total cannot move the answer no matter how well it is
        known.

        '''

        self._validateNetwork()

        total = sum(entry['resistance'] for entry in self.resistances.values())

        if total <= 0.0:
            raise ThermalNetworkError('The network has no resistance.',
                                      context = createErrorContext(component = 'ThermalNetwork'))

        shares = {f'{nodeA} to {nodeB}': {'resistance': entry['resistance'],
                                          'fraction':   entry['resistance'] / total,
                                          'note':       entry['note']}
                  for (nodeA, nodeB), entry in self.resistances.items()}

        dominant = max(shares, key = lambda name: shares[name]['fraction'])

        findings = []
        findings.append(
            f'\'{dominant}\' carries {shares[dominant]["fraction"] * 100.0:.0f} % of the series '
            f'resistance. That is where the uncertainty in the answer lives.')

        negligible = [name for name, entry in shares.items()
                      if entry['fraction'] < SENSITIVITY_REPORTING_THRESHOLD]
        if negligible:
            findings.append(
                f'{len(negligible)} resistance(s) carry under '
                f'{SENSITIVITY_REPORTING_THRESHOLD * 100.0:.0f} % each. Refining them cannot move '
                f'the answer.')

        contactPaths = [name for name, entry in shares.items() if 'contact' in entry['note']]
        if contactPaths:
            contactShare = sum(shares[name]['fraction'] for name in contactPaths)
            findings.append(
                f'Contact interfaces carry {contactShare * 100.0:.0f} % of the total. Contact '
                f'conductance spans a factor of forty across joint types, so that fraction is also '
                f'the least certain part of the model.')

        return {'shares':     shares,
                'dominant':   dominant,
                'totalSeries': total,
                'findings':   findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the network and its solution.
        '''

        steady = self.solveSteadyState()
        sensitivity = self.resistanceSensitivity()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  THERMAL NETWORK: {len(self.nodes)} nodes, '
                     f'{len(self.resistances)} resistances')
        lines.append('=' * 96)
        lines.append('')

        rows = [[name,
                 'boundary' if node['boundary'] else f'{node["capacitance"]:.0f}',
                 f'{node["temperature"]:.1f}',
                 f'{node["heatLoad"]:.1f}']
                for name, node in self.nodes.items()]
        lines.append(formatReportTable(rows, ['Node', 'C [J/K]', 'T [K]', 'Q [W]'],
                                       title = 'Steady state'))
        lines.append('')

        resistanceRows = [[name, f'{entry["resistance"]:.4f}',
                           f'{entry["fraction"] * 100.0:.1f}',
                           entry['note']]
                          for name, entry in sorted(sensitivity['shares'].items(),
                                                    key = lambda item: -item[1]['fraction'])]
        lines.append(formatReportTable(resistanceRows,
                                       ['Path', 'R [K/W]', 'Share [%]', 'Type'],
                                       title = 'Resistances'))

        allFindings = steady['findings'] + sensitivity['findings']
        if allFindings:
            lines.append('')
            lines.append('  FINDINGS')
            for finding in allFindings:
                lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir is not None:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'thermalNetwork.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateNetwork(self) -> None:

        '''
        Check the network is well formed and connected.
        '''

        context = createErrorContext(component = 'ThermalNetwork')

        if not self.nodes:
            raise ThermalNetworkError('The network has no nodes.', context = context)

        if not self.resistances:
            raise ThermalNetworkError('The network has no resistances, so nothing is connected.',
                                      context = context)

        if not any(node['boundary'] for node in self.nodes.values()):
            raise ThermalNetworkError(
                'No boundary node. Every temperature is then relative and the network has no '
                'reference, so the steady state solve is singular.', context = context)

        connected = set()
        for nodeA, nodeB in self.resistances:
            connected.add(nodeA)
            connected.add(nodeB)

        orphans = set(self.nodes) - connected
        if orphans:
            raise ThermalNetworkError(
                f'Nodes {sorted(orphans)} are not connected to anything. Their temperature is '
                f'undetermined.', context = context)

        if self.timeStep <= 0.0:
            raise InvalidInputError('Time step must be positive.', context = context)

        if self.endTime <= 0.0:
            raise InvalidInputError('End time must be positive.', context = context)
