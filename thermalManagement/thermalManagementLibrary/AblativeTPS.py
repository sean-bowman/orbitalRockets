
# -- AblativeTPS Class Definition -- #

'''

Ablative thermal protection: recession, char depth, backface temperature and sizing to a heat pulse.

An ablative works by destroying itself in a controlled way. The surface pyrolyses, the gases blow
outward through the char and thicken the boundary layer, the char radiates at its surface
temperature, and the material recedes. Each of those absorbs energy, and the effective heat of
ablation lumps them into one number.

That lumping is coarse and it is genuinely useful:

    s_dot = q_net / (rho H_ablation)

It says the recession rate is the net heat flux divided by the energy the material absorbs per unit
mass. Everything difficult is inside `H_ablation`, which is why it is measured in an arc jet rather
than derived.

Two things decide whether an ablative is the right answer, and neither is the peak heat flux:

**The integrated heat load, not the peak flux, sizes the material.** Recession is a time integral,
so a long moderate pulse removes more material than a short severe one at the same peak. A design
sized on peak flux is sized against the wrong quantity.

**The backface temperature is what actually has to be met.** The requirement is almost never on the
surface, which is allowed to reach thousands of kelvin. It is on the structure behind, and the
material thickness is set by the insulation the remaining virgin layer provides.

Char conductivity is the parameter that decides how well that works. Carbon phenolic recedes less
than silica phenolic and conducts far more heat through its char, so it is the better material for
a short severe pulse and the worse one for a long soak.

See Also:
---------
ThermalNetwork : The backface node, and the soakback after the pulse ends
Radiator       : Radiative rejection, the other way to lose heat at temperature

Theory: docs/AeroheatingAndTPS.md

Author: Sean Bowman
Date:   08/08/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import os

import numpy as np

try:
    from thermalUtils import (applyInputs, formatReportTable, thermalDiffusivity,
                              thermalPenetrationDepth, STEFAN_BOLTZMANN, ABLATIVE_MATERIALS,
                              InvalidInputError, AblationError, createErrorContext)
except ImportError:
    from .thermalUtils import (applyInputs, formatReportTable, thermalDiffusivity,
                               thermalPenetrationDepth, STEFAN_BOLTZMANN, ABLATIVE_MATERIALS,
                               InvalidInputError, AblationError, createErrorContext)

# ------------------------------------------------------------------------------------------------ #
# -- Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Blowing reduces the convective heat transfer by thickening the boundary layer. The blockage
# factor is the fraction of the cold-wall flux that actually reaches the surface, and it is one of
# the reasons an ablative outperforms a passive insulator at the same conductivity.
BLOWING_BLOCKAGE_DEFAULT = 0.70    # [-], fraction of cold wall flux reaching the surface

# Emissivity of a charred ablating surface. Char is close to a black body and this is not a
# sensitive parameter, but it must be the same one everywhere in the energy balance.
SURFACE_EMISSIVITY = 0.85    # [-]

# Margin on the sized thickness. Ablation correlations carry real uncertainty and the failure mode
# is burn-through, so the margin is applied to the material rather than to the load.
THICKNESS_MARGIN_DEFAULT = 1.25    # [-]

# Below this backface temperature rise a design is insulation limited rather than recession limited,
# which changes which material property matters.
RECESSION_LIMITED_FRACTION = 0.5    # [-], recession as a fraction of the total thickness

# ------------------------------------------------------------------------------------------------ #
# -- AblativeTPS -- #
# ------------------------------------------------------------------------------------------------ #

class AblativeTPS:

    '''

    Ablative heat shield sizing.

    Usage:
    ------
        shield = AblativeTPS()
        shield.setInputs({'material': 'PICA', 'peakHeatFlux': 1.2e6,
                          'heatLoad': 1.5e8, 'pulseDuration': 180.0,
                          'backfaceLimit': 450.0})
        result = shield.sizeThickness()

    '''

    def __init__(self):

        # -- Material -- #

        self.material          = 'silica phenolic'   # key into ABLATIVE_MATERIALS
        self.heatOfAblation    = np.nan  # [J/kg], overrides the table
        self.density           = np.nan  # [kg/m^3]
        self.charConductivity  = np.nan  # [W/m/K]
        self.virginConductivity = np.nan # [W/m/K]
        self.specificHeat      = np.nan  # [J/kg/K]
        self.surfaceTemperature = np.nan # [K], the ablating surface temperature

        # -- Environment -- #

        self.peakHeatFlux      = np.nan  # [W/m^2], cold wall
        self.heatLoad          = np.nan  # [J/m^2], integrated over the pulse
        self.pulseDuration     = np.nan  # [s]
        self.blowingBlockage   = BLOWING_BLOCKAGE_DEFAULT   # [-]

        # -- Requirement -- #

        self.backfaceLimit     = 450.0   # [K], the structure behind the shield
        self.initialTemperature = 293.15 # [K]
        self.thicknessMargin   = THICKNESS_MARGIN_DEFAULT   # [-]

        # -- Results -- #

        self.findings          = []      # [-]

    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: peakHeatFlux, pulseDuration.

        '''

        requiredParams = {'peakHeatFlux':  (int, float),
                          'pulseDuration': (int, float)}

        optionalParams = {'material':            str,
                          'heatOfAblation':      (int, float),
                          'density':             (int, float),
                          'charConductivity':    (int, float),
                          'virginConductivity':  (int, float),
                          'specificHeat':        (int, float),
                          'surfaceTemperature':  (int, float),
                          'heatLoad':            (int, float),
                          'blowingBlockage':     (int, float),
                          'backfaceLimit':       (int, float),
                          'initialTemperature':  (int, float),
                          'thicknessMargin':     (int, float)}

        applyInputs(self, inputs, requiredParams, optionalParams)

        if self.material not in ABLATIVE_MATERIALS:
            raise InvalidInputError(
                f'Unknown ablative \'{self.material}\'. Known: {sorted(ABLATIVE_MATERIALS)}.',
                context = createErrorContext(component = 'AblativeTPS'))

        entry = ABLATIVE_MATERIALS[self.material]

        for name, key in (('heatOfAblation', 'heatOfAblation'), ('density', 'density'),
                          ('charConductivity', 'charConductivity'),
                          ('virginConductivity', 'virginConductivity'),
                          ('specificHeat', 'specificHeat'),
                          ('surfaceTemperature', 'surfaceTemperature')):
            if not np.isfinite(getattr(self, name)):
                setattr(self, name, entry[key])

        # a rectangular pulse is assumed where the integrated load was not supplied
        if not np.isfinite(self.heatLoad):
            self.heatLoad = self.peakHeatFlux * self.pulseDuration

    # -------------------------------------------------------------------------------------------- #

    def calculateNetHeatFlux(self) -> dict:

        '''

        The flux actually reaching the surface, after blowing blockage and surface re-radiation.

        An ablating surface sits at a very high temperature and radiates hard. At 3000 K a surface
        with emissivity 0.85 rejects nearly 4 MW/m^2 by radiation alone, which for a moderate
        entry is a large fraction of the incoming flux.

        '''

        self._validateInputs()

        blocked = self.peakHeatFlux * self.blowingBlockage

        # The surface temperature is an output of the energy balance, not an input. The tabulated
        # value is the temperature the material holds while it is ablating hard; below the flux
        # that sustains that, the surface simply sits at radiative equilibrium and does not recede.
        #
        # Using the tabulated temperature regardless overstates re-radiation, drives the net flux
        # negative, and then oversizes the insulation against a surface hotter than the real one.
        equilibrium = (blocked / (SURFACE_EMISSIVITY * STEFAN_BOLTZMANN)) ** 0.25

        ablating = equilibrium >= self.surfaceTemperature
        actual   = self.surfaceTemperature if ablating else equilibrium

        reradiated = SURFACE_EMISSIVITY * STEFAN_BOLTZMANN * actual ** 4

        net = max(blocked - reradiated, 0.0)

        findings = []
        findings.append(
            f'Of {self.peakHeatFlux / 1.0e6:.2f} MW/m^2 cold wall, blowing blocks '
            f'{(1.0 - self.blowingBlockage) * 100.0:.0f} %, leaving '
            f'{blocked / 1.0e6:.2f} MW/m^2 at the surface.')

        if ablating:
            findings.append(
                f'The surface holds at its ablation temperature of {actual:.0f} K, rejecting '
                f'{reradiated / 1.0e6:.2f} MW/m^2 by radiation and leaving '
                f'{net / 1.0e6:.2f} MW/m^2 to drive recession.')
        else:
            findings.append(
                f'The flux is not enough to sustain ablation. The surface sits at its radiative '
                f'equilibrium of {equilibrium:.0f} K, below the {self.surfaceTemperature:.0f} K '
                f'ablation temperature, so the material does not recede and is acting as a '
                f'radiating hot structure. Sizing it as an ablative here is sizing the wrong '
                f'mechanism.')

        return {'coldWallFlux':      self.peakHeatFlux,
                'afterBlowing':      blocked,
                'equilibriumTemperature': equilibrium,
                'ablationTemperature': self.surfaceTemperature,
                'surfaceTemperature': actual,
                'isAblating':        bool(ablating),
                'reradiated':        reradiated,
                'netFlux':           net,
                'blockageFactor':    self.blowingBlockage,
                'findings':          findings}

    # -------------------------------------------------------------------------------------------- #

    def calculateRecession(self) -> dict:

        '''

        Recession depth over the pulse.

            s_dot = q_net / (rho H_ablation)

        Recession is a time integral, so the integrated heat load rather than the peak flux is what
        removes material. A long moderate pulse takes more than a short severe one at the same
        peak, and sizing on peak flux is sizing against the wrong quantity.

        '''

        self._validateInputs()

        flux = self.calculateNetHeatFlux()

        rate = flux['netFlux'] / (self.density * self.heatOfAblation)

        # Integrated over the pulse, using the mean flux from the heat load rather than the peak.
        # The same energy balance applies here: the surface only holds at its ablation temperature
        # if the mean flux sustains it, and otherwise it sits at the mean radiative equilibrium and
        # does not recede.
        meanFlux    = self.heatLoad / self.pulseDuration
        meanBlocked = meanFlux * self.blowingBlockage

        meanEquilibrium = (meanBlocked / (SURFACE_EMISSIVITY * STEFAN_BOLTZMANN)) ** 0.25
        meanAblating    = meanEquilibrium >= self.surfaceTemperature
        meanSurface     = self.surfaceTemperature if meanAblating else meanEquilibrium

        meanNet = max(meanBlocked
                      - SURFACE_EMISSIVITY * STEFAN_BOLTZMANN * meanSurface ** 4, 0.0)

        depth = meanNet / (self.density * self.heatOfAblation) * self.pulseDuration

        findings = list(flux['findings'])

        peakDepth = rate * self.pulseDuration
        if peakDepth > depth * 1.05:
            findings.append(
                f'Sizing on the peak flux would give {peakDepth * 1000.0:.2f} mm of recession '
                f'against {depth * 1000.0:.2f} mm from the integrated load. Recession is a time '
                f'integral, so the load is the right quantity.')

        if flux['isAblating'] and not meanAblating:
            findings.append(
                f'The peak flux sustains ablation and the mean flux does not, so recession occurs '
                f'only around the peak. A single mean-flux calculation reports zero and misses it '
                f'entirely; a time-resolved trajectory is needed to size this case properly.')

        return {'recessionRate':      rate,
                'recessionDepth':     depth,
                'peakFluxEstimate':   peakDepth,
                'meanFlux':           meanFlux,
                'meanSurfaceTemperature': meanSurface,
                'meanIsAblating':     bool(meanAblating),
                'heatLoad':           self.heatLoad,
                'findings':           findings}

    # -------------------------------------------------------------------------------------------- #

    def sizeThickness(self) -> dict:

        '''

        Total thickness: the material lost to recession plus the insulating layer that keeps the
        backface within limits.

        The requirement is almost never on the surface, which is allowed to reach thousands of
        kelvin. It is on the structure behind, and the remaining virgin material is what protects
        it.

        '''

        self._validateInputs()

        recession = self.calculateRecession()
        flux      = self.calculateNetHeatFlux()

        # the insulating requirement, from transient conduction into the remaining virgin material.
        # The thermal wave must not reach the backface with enough amplitude to exceed its limit.
        diffusivity = thermalDiffusivity(self.virginConductivity, self.density, self.specificHeat)
        penetration = thermalPenetrationDepth(diffusivity, self.pulseDuration)

        allowedRise = self.backfaceLimit - self.initialTemperature

        if allowedRise <= 0.0:
            raise AblationError(
                f'The backface limit {self.backfaceLimit:.1f} K is at or below the initial '
                f'temperature {self.initialTemperature:.1f} K, so there is no allowable rise.',
                context = createErrorContext(component = 'AblativeTPS'))

        # semi-infinite solid with a step surface temperature: the depth at which the rise is the
        # allowable fraction of the surface rise, from the complementary error function solution
        # the driving surface temperature is the actual one from the energy balance
        surfaceRise = flux['surfaceTemperature'] - self.initialTemperature
        ratio = np.clip(allowedRise / surfaceRise, 1.0e-6, 0.999)

        # erfc^-1 approximated by inverting the series; adequate for a sizing estimate
        from math import erfc
        etaValues = np.linspace(0.0, 4.0, 4001)
        erfcValues = np.array([erfc(value) for value in etaValues])
        eta = float(np.interp(ratio, erfcValues[::-1], etaValues[::-1]))

        insulating = 2.0 * eta * np.sqrt(diffusivity * self.pulseDuration)

        total = (recession['recessionDepth'] + insulating) * self.thicknessMargin

        recessionFraction = recession['recessionDepth'] / max(total, 1.0e-12)
        limitedBy = ('recession' if recessionFraction > RECESSION_LIMITED_FRACTION
                     else 'insulation')

        self.findings = list(recession['findings'])

        self.findings.append(
            f'Total {total * 1000.0:.2f} mm: {recession["recessionDepth"] * 1000.0:.2f} mm lost to '
            f'recession, {insulating * 1000.0:.2f} mm of insulation, and a '
            f'{self.thicknessMargin:.2f} margin.')

        self.findings.append(
            f'The design is {limitedBy} limited, with recession '
            f'{recessionFraction * 100.0:.0f} % of the total. '
            + ('A higher heat of ablation is the lever.' if limitedBy == 'recession'
               else 'A lower virgin conductivity is the lever, not a higher heat of ablation.'))

        arealMass = total * self.density
        self.findings.append(
            f'Areal mass {arealMass:.2f} kg/m^2. Low density materials win here even when their '
            f'heat of ablation is comparable, which is the entire argument for PICA.')

        return {'recessionDepth':    recession['recessionDepth'],
                'insulatingDepth':   insulating,
                'totalThickness':    total,
                'margin':            self.thicknessMargin,
                'arealMass':         arealMass,
                'limitedBy':         limitedBy,
                'recessionFraction': recessionFraction,
                'penetrationDepth':  penetration,
                'diffusivity':       diffusivity,
                'findings':          self.findings}

    # -------------------------------------------------------------------------------------------- #

    def compareMaterials(self) -> dict:

        '''

        Every material in the table against this heat pulse, on thickness and areal mass.

        Areal mass rather than thickness is the comparison that matters, and it frequently reorders
        the ranking: a thick low density material beats a thin dense one.

        '''

        self._validateInputs()

        saved = self.material
        results = {}

        try:
            for name in ABLATIVE_MATERIALS:

                fresh = AblativeTPS()
                fresh.setInputs({'material':           name,
                                 'peakHeatFlux':       self.peakHeatFlux,
                                 'heatLoad':           self.heatLoad,
                                 'pulseDuration':      self.pulseDuration,
                                 'backfaceLimit':      self.backfaceLimit,
                                 'initialTemperature': self.initialTemperature,
                                 'blowingBlockage':    self.blowingBlockage,
                                 'thicknessMargin':    self.thicknessMargin})

                sizing = fresh.sizeThickness()
                results[name] = {'thickness': sizing['totalThickness'],
                                 'arealMass': sizing['arealMass'],
                                 'limitedBy': sizing['limitedBy'],
                                 'note':      ABLATIVE_MATERIALS[name]['note']}
        finally:
            self.material = saved

        byMass      = min(results, key = lambda name: results[name]['arealMass'])
        byThickness = min(results, key = lambda name: results[name]['thickness'])

        findings = []
        if byMass != byThickness:
            findings.append(
                f'\'{byMass}\' is lightest and \'{byThickness}\' is thinnest. Areal mass is the '
                f'comparison that matters and it reorders the ranking, because a thick low density '
                f'material beats a thin dense one.')

        return {'materials':      results,
                'lightest':       byMass,
                'thinnest':       byThickness,
                'findings':       findings}

    # -------------------------------------------------------------------------------------------- #

    def generateReport(self, outputDir: str = None) -> str:

        '''
        A readable summary of the shield.
        '''

        sizing = self.sizeThickness()

        lines = []
        lines.append('=' * 96)
        lines.append(f'  ABLATIVE TPS: {self.material}, '
                     f'{self.peakHeatFlux / 1.0e6:.2f} MW/m^2 peak, '
                     f'{self.pulseDuration:.0f} s')
        lines.append('=' * 96)
        lines.append('')

        rows = [['Recession',        f'{sizing["recessionDepth"] * 1000.0:.2f}', 'mm'],
                ['Insulation',       f'{sizing["insulatingDepth"] * 1000.0:.2f}', 'mm'],
                ['Margin',           f'{sizing["margin"]:.2f}', '-'],
                ['Total thickness',  f'{sizing["totalThickness"] * 1000.0:.2f}', 'mm'],
                ['Areal mass',       f'{sizing["arealMass"]:.2f}', 'kg/m^2'],
                ['Limited by',       sizing['limitedBy'], '-']]
        lines.append(formatReportTable(rows, ['Quantity', 'Value', 'Unit'], title = 'Sizing'))

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
            with open(os.path.join(outputDir, 'ablativeTPS.txt'), 'w',
                      encoding = 'utf-8') as handle:
                handle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''
        Check the environment and material are physical.
        '''

        context = createErrorContext(component = 'AblativeTPS')

        if not np.isfinite(self.peakHeatFlux) or self.peakHeatFlux <= 0.0:
            raise InvalidInputError('Peak heat flux must be positive.', context = context)

        if not np.isfinite(self.pulseDuration) or self.pulseDuration <= 0.0:
            raise InvalidInputError('Pulse duration must be positive.', context = context)

        if not 0.0 < self.blowingBlockage <= 1.0:
            raise InvalidInputError(
                f'Blowing blockage must be in (0, 1], got {self.blowingBlockage}.',
                context = context)

        if self.thicknessMargin < 1.0:
            raise InvalidInputError(
                f'Thickness margin must be at least 1.0, got {self.thicknessMargin}.',
                context = context)

        meanFlux = self.heatLoad / self.pulseDuration
        if meanFlux > self.peakHeatFlux * 1.001:
            raise AblationError(
                f'The mean flux from the heat load is {meanFlux / 1.0e6:.3f} MW/m^2, above the '
                f'stated peak of {self.peakHeatFlux / 1.0e6:.3f} MW/m^2. One of the two is wrong.',
                context = context)
