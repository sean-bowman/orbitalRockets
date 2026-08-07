
# -- MaterialDatabase Class Definition -- #

'''

Property query across alloy, condition, temperature, orientation and statistical basis, with the
source of every number carried through to the report.

The class exists for three reasons that a raw dictionary lookup does not cover.

    temperature       Properties are stored as ratio-to-room-temperature curves and interpolated
                      here. Outside the validated range the query CLAMPS and records the fact
                      rather than extrapolating, because a linearly extrapolated Inconel yield at
                      1400 K is a plausible-looking number with no physical content.

    basis             A typical value and an A-basis allowable are different quantities and mixing
                      them is the most common materials mistake there is. The basis is an explicit
                      input, an absent allowable returns None rather than falling back to typical,
                      and generateReport prints the basis class beside every number.

    provenance        Every property resolves to a SOURCES record carrying basisClass, so an
                      author estimate can never be mistaken for an MMPDS tolerance limit.

A note on the interface. Eight other classes in this domain need a property lookup, and none of them
should be constructing a MaterialDatabase inside their own setInputs to get one. The module-level
queryMaterial() is the callable path and the class wraps it for reporting. This is a deliberate
departure from the one-class-per-file convention used elsewhere in the repository, and it is the only
one in this domain.

See Also:
---------
Allowables        : Turns sample data into a basis value. Use it when this database has no allowable.
MaterialSelector  : Screens and ranks across the whole database
CorrosionAssessment : Consumes anodicIndex, chemistry and the sccThreshold block
materialData      : The data itself

Theory: docs/MaterialsOverview.md, docs/AllowablesAndStatistics.md

Author: Sean Bowman
Date:   08/06/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from utils import (applyInputs, formatReportTable,
                       InvalidInputError, CompatibilityError, createErrorContext)
    from materialData import MATERIAL_DATABASE, MATERIAL_ALIASES, SOURCES
except ImportError:
    from .utils import (applyInputs, formatReportTable,
                        InvalidInputError, CompatibilityError, createErrorContext)
    from .materialData import MATERIAL_DATABASE, MATERIAL_ALIASES, SOURCES

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Which ratio curve corrects which property. A property not listed here is returned at its room
# temperature value with no correction, and that is recorded in the notes rather than assumed to be
# harmless.

CURVE_FOR_PROPERTY = {
    'yieldStrength':       'yieldRatio',
    'ultimateStrength':    'ultimateRatio',
    'elasticModulus':      'modulusRatio',
    'shearModulus':        'modulusRatio',
    'bearingUltimate':     'ultimateRatio',
    'transverseStrength':  'ultimateRatio',
    'compressiveStrength': 'ultimateRatio',
    'interlaminarShear':   'ultimateRatio',
    'thermalConductivity': 'conductivityRatio',
    'thermalExpansion':    'expansionRatio',
    'planeStrainToughness': 'toughnessRatio'
}

# Statistical basis, worst to best for a designer. 'S' is a specification guaranteed minimum: every
# lot meets it, but it is not a computed tolerance limit and it is usually more conservative than a
# real A-basis would be.

BASIS_ORDER = ('typical', 'S', 'B', 'A')

BASIS_DESCRIPTION = {
    'typical': 'Handbook central value. NOT a design allowable.',
    'S':       'Specification guaranteed minimum. Not a statistical basis.',
    'B':       '90 percent of the population exceeds this, at 95 percent confidence.',
    'A':       '99 percent of the population exceeds this, at 95 percent confidence.'
}

# Grain directions. Short transverse is the one that fails, and on a thick 7xxx product it is where
# stress corrosion cracking lives.

ORIENTATIONS = ('L', 'LT', 'ST')

# ------------------------------------------------------------------------------------------------ #
# -- Module Functions -- #
# ------------------------------------------------------------------------------------------------ #

def resolveMaterialKey(material: str) -> str:

    '''

    Normalise a material name to its canonical database key.

    Collapses internal whitespace and upper cases, matching common/materials.py so its nine keys pass
    through unchanged, then resolves through MATERIAL_ALIASES.

    '''

    if not isinstance(material, str):
        raise InvalidInputError(
            message       = 'Material name must be a string.',
            parameterName = 'material', value = material,
            validRange    = 'A key or alias in MATERIAL_DATABASE'
        )

    key = ' '.join(material.strip().upper().split())

    if key in MATERIAL_DATABASE:
        return key

    if key in MATERIAL_ALIASES:
        return MATERIAL_ALIASES[key]

    raise InvalidInputError(
        message       = f'No entry for material \'{material}\'.',
        parameterName = 'material', value = material,
        validRange    = str(sorted(MATERIAL_DATABASE.keys()))
    )

def _selectCurveBlock(conditionRecord: dict, temperature: float) -> dict:

    '''

    Choose between the hot and cryogenic curve blocks.

    Nickel alloys carry both, because their published elevated temperature data starts at room
    temperature and their cryogenic data is a separate source with a separate grid. Everything else
    carries a single block spanning the whole range.

    '''

    hotBlock  = conditionRecord.get('temperatureCurves')
    cryoBlock = conditionRecord.get('cryogenicCurves')

    if cryoBlock is None:
        return hotBlock

    if hotBlock is None:
        return cryoBlock

    # Below the hot block's lower bound the cryogenic block is the applicable one.
    hotLower = hotBlock['validRange'][0]

    return cryoBlock if temperature < hotLower else hotBlock

def _interpolateRatio(curveBlock: dict, curveName: str, temperature: float) -> tuple:

    '''

    Interpolate a ratio curve, clamping outside the validated range.

    Returns (ratio, wasClamped). Clamping rather than extrapolating is deliberate: an extrapolated
    strength ratio is a number with no data behind it and it will be used as though it had.

    '''

    if curveBlock is None or curveName not in curveBlock:
        return 1.0, False

    grid   = curveBlock['temperature']
    ratios = curveBlock[curveName]

    lower, upper = curveBlock.get('validRange', (grid[0], grid[-1]))

    clamped   = temperature < lower or temperature > upper
    evaluated = min(max(temperature, grid[0]), grid[-1])

    return float(np.interp(evaluated, grid, ratios)), clamped

def queryMaterial(material: str, condition: str = None, temperature: float = 293.15,
                  orientation: str = 'L', basis: str = 'typical') -> dict:

    '''

    The workhorse lookup. Returns a flat property dictionary, temperature corrected.

    Deliberately a module-level function rather than a method, so the other classes in this domain can
    call it in a loop without constructing an object. The returned dictionary has the same shape as
    common/materials.py's materialProperties(), plus the extra fields this database carries.

    Arguments:
        material     Alloy key or alias, case and whitespace insensitive
        condition    Condition key. Defaults to the first condition defined for the alloy.
        temperature  [K]
        orientation  'L', 'LT' or 'ST'. Only affects allowables.
        basis        'typical', 'S', 'B' or 'A'

    Strength and modulus keys carry the requested basis. If the basis has no value for this alloy,
    condition and orientation, the key is present and set to None, and 'basisAvailable' is False. It
    does NOT silently fall back to typical, because that is how a typical value ends up in a stress
    report labelled as an allowable.

    '''

    key         = resolveMaterialKey(material)
    alloyRecord = MATERIAL_DATABASE[key]

    if basis not in BASIS_ORDER:
        raise InvalidInputError(
            message       = f'Unknown statistical basis \'{basis}\'.',
            parameterName = 'basis', value = basis, validRange = str(BASIS_ORDER)
        )

    if orientation not in ORIENTATIONS:
        raise InvalidInputError(
            message       = f'Unknown grain orientation \'{orientation}\'.',
            parameterName = 'orientation', value = orientation, validRange = str(ORIENTATIONS)
        )

    conditionKey = condition.strip().lower() if condition is not None \
                   else next(iter(alloyRecord['conditions']))

    if conditionKey not in alloyRecord['conditions']:
        raise InvalidInputError(
            message       = f'Material \'{key}\' has no condition \'{condition}\'.',
            parameterName = 'condition', value = condition,
            validRange    = str(sorted(alloyRecord['conditions'].keys()))
        )

    conditionRecord = alloyRecord['conditions'][conditionKey]
    curveBlock      = _selectCurveBlock(conditionRecord, temperature)

    properties   = {}
    extrapolated = []
    notes        = []

    # -- Alloy level, temperature independent -- #

    for name in ('commonName', 'family', 'uns', 'crystalStructure', 'density', 'poissonRatio',
                 'anodicIndex', 'relativeCost', 'costBasisDate', 'meltingRange', 'betaTransus',
                 'glassTransition', 'specifications', 'leadTimeWeeks', 'chemistry',
                 'incompatible', 'compatible', 'notes'):
        if name in alloyRecord:
            properties[name] = alloyRecord[name]

    properties['material']    = key
    properties['condition']   = conditionKey
    properties['description'] = conditionRecord.get('description', '')
    properties['forms']       = conditionRecord.get('forms', [])
    properties['temperature'] = temperature
    properties['orientation'] = orientation
    properties['basis']       = basis

    # -- Typical mechanical properties, temperature corrected -- #

    for name, value in conditionRecord.get('typical', {}).items():
        curveName = CURVE_FOR_PROPERTY.get(name)
        if curveName is None:
            properties[name] = value
            continue
        ratio, clamped = _interpolateRatio(curveBlock, curveName, temperature)
        properties[name] = value * ratio
        if clamped:
            extrapolated.append(name)

    # -- Thermal properties, temperature corrected -- #

    for name, value in conditionRecord.get('thermal', {}).items():
        curveName = CURVE_FOR_PROPERTY.get(name)
        if curveName is None:
            properties[name] = value
            continue
        ratio, clamped = _interpolateRatio(curveBlock, curveName, temperature)
        properties[name] = value * ratio
        if clamped:
            extrapolated.append(name)

    # -- Allowables, if the requested basis exists -- #

    properties['basisAvailable'] = False

    if basis != 'typical':
        allowableBlock = conditionRecord.get('allowables', {}).get(basis)
        if allowableBlock is None:
            notes.append(
                f'No {basis}-basis allowable exists in this database for {key} in the {conditionKey} '
                f'condition. The strength values returned are typical values. Establish a basis with '
                f'the Allowables class before using them as design values.')
        else:
            for name in ('yieldStrength', 'ultimateStrength'):
                orientedBlock = allowableBlock.get(name)
                if orientedBlock is None:
                    continue
                value = orientedBlock.get(orientation, orientedBlock.get('L'))
                if value is None:
                    notes.append(
                        f'No {basis}-basis {name} in the {orientation} direction for {key}. On a '
                        f'thick product the short transverse value is the one that governs and its '
                        f'absence is a real gap, not a formality.')
                    properties[name] = None
                    continue
                curveName      = CURVE_FOR_PROPERTY[name]
                ratio, clamped = _interpolateRatio(curveBlock, curveName, temperature)
                properties[name] = value * ratio
                properties['basisAvailable'] = True
                if clamped:
                    extrapolated.append(name)

    # -- Blocks passed through whole -- #

    for blockName in ('fracture', 'fatigue', 'environmental', 'anisotropy', 'sensitization',
                      'quenchFactor', 'stressRupture'):
        if blockName in conditionRecord:
            properties[blockName] = conditionRecord[blockName]

    # -- ASME B31.3 style basic allowable, matching common/materials.py so the two agree -- #

    if properties.get('yieldStrength') is not None and properties.get('ultimateStrength') is not None:
        properties['allowableStress'] = min(2.0 / 3.0 * properties['yieldStrength'],
                                            properties['ultimateStrength'] / 3.5)

    if extrapolated:
        validRange = curveBlock.get('validRange', (np.nan, np.nan)) if curveBlock else (np.nan, np.nan)
        notes.append(
            f'Temperature {temperature:.1f} K is outside the validated range '
            f'{validRange[0]:.0f} to {validRange[1]:.0f} K. These properties were CLAMPED to the '
            f'range endpoint rather than extrapolated: {", ".join(sorted(set(extrapolated)))}. '
            f'Treat them as unvalidated.')

    properties['extrapolated']  = sorted(set(extrapolated))
    properties['databaseNotes'] = notes
    properties['sources']       = conditionRecord.get('sources', {})

    return properties

def getProvenance(material: str, condition: str = None, block: str = 'typical') -> dict:

    '''

    Resolve the source record behind a property block.

    The basisClass field is the one that matters. 'estimate' means the number is not traceable and
    must not appear in a stress report.

    '''

    key             = resolveMaterialKey(material)
    alloyRecord     = MATERIAL_DATABASE[key]
    conditionKey    = condition.strip().lower() if condition is not None \
                      else next(iter(alloyRecord['conditions']))
    conditionRecord = alloyRecord['conditions'][conditionKey]

    sourceKey = conditionRecord.get('sources', {}).get(block)

    if sourceKey is None:
        return {'document': 'unknown', 'basisClass': 'estimate', 'confidence': 'none',
                'note': f'No source recorded for the \'{block}\' block of {key} {conditionKey}.'}

    record = dict(SOURCES[sourceKey])
    record['sourceKey'] = sourceKey

    return record

def listMaterials(family: str = None, form: str = None,
                  minimumTemperature: float = None, maximumTemperature: float = None) -> list:

    '''

    List database keys matching a filter. Used by MaterialSelector to build its candidate set.

    '''

    matches = []

    for key, alloyRecord in MATERIAL_DATABASE.items():

        if family is not None and family.strip().lower() not in alloyRecord['family'].lower():
            continue

        for conditionKey, conditionRecord in alloyRecord['conditions'].items():

            if form is not None and form.strip().lower() not in conditionRecord.get('forms', []):
                continue

            curveBlock = conditionRecord.get('cryogenicCurves') or conditionRecord.get('temperatureCurves')
            if curveBlock is not None:
                lower, upper = curveBlock.get('validRange', (0.0, 1.0e4))
                hotBlock     = conditionRecord.get('temperatureCurves')
                if hotBlock is not None:
                    upper = max(upper, hotBlock.get('validRange', (0.0, 0.0))[1])
                if minimumTemperature is not None and minimumTemperature < lower:
                    continue
                if maximumTemperature is not None and maximumTemperature > upper:
                    continue

            matches.append((key, conditionKey))

    return matches

# ------------------------------------------------------------------------------------------------ #

class MaterialDatabase:

    '''

    Object wrapper around queryMaterial, adding a datasheet report and a provenance trail.

    Primary Input Properties:
    -------------------------
    material : str
        Alloy key or alias. Case and whitespace insensitive.
    condition : str
        Condition key. Defaults to the alloy's first defined condition.
    temperature : float
        Service temperature [K]
    orientation : str
        'L', 'LT' or 'ST'. Short transverse is the one that fails.
    basis : str
        'typical', 'S', 'B' or 'A'

    Key Output Properties:
    ----------------------
    properties : dict
        Flat, temperature corrected property dictionary
    extrapolated : list
        Properties clamped because the query temperature was outside the validated range
    databaseNotes : list
        Warnings that should be read, not scrolled past

    Public Methods:
    ---------------
    setInputs(inputs)             Load a configuration dictionary
    getProperties()               The temperature corrected property dictionary
    getAllowable(property)        A single allowable at the configured basis and orientation
    getTemperatureCurve(prop, T)  A property evaluated over an array of temperatures
    getFractureData()             Toughness, Paris constants, threshold
    getFatigueData()              Basquin constants and endurance limit
    checkCompatibility(fluid)     Raises CompatibilityError on a prohibited combination
    compare(materials, props)     Side by side across several alloys
    generateReport(outputDir)     Datasheet with a source column

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Query Definition -- #

        self.material      = '316L'      # [case insensitive string], key or alias
        self.condition     = None        # [case insensitive string], None takes the first defined
        self.temperature   = 293.15      # [K]
        self.orientation   = 'L'         # [-], 'L', 'LT' or 'ST'
        self.basis         = 'typical'   # [-], 'typical', 'S', 'B' or 'A'
        self.form          = None        # [case insensitive string], mill product form

        # -- Results -- #

        self.properties    = {}          # [dict], flat and temperature corrected
        self.extrapolated  = []          # [list of str]
        self.databaseNotes = []          # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: material.

        '''

        requiredParams = {
            'material': 'Material name not provided.'
        }

        optionalParams = ['condition', 'temperature', 'orientation', 'basis', 'form']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self._validateInputs()

    def getProperties(self) -> dict:

        '''

        Query the database and store the result.

        '''

        self.properties    = queryMaterial(self.material, self.condition, self.temperature,
                                           self.orientation, self.basis)
        self.extrapolated  = self.properties['extrapolated']
        self.databaseNotes = list(self.properties['databaseNotes'])

        return self.properties

    def getAllowable(self, propertyName: str = 'ultimateStrength') -> float:

        '''

        Return a single allowable at the configured basis, orientation and temperature.

        Returns None when the basis does not exist for this alloy and condition, rather than falling
        back to a typical value. A None here means the allowable has to be established, and the
        Allowables class is what establishes it.

        '''

        if not self.properties:
            self.getProperties()

        if self.basis == 'typical':
            self.databaseNotes.append(
                f'getAllowable called with basis \'typical\'. A typical value is not an allowable. '
                f'Set basis to \'A\', \'B\' or \'S\', or establish one with the Allowables class.')

        return self.properties.get(propertyName)

    def getTemperatureCurve(self, propertyName: str, temperatures) -> np.ndarray:

        '''

        Evaluate a property across an array of temperatures.

        Each point goes through the same clamping logic as a single query, so a curve that runs off
        the end of the validated range flattens rather than diverging, and the fact is recorded.

        '''

        temperatures = np.atleast_1d(np.asarray(temperatures, dtype = float))
        values       = np.zeros_like(temperatures)

        for index, temperature in enumerate(temperatures):
            result = queryMaterial(self.material, self.condition, float(temperature),
                                   self.orientation, self.basis)
            value  = result.get(propertyName)
            values[index] = np.nan if value is None else value
            if result['extrapolated'] and propertyName in result['extrapolated']:
                if 'clamped' not in ' '.join(self.databaseNotes):
                    self.databaseNotes.append(
                        f'{propertyName} was clamped at one or more points in the requested '
                        f'temperature range. The curve is flat there, not physical.')

        return values

    def getFractureData(self) -> dict:

        '''

        Plane strain toughness, Paris constants and threshold. Feeds DamageTolerance.

        '''

        if not self.properties:
            self.getProperties()

        data = self.properties.get('fracture')

        if data is None:
            self.databaseNotes.append(
                f'No fracture data in this database for {self.material} in the '
                f'{self.properties["condition"]} condition. A fracture critical part cannot be '
                f'analysed without it and the data has to be sourced.')
            return {}

        # The toughness is stored at room temperature and corrected by the same curve mechanism.
        corrected = dict(data)
        toughness = data.get('planeStrainToughness', {})
        record    = MATERIAL_DATABASE[resolveMaterialKey(self.material)]
        block     = _selectCurveBlock(record['conditions'][self.properties['condition']],
                                      self.temperature)
        ratio, _  = _interpolateRatio(block, 'toughnessRatio', self.temperature)

        corrected['planeStrainToughness'] = {key: value * ratio for key, value in toughness.items()}
        corrected['temperature']          = self.temperature

        return corrected

    def getFatigueData(self) -> dict:

        '''

        Basquin constants, endurance stress and the surface condition they were measured on.

        '''

        if not self.properties:
            self.getProperties()

        data = self.properties.get('fatigue')

        if data is None:
            self.databaseNotes.append(
                f'No fatigue data for {self.material} in the {self.properties["condition"]} '
                f'condition.')
            return {}

        return dict(data)

    def checkCompatibility(self, fluid: str) -> list:

        '''

        Screen a material and fluid combination.

        Raises rather than warns on a hard prohibition, matching Seal.checkCompatibility in the
        fluidSystems library. Titanium in oxygen is not a caution.

        '''

        if not self.properties:
            self.getProperties()

        target       = ' '.join(fluid.strip().upper().split())
        incompatible = self.properties.get('incompatible', [])
        compatible   = self.properties.get('compatible', [])

        for entry in incompatible:
            if target == entry or target in entry:
                raise CompatibilityError(
                    message  = f'{self.properties["commonName"]} is prohibited in {fluid} service. '
                               f'Database entry: \'{entry}\'.',
                    material = self.properties['commonName'],
                    fluid    = fluid
                )

        if target in compatible:
            return [f'{self.properties["commonName"]} is compatible with {fluid}.']

        note = (f'{fluid} does not appear in either the compatible or the incompatible list for '
                f'{self.properties["commonName"]}. Absence of a prohibition is not evidence of '
                f'compatibility. Check the material specification before relying on it.')
        self.databaseNotes.append(note)

        return [note]

    def compare(self, materials: list, propertyNames: list = None) -> dict:

        '''

        Side by side comparison across several alloys at the configured temperature and basis.

        Accepts either a bare alloy name or an (alloy, condition) tuple.

        '''

        if propertyNames is None:
            propertyNames = ['density', 'yieldStrength', 'ultimateStrength', 'elasticModulus',
                             'thermalConductivity', 'relativeCost']

        comparison = {}

        for entry in materials:
            name, condition = entry if isinstance(entry, (tuple, list)) else (entry, None)
            result = queryMaterial(name, condition, self.temperature, self.orientation, self.basis)
            label  = f'{result["material"]} {result["condition"]}'
            comparison[label] = {key: result.get(key) for key in propertyNames}

        return comparison

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a material datasheet with the statistical basis and the source beside every number.

        '''

        if not self.properties:
            self.getProperties()

        data    = self.properties
        rows    = []
        sources = data.get('sources', {})

        def sourceLabel(block: str) -> str:
            key = sources.get(block)
            return SOURCES[key]['basisClass'] if key in SOURCES else 'unknown'

        rows.append(['Material',        f'{data["commonName"]}'])
        rows.append(['Condition',       f'{data["condition"]} -- {data["description"]}'])
        rows.append(['Family',          f'{data["family"]}'])
        rows.append(['UNS',             f'{data["uns"] if data.get("uns") else "n/a"}'])
        rows.append(['Crystal structure', f'{data["crystalStructure"]}'])
        rows.append(['Temperature',     f'{data["temperature"]:.1f} K'])
        rows.append(['Orientation',     f'{data["orientation"]}'])
        rows.append(['Basis',           f'{data["basis"]} -- {BASIS_DESCRIPTION[data["basis"]]}'])
        rows.append(['Density',         f'{data["density"]:.1f} kg/m^3'])
        rows.append(['Poisson ratio',   f'{data["poissonRatio"]:.3f}'])

        yieldStrength = data.get('yieldStrength')
        ultimate      = data.get('ultimateStrength')

        rows.append(['Yield strength',
                     f'{yieldStrength / 1.0e6:.1f} MPa [{sourceLabel("typical")}]'
                     if yieldStrength is not None else 'no value at this basis and orientation'])
        rows.append(['Ultimate strength',
                     f'{ultimate / 1.0e6:.1f} MPa [{sourceLabel("typical")}]'
                     if ultimate is not None else 'no value at this basis and orientation'])

        if data.get('elasticModulus') is not None:
            rows.append(['Elastic modulus', f'{data["elasticModulus"] / 1.0e9:.1f} GPa'])
        if data.get('allowableStress') is not None:
            rows.append(['B31.3 allowable', f'{data["allowableStress"] / 1.0e6:.1f} MPa'])
        if data.get('thermalConductivity') is not None:
            rows.append(['Thermal conductivity', f'{data["thermalConductivity"]:.1f} W/m-K'])
        if data.get('thermalExpansion') is not None:
            rows.append(['Thermal expansion', f'{data["thermalExpansion"] * 1.0e6:.2f} 1e-6/K'])

        if 'fracture' in data:
            toughness = self.getFractureData().get('planeStrainToughness', {})
            if toughness:
                worst = min(toughness.values())
                rows.append(['Plane strain toughness',
                             f'{worst / 1.0e6:.1f} MPa-sqrt(m) [{sourceLabel("fracture")}]'])

        if 'environmental' in data:
            environmental = data['environmental']
            if environmental.get('pren') is not None:
                rows.append(['PREN', f'{environmental["pren"]:.1f}'])
            if environmental.get('hydrogenRatio') is not None:
                rows.append(['H2 notched ratio', f'{environmental["hydrogenRatio"]:.2f}'])
            rating = environmental.get('sccRating', {}).get(data['orientation'])
            if rating is not None:
                rows.append(['SCC resistance', f'{rating} ({data["orientation"]})'])

        rows.append(['Relative cost', f'{data["relativeCost"]:.1f}x 316L bar, {data["costBasisDate"]}'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'MATERIAL DATASHEET')

        if data.get('notes'):
            report += f'\n\nMATERIAL NOTES\n{"-" * 60}\n{data["notes"]}\n'

        if data.get('incompatible'):
            report += f'\nPROHIBITED: {", ".join(data["incompatible"])}\n'

        estimated = [block for block in sources if SOURCES.get(sources[block], {}).get('basisClass')
                     == 'estimate']
        if estimated:
            report += (f'\nCAUTION: the following property blocks are author estimates and are NOT '
                       f'traceable: {", ".join(sorted(estimated))}. Preliminary trade use only.\n')

        for note in self.databaseNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'materialDatasheet.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        resolveMaterialKey(self.material)

        if self.basis not in BASIS_ORDER:
            raise InvalidInputError(
                message       = f'Unknown statistical basis \'{self.basis}\'.',
                parameterName = 'basis', value = self.basis, validRange = str(BASIS_ORDER)
            )

        if self.orientation not in ORIENTATIONS:
            raise InvalidInputError(
                message       = f'Unknown grain orientation \'{self.orientation}\'.',
                parameterName = 'orientation', value = self.orientation,
                validRange    = str(ORIENTATIONS)
            )

        if not np.isfinite(self.temperature) or self.temperature <= 0.0:
            raise InvalidInputError(
                message       = 'Temperature must be a positive absolute temperature.',
                parameterName = 'temperature', value = self.temperature,
                validRange    = 'Greater than 0 K'
            )
