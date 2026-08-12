
# -- TelemetryBudget -- #

'''

What fits down the link, what does not, and the measurement you will wish you had recorded.

A telemetry budget is a bandwidth allocation problem with one unusual property: **the cost of
getting it wrong is not paid during the flight, it is paid during the investigation afterwards.**
A channel that was not recorded is not a degraded measurement, it is an absence, and the absence is
discovered at the worst possible moment.

The arithmetic is straightforward. A measurement at a sample rate and a word length is a bit rate,
the sum has to fit the link, and the link has a margin. What the arithmetic makes visible is the
trade: **channel count and sample rate compete for the same bandwidth**, and the instinct to sample
everything fast produces a list that does not fit and gets cut by whoever is least attached to
their channel rather than by what matters.

The second thing worth having is the distinction between what is downlinked and what is recorded.
A recorder is not bandwidth-limited and it has to survive; a downlink is bandwidth-limited and it
arrives regardless. **They fail in opposite ways**, which is the argument for having both.

Author: Sean Bowman
Date:   10/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from avionicsUtils import (nyquistRate, applyInputs, formatReportTable, createErrorContext,
                               InvalidInputError, TelemetryError)
except ImportError:
    from .avionicsUtils import (nyquistRate, applyInputs, formatReportTable, createErrorContext,
                                InvalidInputError, TelemetryError)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Framing, synchronisation and error correction overhead as a fraction of the payload bit rate.
# Representative and registered as unvalidated.
FRAMING_OVERHEAD = 0.20    # [-]

# Link margin required above the computed rate. A link with no margin is a link that drops frames
# at the first antenna null.
LINK_MARGIN = 0.25    # [-]

# Samples per cycle needed to resolve a transient's amplitude and shape rather than merely detect
# its frequency. The same distinction propulsionTesting makes about combustion instability.
RESOLUTION_FACTOR = 10.0    # [-]

# ------------------------------------------------------------------------------------------------ #
# -- TelemetryBudget -- #
# ------------------------------------------------------------------------------------------------ #

class TelemetryBudget:

    '''

    Bit rate from a measurement list, link margin, and the sample rate adequacy of each channel.

    '''

    def __init__(self):

        self.measurements = []
        self.linkCapacity = np.nan
        self.recorderCapacity = np.nan
        self.flightTime   = np.nan

        self.findings = []

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        `measurements` is a list of dictionaries with a `name`, a `count`, a `sampleRate` in hertz,
        a `wordLength` in bits, and optionally a `signalFrequency` giving the highest frequency the
        channel is meant to represent.

        `linkCapacity` is the downlink bit rate available, and `recorderCapacity` the onboard
        storage in bits.

        '''

        requiredParams = {'measurements': list,
                          'linkCapacity': (int, float)}

        optionalParams = {'recorderCapacity': (int, float),
                          'flightTime':       (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    # -------------------------------------------------------------------------------------------- #

    def calculateBitRate(self) -> dict:

        '''

        The bit rate the measurement list demands, before and after framing overhead.

        '''

        detail = []

        payload = 0.0

        for entry in self.measurements:

            rate = entry['count'] * entry['sampleRate'] * entry['wordLength']

            payload += rate

            detail.append({'name':       entry['name'],
                           'count':      entry['count'],
                           'sampleRate': entry['sampleRate'],
                           'wordLength': entry['wordLength'],
                           'bitRate':    rate})

        framed = payload * (1.0 + FRAMING_OVERHEAD)

        for item in detail:
            item['share'] = item['bitRate'] / payload

        return {'detail':      detail,
                'payloadRate': payload,
                'framedRate':  framed,
                'overhead':    framed - payload,
                'channelCount': sum(entry['count'] for entry in self.measurements)}

    # -------------------------------------------------------------------------------------------- #

    def checkLink(self) -> dict:

        '''

        Whether the list fits the downlink with margin, and by how much it does not.

        Refused rather than reported when it does not fit, because a telemetry plan that exceeds
        its link does not degrade gracefully: the frames that do not fit are simply absent, and
        which ones are absent is decided by the framing rather than by anybody's priorities.

        '''

        findings = []

        rate = self.calculateBitRate()

        required = rate['framedRate'] * (1.0 + LINK_MARGIN)

        findings.append(
            f'{rate["channelCount"]} channels demand {rate["payloadRate"] / 1000.0:.1f} kbit/s, '
            f'{rate["framedRate"] / 1000.0:.1f} with {FRAMING_OVERHEAD:.0%} framing.')

        findings.append(
            f'With a {LINK_MARGIN:.0%} link margin that needs {required / 1000.0:.1f} kbit/s '
            f'against {self.linkCapacity / 1000.0:.1f} available.')

        if required > self.linkCapacity:

            excess = required / self.linkCapacity

            raise TelemetryError(
                f'The measurement list needs {required / 1000.0:.1f} kbit/s including framing and '
                f'margin, against a {self.linkCapacity / 1000.0:.1f} kbit/s link. It is over by a '
                f'factor of {excess:.2f}. **A telemetry plan that exceeds its link does not '
                f'degrade gracefully**: the frames that do not fit are absent, and which ones are '
                f'absent is decided by the framing rather than by anybody priorities. Cut the '
                f'list deliberately, and record what was cut and why.',
                context = createErrorContext(component = 'TelemetryBudget'))

        findings.append(
            f'It fits, with {self.linkCapacity / required:.2f} times the required rate available.')

        self.findings = findings

        return {'payloadRate':  rate['payloadRate'],
                'framedRate':   rate['framedRate'],
                'requiredRate': required,
                'capacity':     self.linkCapacity,
                'utilisation':  required / self.linkCapacity,
                'fits':         True,
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def checkSampleRates(self) -> dict:

        '''

        Whether each channel is sampled fast enough to represent what it is measuring.

        Two thresholds, as elsewhere in this repository. Nyquist says whether the frequency is
        representable at all; ten samples per cycle is what it takes to recover an amplitude and a
        shape, and a transient is a shape.

        **A channel below Nyquist does not miss its signal, it aliases it** into a lower frequency
        that is not there, which is worse than not measuring.

        '''

        findings = []

        results = {}

        aliasing = []
        coarse   = []

        for entry in self.measurements:

            if 'signalFrequency' not in entry:
                continue

            frequency = entry['signalFrequency']

            detect  = 2.0 * frequency
            resolve = RESOLUTION_FACTOR * frequency

            status = ('resolves' if entry['sampleRate'] >= resolve
                      else 'detects' if entry['sampleRate'] >= detect
                      else 'aliases')

            results[entry['name']] = {'sampleRate':     entry['sampleRate'],
                                      'signalFrequency': frequency,
                                      'detectRate':     detect,
                                      'resolveRate':    resolve,
                                      'status':         status}

            if status == 'aliases':
                aliasing.append(entry['name'])
            elif status == 'detects':
                coarse.append(entry['name'])

        if aliasing:
            raise TelemetryError(
                f'These channels are sampled below Nyquist for the frequency they are meant to '
                f'represent: {aliasing}. **A channel below Nyquist does not miss its signal, it '
                f'aliases it** into a lower frequency that is not there, and an investigation '
                f'reading that data will chase something that never happened. Raise the rate, '
                f'filter ahead of the sampler, or lower the stated signal frequency to what is '
                f'actually being measured.',
                context = createErrorContext(component = 'TelemetryBudget'))

        findings.append(
            f'{len(results)} channels have a stated signal frequency and none aliases.')

        if coarse:
            findings.append(
                f'{len(coarse)} of them detect without resolving: {coarse}. Those channels can say '
                f'that something happened and not how large it was, which is enough for a health '
                f'check and not enough for an investigation.')

        self.findings = findings

        return {'results':  results,
                'aliasing': aliasing,
                'coarse':   coarse,
                'allResolve': bool(not aliasing and not coarse),
                'findings': findings}

    # -------------------------------------------------------------------------------------------- #

    def checkRecorder(self) -> dict:

        '''

        Whether the onboard recorder holds the flight, and what it buys over the downlink.

        The recorder and the downlink fail in opposite ways. **A recorder is not bandwidth-limited
        and it has to survive; a downlink is bandwidth-limited and it arrives regardless.** That is
        the whole argument for having both, and it is why a vehicle that records everything and
        downlinks a subset is the usual arrangement.

        '''

        if not np.isfinite(self.recorderCapacity) or not np.isfinite(self.flightTime):
            raise InvalidInputError(
                'A recorder capacity and a flight time are both needed. Without the flight time a '
                'capacity is not a duration, which is the thing worth knowing.',
                context = createErrorContext(component = 'TelemetryBudget'))

        findings = []

        rate = self.calculateBitRate()

        stored = rate['framedRate'] * self.flightTime

        duration = self.recorderCapacity / rate['framedRate']

        fits = bool(stored <= self.recorderCapacity)

        findings.append(
            f'At {rate["framedRate"] / 1000.0:.1f} kbit/s the recorder holds '
            f'{duration / 60.0:.1f} minutes against a {self.flightTime / 60.0:.1f} minute flight.')

        if not fits:
            raise TelemetryError(
                f'The recorder holds {duration / 60.0:.1f} minutes and the flight is '
                f'{self.flightTime / 60.0:.1f}. It runs out before the end, and **the end is the '
                f'part an investigation wants most.** Either the capacity rises or the recorded '
                f'list is cut, and cutting it deliberately is better than the recorder deciding.',
                context = createErrorContext(component = 'TelemetryBudget'))

        findings.append(
            f'The recorder is not bandwidth-limited and it has to survive; the downlink is '
            f'bandwidth-limited and it arrives regardless. **They fail in opposite ways**, which '
            f'is why a vehicle usually records everything and downlinks a subset.')

        self.findings = findings

        return {'framedRate':   rate['framedRate'],
                'storedBits':   stored,
                'capacity':     self.recorderCapacity,
                'duration':     duration,
                'margin':       duration / self.flightTime,
                'fits':         fits,
                'findings':     findings}

    # -------------------------------------------------------------------------------------------- #

    def compareAllocations(self, factors: list = None) -> dict:

        '''

        The trade between channel count and sample rate, at fixed bandwidth.

        They compete for the same bits, and the instinct to sample everything fast produces a list
        that does not fit. Showing the trade explicitly is what turns the cut from an argument into
        a decision.

        '''

        if factors is None:
            factors = [0.5, 1.0, 2.0, 4.0]

        rate = self.calculateBitRate()

        available = self.linkCapacity / (1.0 + LINK_MARGIN) / (1.0 + FRAMING_OVERHEAD)

        results = {}

        for factor in factors:

            demanded = rate['payloadRate'] * factor

            results[factor] = {'payloadRate':     demanded,
                               'fits':            bool(demanded <= available),
                               'channelsAffordable': (rate['channelCount'] * available / demanded)}

        return {'available': available,
                'results':   results,
                'baselineChannels': rate['channelCount']}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        Assemble the full telemetry budget report.
        '''

        rate = self.calculateBitRate()
        link = self.checkLink()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  TELEMETRY BUDGET: {rate["channelCount"]} channels on a '
                     f'{self.linkCapacity / 1000.0:.0f} kbit/s link')
        lines.append('=' * 96)
        lines.append('')

        lines.append(formatReportTable(
            [[entry['name'],
              f'{entry["count"]}',
              f'{entry["sampleRate"]:.0f}',
              f'{entry["wordLength"]}',
              f'{entry["bitRate"] / 1000.0:.2f}',
              f'{entry["share"]:.0%}']
             for entry in sorted(rate['detail'], key = lambda item: -item['bitRate'])],
            ['Group', 'Channels', 'Rate [Hz]', 'Bits', 'kbit/s', 'Share'],
            title = 'Measurement list'))

        lines.append('')
        lines.append(formatReportTable(
            [['Payload rate',   f'{link["payloadRate"] / 1000.0:.2f}',   'kbit/s'],
             ['With framing',   f'{link["framedRate"] / 1000.0:.2f}',    'kbit/s'],
             ['With margin',    f'{link["requiredRate"] / 1000.0:.2f}',  'kbit/s'],
             ['Link capacity',  f'{link["capacity"] / 1000.0:.2f}',      'kbit/s'],
             ['Utilisation',    f'{link["utilisation"]:.0%}',            '']],
            ['Quantity', 'Value', 'Unit'], title = 'Link'))

        lines.append('')
        for finding in link['findings']:
            lines.append(f'    - {finding}')

        lines.append('')
        lines.append('=' * 96)

        report = '\n'.join(lines)

        if outputDir:
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'telemetry_budget.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Guard the inputs that produce a confidently wrong answer rather than an error.
        '''

        if not self.measurements:
            raise InvalidInputError(
                'A telemetry budget needs at least one measurement group.',
                context = createErrorContext(component = 'TelemetryBudget'))

        names = set()

        for index, entry in enumerate(self.measurements):

            for key in ('name', 'count', 'sampleRate', 'wordLength'):
                if key not in entry:
                    raise InvalidInputError(
                        f'Measurement group {index + 1} has no {key}.',
                        context = createErrorContext(component = 'TelemetryBudget'))

            if entry['name'] in names:
                raise InvalidInputError(
                    f"Duplicate measurement group name '{entry['name']}'.",
                    context = createErrorContext(component = 'TelemetryBudget'))

            names.add(entry['name'])

            for key in ('count', 'sampleRate', 'wordLength'):
                if entry[key] <= 0:
                    raise InvalidInputError(
                        f"Measurement group '{entry['name']}' has a non-positive {key}.",
                        context = createErrorContext(component = 'TelemetryBudget'))

            if 'signalFrequency' in entry and entry['signalFrequency'] <= 0.0:
                raise InvalidInputError(
                    f"Measurement group '{entry['name']}' has a non-positive signal frequency.",
                    context = createErrorContext(component = 'TelemetryBudget'))

        if self.linkCapacity <= 0.0:
            raise InvalidInputError(
                f'The link capacity must be positive, got {self.linkCapacity}.',
                context = createErrorContext(component = 'TelemetryBudget'))

        for name, value in (('recorder capacity', self.recorderCapacity),
                            ('flight time',       self.flightTime)):
            if np.isfinite(value) and value <= 0.0:
                raise InvalidInputError(
                    f'The {name} must be positive, got {value}.',
                    context = createErrorContext(component = 'TelemetryBudget'))
