
# -- Allowables Class Definition -- #

'''

A-basis and B-basis design allowables from sample data, and the knockdown chain from a raw tolerance
limit to a number that can go in a stress report.

The distinction this class exists to enforce is the one that gets missed most often. A handbook
value is the approximate mean of a population. A design allowable is a lower tolerance limit on that
population at a stated confidence. They are different quantities and the gap between them is not
small: for a typical 4 percent coefficient of variation and a sample of thirty, the A-basis sits
12 percent below the typical value.

    A-basis    99 percent of the population exceeds this value, at 95 percent confidence.
               Required where failure of a single element causes loss of structural integrity.

    B-basis    90 percent of the population exceeds this value, at 95 percent confidence.
               Permitted where the load path is redundant.

    S-basis    A specification guaranteed minimum. Not a statistical basis at all, and usually more
               conservative than a computed A-basis would be.

The whole story is in the k-factor, and the k-factor is a function of sample size:

    k_B = 3.04 at n = 5,  1.93 at n = 20,  1.53 at n = 100,  -> 1.282 as n -> infinity
    k_A = 5.74 at n = 5,  3.30 at n = 20,  2.68 at n = 100,  -> 2.326 as n -> infinity

Three independent routes to that factor are implemented, not because any one of them is in doubt but
because a cross-check between them catches a coding error that a single implementation cannot. They
agree to within 2 percent at n = 10 and better than 1 percent above n = 20.

THIS CLASS CAN DO REAL HARM. An A-basis computed from five specimens is a number with the authority
of a statistical allowable and the content of a guess. calculateBasisValue raises below n = 10 and
warns loudly below n = 100 or fewer than 10 lots, and those guards should not be removed.

See Also:
---------
MaterialDatabase : Where a published allowable already exists, use it rather than computing one
DamageTolerance  : Consumes the design value as the stress that drives the critical flaw size
HeatTreatment    : Supplies process knockdowns to the chain

Theory: docs/AllowablesAndStatistics.md

Author: Sean Bowman
Date:   08/07/2026

'''

# ------------------------------------------------------------------------------------------------ #
# -- Imports -- #
# ------------------------------------------------------------------------------------------------ #

import numpy as np

try:
    from scipy import stats as scipyStats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from utils import (applyInputs, formatReportTable, secantSolve,
                       InvalidInputError, createErrorContext)
    from MaterialDatabase import queryMaterial, resolveMaterialKey
except ImportError:
    from .utils import (applyInputs, formatReportTable, secantSolve,
                        InvalidInputError, createErrorContext)
    from .MaterialDatabase import queryMaterial, resolveMaterialKey

# ------------------------------------------------------------------------------------------------ #
# -- Module Constants -- #
# ------------------------------------------------------------------------------------------------ #

# Standard normal quantiles for the exceedance probabilities that define the two bases, and for the
# 95 percent confidence level. These are the only three numbers the whole method rests on.

Z_QUANTILE_A     = 2.3263479     # [-], one-sided 99 percent exceedance
Z_QUANTILE_B     = 1.2815516     # [-], one-sided 90 percent exceedance
Z_CONFIDENCE_95  = 1.6448536     # [-], 95 percent confidence

BASIS_QUANTILE = {'A': Z_QUANTILE_A, 'B': Z_QUANTILE_B}

BASIS_EXCEEDANCE = {'A': 0.99, 'B': 0.90}

# Minimum sample sizes. The hard floor is where the tolerance factor becomes so large that the
# resulting allowable is driven by the sample size rather than by the material, and reporting it as
# a material property is misleading. The advisory floor is MMPDS practice for a direct computation.

MINIMUM_SAMPLE_SIZE   = 10       # [-], below this calculateBasisValue raises
ADVISORY_SAMPLE_SIZE  = 100      # [-], below this it warns
ADVISORY_BATCH_COUNT  = 10       # [-], MMPDS wants at least ten lots for a direct basis value

# Process knockdowns applied on top of a basis value. Each is a multiplier, and each is a real,
# separately justified reduction rather than a blanket margin. They compound multiplicatively, which
# is why a welded casting made from a slow-quenched forging ends up with very little left.
#
# The casting factors are the NASA-STD-5001 / 6016 ladder and they are the strongest argument for
# paying for a qualified casting process: the difference between 1.0 and 2.0 is the whole allowable.

STANDARD_KNOCKDOWNS = {
    'weld, aluminium as-welded':   {'factor': 0.55, 'basis': 'HAZ loses temper, no recovery without solution treat and age'},
    'weld, aluminium post-weld HT': {'factor': 0.90, 'basis': 'Solution treated and aged after welding'},
    'weld, austenitic stainless':  {'factor': 1.00, 'basis': 'Solid solution alloy, no strength to lose'},
    'weld, electron beam':         {'factor': 0.95, 'basis': 'Narrow HAZ, minimal heat input'},
    'weld, friction stir':         {'factor': 0.80, 'basis': 'Solid state, no melting, but the nugget is recrystallised'},
    'weld, nickel PH as-welded':   {'factor': 0.55, 'basis': 'Precipitation hardened alloy welded in the aged condition'},
    'casting, factor 1.0':         {'factor': 1.00, 'basis': 'Qualified process, 100 percent volumetric NDE, three sample lots'},
    'casting, factor 1.33':        {'factor': 0.752, 'basis': 'Partial NDE or incomplete process qualification'},
    'casting, factor 2.0':         {'factor': 0.500, 'basis': 'Default where no casting process qualification exists'},
    'additive, Z direction':       {'factor': 0.90, 'basis': 'Build direction normal to the load, HIP applied'},
    'additive, as-built surface':  {'factor': 0.75, 'basis': 'Fatigue allowable on an unmachined LPBF surface'},
    'quench, slow section':        {'factor': 0.85, 'basis': 'Thick section, incomplete solution retention'},
    'thickness, heavy section':    {'factor': 0.95, 'basis': 'Thick product reduction relative to the tested thickness'},
    'moisture, composite hot wet': {'factor': 0.85, 'basis': 'Saturated laminate at elevated temperature'}
}

# Distribution fitting. The default is normal because that is what MMPDS assumes for metallic
# strength data and what the k-factors above are derived for. Weibull is the right model for a
# minimum-of-many-flaws mechanism, which is composites and ceramics rather than metals.

SUPPORTED_DISTRIBUTIONS = ('normal', 'lognormal', 'weibull')

# ------------------------------------------------------------------------------------------------ #
# -- Module Functions -- #
# ------------------------------------------------------------------------------------------------ #

def toleranceFactorExact(sampleSize: int, basis: str = 'B', confidence: float = 0.95) -> float:

    '''

    The exact one-sided normal tolerance factor, from the non-central t distribution.

        k = t'_(n-1, delta)(gamma) / sqrt(n)        delta = z_p * sqrt(n)

    This is the definition rather than an approximation to it. Requires scipy; the caller should
    fall back to the Natrella form if scipy is absent.

    '''

    if not SCIPY_AVAILABLE:
        raise ImportError('toleranceFactorExact needs scipy. Use toleranceFactorNatrella instead.')

    quantile      = BASIS_QUANTILE[basis]
    noncentrality = quantile * np.sqrt(sampleSize)

    return float(scipyStats.nct.ppf(confidence, sampleSize - 1, noncentrality) / np.sqrt(sampleSize))

def toleranceFactorNatrella(sampleSize: int, basis: str = 'B', confidence: float = 0.95) -> float:

    '''

    The Natrella / Owen closed-form approximation to the same factor.

        a = 1 - z_gamma^2 / (2 (n - 1))
        b = z_p^2 - z_gamma^2 / n
        k = [ z_p + sqrt(z_p^2 - a b) ] / a

    Within 2 percent of exact at n = 10 and better than 1 percent above n = 20. Exists so the class
    works without scipy and, more usefully, as an independent check on the exact route.

    '''

    quantile   = BASIS_QUANTILE[basis]
    zConfidence = Z_CONFIDENCE_95 if confidence == 0.95 else \
                  (scipyStats.norm.ppf(confidence) if SCIPY_AVAILABLE else Z_CONFIDENCE_95)

    a = 1.0 - zConfidence ** 2 / (2.0 * (sampleSize - 1))
    b = quantile ** 2 - zConfidence ** 2 / sampleSize

    discriminant = quantile ** 2 - a * b

    if a <= 0.0 or discriminant < 0.0:
        raise InvalidInputError(
            message       = f'The Natrella approximation breaks down at n = {sampleSize}. The sample '
                            f'is too small for a tolerance limit to mean anything.',
            parameterName = 'sampleSize', value = sampleSize,
            validRange    = 'Greater than about 4'
        )

    return float((quantile + np.sqrt(discriminant)) / a)

def toleranceFactorMmpds(sampleSize: int, basis: str = 'B') -> float:

    '''

    The published MMPDS Chapter 9 curve fits, at 95 percent confidence only.

        k_B = 1.282 + exp(0.958 - 0.520 ln n + 3.19 / n)
        k_A = 2.326 + exp(1.340 - 0.522 ln n + 3.87 / n)

    Included for traceability to the document this domain claims to follow. The leading constants
    are the limiting normal quantiles, so the fits converge correctly as n grows.

    '''

    logSize = np.log(sampleSize)

    if basis == 'B':
        return float(1.282 + np.exp(0.958 - 0.520 * logSize + 3.19 / sampleSize))

    return float(2.326 + np.exp(1.340 - 0.522 * logSize + 3.87 / sampleSize))

# ------------------------------------------------------------------------------------------------ #

class Allowables:

    '''

    Compute a design allowable from sample data and carry it through the knockdown chain.

    Primary Input Properties:
    -------------------------
    sampleData : np.ndarray
        Measured values [Pa], one per specimen
    batchIdentifiers : np.ndarray
        Lot or heat identifier per specimen, for the multi-batch variance route
    basis : str
        'A' or 'B'
    distribution : str
        'normal', 'lognormal', 'weibull' or 'auto'
    knockdowns : dict
        Ordered process knockdowns, either a key into STANDARD_KNOCKDOWNS or a bare multiplier

    Key Output Properties:
    ----------------------
    toleranceLimit : float
        The raw basis value [Pa], before any knockdown
    designValue : float
        After every knockdown [Pa]. This is the number that goes in a stress report.
    knockdownChain : list
        The ordered audit trail from typical value to design value

    Public Methods:
    ---------------
    setInputs(inputs)                 Load a configuration dictionary
    fitDistribution()                 Anderson-Darling fit, selects when distribution is 'auto'
    calculateKFactor()                Tolerance factor by the configured method
    calculateBasisValue()             A and B basis from the sample. Raises below n = 10.
    calculateAnovaBasis()             Multi-batch variance components basis
    calculateNonparametricBasis()     Order statistic basis, no distribution assumption
    applyKnockdowns()                 The ordered chain
    selectDesignValue()               A or B from the load path redundancy
    calculateMarginOfSafety(stress, factorOfSafety)
    calculateRequiredSampleSize(targetRatio)
    generateReport(outputDir)         Formatted results table with the full chain

    Author: Sean Bowman

    '''

    # -------------------------------------------------------------------------------------------- #
    # -- Constructor -- #
    # -------------------------------------------------------------------------------------------- #

    def __init__(self):

        # -- Sample Data -- #

        self.sampleData         = np.array([])   # [Pa] or any consistent unit
        self.batchIdentifiers   = np.array([])   # [-], lot or heat ID per specimen
        self.propertyName       = 'ultimateStrength'   # [case sensitive string]

        # -- Basis Selection -- #

        self.basis              = 'B'        # [-], 'A' or 'B'
        self.distribution       = 'normal'   # [-], or 'auto' to select by goodness of fit
        self.kFactorMethod      = 'exact'    # [-], 'exact', 'natrella' or 'mmpds'
        self.confidence         = 0.95       # [-]
        self.loadPath           = 'redundant'  # [-], 'single' or 'redundant'

        # -- Knockdowns -- #

        self.knockdowns         = {}         # [dict], ordered name -> key or multiplier

        # -- Results -- #

        self.sampleSize         = 0          # [-]
        self.batchCount         = 0          # [-]
        self.mean               = np.nan     # [Pa]
        self.standardDeviation  = np.nan     # [Pa]
        self.coefficientOfVariation = np.nan  # [-]
        self.kFactor            = np.nan     # [-]
        self.toleranceLimit     = np.nan     # [Pa], the raw basis value
        self.basisValues        = {}         # [dict], both A and B
        self.designValue        = np.nan     # [Pa], after knockdowns
        self.selectedDistribution = ''       # [case sensitive string]
        self.goodnessOfFit      = {}         # [dict]
        self.knockdownChain     = []         # [list of dict], the audit trail
        self.allowableNotes     = []         # [list of str]

    # -------------------------------------------------------------------------------------------- #
    # -- Public Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def setInputs(self, inputs: dict) -> None:

        '''

        Load a configuration dictionary onto the object.

        Required: sampleData.

        '''

        requiredParams = {
            'sampleData': 'Sample data not provided. An allowable cannot be computed without it.'
        }

        optionalParams = ['batchIdentifiers', 'propertyName', 'basis', 'distribution',
                          'kFactorMethod', 'confidence', 'loadPath', 'knockdowns']

        applyInputs(self, inputs, requiredParams, optionalParams)

        self.sampleData = np.atleast_1d(np.asarray(self.sampleData, dtype = float))
        self.sampleSize = int(self.sampleData.size)

        if np.size(self.batchIdentifiers) > 0:
            self.batchIdentifiers = np.atleast_1d(np.asarray(self.batchIdentifiers))
            self.batchCount       = int(np.unique(self.batchIdentifiers).size)

        self._validateInputs()

    def fitDistribution(self) -> dict:

        '''

        Anderson-Darling goodness of fit across the supported distributions.

        When self.distribution is 'auto' the best fitting model is selected. Otherwise the configured
        model is used regardless, and the statistics are reported so a poor fit is visible.

        A poor normal fit on metallic strength data usually means the sample mixes product forms,
        heats or test temperatures rather than that the metal is non-normal.

        '''

        if not SCIPY_AVAILABLE:
            self.selectedDistribution = 'normal'
            self.allowableNotes.append(
                'scipy is not available, so no distribution fitting was performed and normality was '
                'assumed. For metallic strength data that is usually right, but it is an assumption '
                'here rather than a finding.')
            return {}

        data    = self.sampleData
        results = {}

        # -- Normal -- #
        statistic = scipyStats.anderson(data, dist = 'norm')
        results['normal'] = {'statistic': float(statistic.statistic),
                             'criticalValue5pct': float(statistic.critical_values[2]),
                             'rejected': bool(statistic.statistic > statistic.critical_values[2])}

        # -- Lognormal, by fitting the logarithm -- #
        if np.all(data > 0.0):
            logStatistic = scipyStats.anderson(np.log(data), dist = 'norm')
            results['lognormal'] = {'statistic': float(logStatistic.statistic),
                                    'criticalValue5pct': float(logStatistic.critical_values[2]),
                                    'rejected': bool(logStatistic.statistic >
                                                     logStatistic.critical_values[2])}

        # -- Weibull, two parameter -- #
        if np.all(data > 0.0) and self.sampleSize >= 5:
            shape, location, scale = scipyStats.weibull_min.fit(data, floc = 0.0)
            transformed = (data / scale) ** shape
            weibullStat = scipyStats.anderson(np.log(transformed), dist = 'norm')
            results['weibull'] = {'statistic': float(weibullStat.statistic),
                                  'shape': float(shape), 'scale': float(scale),
                                  'criticalValue5pct': float(weibullStat.critical_values[2]),
                                  'rejected': bool(weibullStat.statistic >
                                                   weibullStat.critical_values[2])}

        self.goodnessOfFit = results

        if self.distribution == 'auto':
            best = min(results, key = lambda name: results[name]['statistic'])
            self.selectedDistribution = best
            self.allowableNotes.append(
                f'Distribution selected automatically as \'{best}\' on the Anderson-Darling '
                f'statistic. Metallic strength data is conventionally treated as normal and a '
                f'selection of anything else is worth understanding before accepting.')
        else:
            self.selectedDistribution = self.distribution
            fit = results.get(self.distribution)
            if fit is not None and fit['rejected']:
                self.allowableNotes.append(
                    f'The {self.distribution} fit is rejected at the 5 percent level '
                    f'(AD statistic {fit["statistic"]:.3f} against a critical value of '
                    f'{fit["criticalValue5pct"]:.3f}). On metallic data this usually means the '
                    f'sample mixes product forms, heats or test temperatures rather than that the '
                    f'material is non-normal. Check the sample before trusting the allowable.')

        return results

    def calculateKFactor(self) -> float:

        '''

        The one-sided tolerance factor for the configured basis, sample size and method.

        '''

        if self.kFactorMethod == 'exact' and not SCIPY_AVAILABLE:
            self.kFactorMethod = 'natrella'
            self.allowableNotes.append(
                'scipy unavailable, so the Natrella approximation was used instead of the exact '
                'non-central t factor. The difference is under 2 percent above n = 10.')

        if self.kFactorMethod == 'exact':
            self.kFactor = toleranceFactorExact(self.sampleSize, self.basis, self.confidence)
        elif self.kFactorMethod == 'natrella':
            self.kFactor = toleranceFactorNatrella(self.sampleSize, self.basis, self.confidence)
        elif self.kFactorMethod == 'mmpds':
            if self.confidence != 0.95:
                raise InvalidInputError(
                    message       = 'The MMPDS curve fits are published at 95 percent confidence only.',
                    parameterName = 'confidence', value = self.confidence, validRange = '0.95'
                )
            self.kFactor = toleranceFactorMmpds(self.sampleSize, self.basis)
        else:
            raise InvalidInputError(
                message       = f'Unknown k-factor method \'{self.kFactorMethod}\'.',
                parameterName = 'kFactorMethod', value = self.kFactorMethod,
                validRange    = "'exact', 'natrella' or 'mmpds'"
            )

        return self.kFactor

    def calculateBasisValue(self) -> dict:

        '''

        A-basis and B-basis tolerance limits from the sample.

            T = mean - k * s

        with s the sample standard deviation on n-1 degrees of freedom.

        Raises below n = 10. At that point the tolerance factor exceeds 2.35 for B-basis and 3.98 for
        A-basis, and the resulting number is a statement about how little data there is rather than
        about the material.

        '''

        if self.sampleSize < MINIMUM_SAMPLE_SIZE:
            raise InvalidInputError(
                message       = f'A tolerance limit from {self.sampleSize} specimens is not '
                                f'defensible. Below n = {MINIMUM_SAMPLE_SIZE} the factor is driven '
                                f'by the sample size rather than the material: k_A is '
                                f'{toleranceFactorNatrella(max(self.sampleSize, 5), "A"):.2f} here '
                                f'against 2.33 at infinite n. Either test more specimens or use a '
                                f'specification minimum and say so.',
                parameterName = 'sampleSize', value = self.sampleSize,
                validRange    = f'At least {MINIMUM_SAMPLE_SIZE}'
            )

        if not self.selectedDistribution:
            self.fitDistribution()
            if not self.selectedDistribution:
                self.selectedDistribution = self.distribution

        self.mean              = float(np.mean(self.sampleData))
        self.standardDeviation = float(np.std(self.sampleData, ddof = 1))
        self.coefficientOfVariation = self.standardDeviation / self.mean

        # -- Both bases, so the cost of requiring A rather than B is visible -- #

        requestedBasis   = self.basis
        self.basisValues = {}

        for basis in ('A', 'B'):
            self.basis = basis
            factor     = self.calculateKFactor()
            if self.selectedDistribution == 'lognormal':
                logMean     = float(np.mean(np.log(self.sampleData)))
                logDeviation = float(np.std(np.log(self.sampleData), ddof = 1))
                value = float(np.exp(logMean - factor * logDeviation))
            else:
                value = self.mean - factor * self.standardDeviation
            self.basisValues[basis] = {'value': value, 'kFactor': factor,
                                       'ratioToMean': value / self.mean}

        self.basis          = requestedBasis
        self.kFactor        = self.basisValues[requestedBasis]['kFactor']
        self.toleranceLimit = self.basisValues[requestedBasis]['value']

        # -- The guards that stop this class doing harm -- #

        if self.sampleSize < ADVISORY_SAMPLE_SIZE:
            self.allowableNotes.append(
                f'{self.sampleSize} specimens is below the {ADVISORY_SAMPLE_SIZE} that MMPDS '
                f'practice expects for a directly computed basis value. The k-factor of '
                f'{self.kFactor:.3f} carries a real penalty for that: at n = '
                f'{ADVISORY_SAMPLE_SIZE} it would be '
                f'{toleranceFactorNatrella(ADVISORY_SAMPLE_SIZE, self.basis):.3f}.')

        if 0 < self.batchCount < ADVISORY_BATCH_COUNT:
            self.allowableNotes.append(
                f'The sample spans {self.batchCount} lots. MMPDS wants at least '
                f'{ADVISORY_BATCH_COUNT}, because between-lot variation is usually larger than '
                f'within-lot variation and a single-lot sample understates the population spread. '
                f'Use calculateAnovaBasis to see the effect.')

        if self.coefficientOfVariation > 0.10:
            self.allowableNotes.append(
                f'The coefficient of variation is {self.coefficientOfVariation * 100.0:.1f} '
                f'percent, which is high for a metallic strength property. Values above about 8 '
                f'percent usually indicate a mixed sample rather than a genuinely variable '
                f'material.')

        return self.basisValues

    def calculateAnovaBasis(self) -> dict:

        '''

        Basis value from a multi-batch sample, separating within-lot and between-lot variance.

            s_total^2 = s_within^2 + s_between^2

        Pooling every specimen as though it came from one population understates the spread whenever
        between-lot variation is real, and it usually is. This route produces the lower and more
        defensible number, and the difference between the two is a direct measure of how much lot to
        lot variation the process carries.

        '''

        if self.batchCount < 2:
            raise InvalidInputError(
                message       = 'The ANOVA route needs batch identifiers spanning at least two lots.',
                parameterName = 'batchIdentifiers', value = self.batchCount,
                validRange    = 'At least 2 distinct lots'
            )

        identifiers = np.asarray(self.batchIdentifiers)
        unique      = np.unique(identifiers)

        batchMeans  = np.array([np.mean(self.sampleData[identifiers == batch]) for batch in unique])
        batchSizes  = np.array([np.sum(identifiers == batch) for batch in unique], dtype = float)

        grandMean = float(np.mean(self.sampleData))

        withinSumSquares = float(sum(np.sum((self.sampleData[identifiers == batch] -
                                             np.mean(self.sampleData[identifiers == batch])) ** 2)
                                     for batch in unique))
        betweenSumSquares = float(np.sum(batchSizes * (batchMeans - grandMean) ** 2))

        withinDegrees  = self.sampleSize - self.batchCount
        betweenDegrees = self.batchCount - 1

        withinVariance = withinSumSquares / withinDegrees if withinDegrees > 0 else 0.0
        betweenMeanSquare = betweenSumSquares / betweenDegrees if betweenDegrees > 0 else 0.0

        # Effective per-batch size for unbalanced designs
        effectiveSize = (self.sampleSize - np.sum(batchSizes ** 2) / self.sampleSize) / betweenDegrees \
                        if betweenDegrees > 0 else 1.0

        betweenVariance = max(0.0, (betweenMeanSquare - withinVariance) / effectiveSize)

        totalDeviation = float(np.sqrt(withinVariance + betweenVariance))

        factor = toleranceFactorNatrella(max(self.batchCount, MINIMUM_SAMPLE_SIZE), self.basis) \
                 if self.batchCount < MINIMUM_SAMPLE_SIZE \
                 else toleranceFactorNatrella(self.batchCount, self.basis)

        anovaLimit = grandMean - factor * totalDeviation

        pooledLimit = self.toleranceLimit if not np.isnan(self.toleranceLimit) else \
                      grandMean - toleranceFactorNatrella(self.sampleSize, self.basis) * \
                      float(np.std(self.sampleData, ddof = 1))

        result = {'grandMean': grandMean,
                  'withinLotDeviation': float(np.sqrt(withinVariance)),
                  'betweenLotDeviation': float(np.sqrt(betweenVariance)),
                  'totalDeviation': totalDeviation,
                  'effectiveBatchSize': float(effectiveSize),
                  'kFactor': factor,
                  'anovaBasisValue': anovaLimit,
                  'pooledBasisValue': pooledLimit,
                  'penaltyFraction': (pooledLimit - anovaLimit) / pooledLimit if pooledLimit else 0.0}

        if betweenVariance > withinVariance:
            self.allowableNotes.append(
                f'Between-lot variation exceeds within-lot variation '
                f'({np.sqrt(betweenVariance) / 1.0e6:.1f} against '
                f'{np.sqrt(withinVariance) / 1.0e6:.1f} MPa). The pooled basis value overstates '
                f'the allowable by {result["penaltyFraction"] * 100.0:.1f} percent and the ANOVA '
                f'value is the defensible one. This is a process control finding as much as a '
                f'statistical one.')

        return result

    def calculateNonparametricBasis(self) -> dict:

        '''

        Order statistic basis value, assuming no distribution at all.

        The r-th smallest observation is a lower tolerance bound with confidence

            C = 1 - sum_{i=0}^{r-1} C(n, i) p^i (1-p)^(n-i)

        where p is the exceedance probability. Solving for the largest r that still meets the target
        confidence gives the rank to use. For B-basis at 95 percent confidence this needs n = 29 to
        use the lowest observation at all, and A-basis needs n = 299, which is precisely why the
        parametric route exists.

        '''

        exceedance = BASIS_EXCEEDANCE[self.basis]
        sorted_    = np.sort(self.sampleData)

        rank = 0
        for candidate in range(1, self.sampleSize + 1):
            if SCIPY_AVAILABLE:
                confidence = 1.0 - scipyStats.binom.cdf(candidate - 1, self.sampleSize,
                                                        1.0 - exceedance)
            else:
                confidence = 1.0 - sum(
                    float(np.math.comb(self.sampleSize, index)) *
                    (1.0 - exceedance) ** index * exceedance ** (self.sampleSize - index)
                    for index in range(candidate))
            if confidence >= self.confidence:
                rank = candidate
            else:
                break

        if rank == 0:
            required = 29 if self.basis == 'B' else 299
            self.allowableNotes.append(
                f'A non-parametric {self.basis}-basis needs at least {required} specimens before '
                f'even the lowest observation qualifies as a tolerance bound, and this sample has '
                f'{self.sampleSize}. This is the cost of assuming nothing about the distribution, '
                f'and it is why metallic allowables are computed parametrically.')
            return {'rank': 0, 'value': None, 'requiredSampleSize': required}

        return {'rank': rank, 'value': float(sorted_[rank - 1]),
                'requiredSampleSize': 29 if self.basis == 'B' else 299}

    def compareBasisRoutes(self) -> dict:

        '''

        What the two assumptions behind a basis value are worth, in per cent of the number.

        A normal-theory basis rests on two things the tolerance factor cannot see. It assumes the
        population is normal, and where the sample spans lots it assumes they can be pooled. Both
        are usually reasonable and neither is checked by the arithmetic, so this runs the routes
        that drop each assumption and reports the difference.

        **The normality cost** is the pooled normal-theory value against the order statistic value,
        which assumes no distribution at all. **The pooling cost** is the pooled value against the
        ANOVA value, which separates within-lot from between-lot variance.

        **Neither difference is an error.** The distribution-free route is a different estimator
        with its own conservatism: it pays for assuming nothing by needing 29 specimens before it
        can use its lowest observation for B-basis and 299 for A-basis, so on a small sample it is
        low for reasons that have nothing to do with normality. What the comparison bounds is how
        much the assumption is worth, which is the quantity a reader actually needs and the one a
        single basis value hides.

        '''

        self._validateInputs()

        normal = self.calculateBasisValue()[self.basis]['value']

        findings = []

        # -- Normality --------------------------------------------------------------------------- #

        distributionFree = self.calculateNonparametricBasis()

        normalityCost = np.nan

        if distributionFree['value'] is not None:
            normalityCost = normal / distributionFree['value'] - 1.0

        fit = self.fitDistribution()

        normalRejected = bool(fit.get('normal', {}).get('rejected', False))

        # -- Pooling ----------------------------------------------------------------------------- #

        poolingCost = np.nan
        anova       = None

        if self.batchIdentifiers is not None and len(np.unique(self.batchIdentifiers)) > 1:

            anova = self.calculateAnovaBasis()

            if anova['anovaBasisValue'] > 0.0:
                poolingCost = anova['pooledBasisValue'] / anova['anovaBasisValue'] - 1.0

        # -- Findings ---------------------------------------------------------------------------- #

        if np.isfinite(normalityCost):
            findings.append(
                f'Assuming normality is worth {normalityCost:+.1%} of the basis value against an '
                f'order statistic bound that assumes nothing. The order statistic route is not the '
                f'truth, it is a different estimator that pays for its generality, so this bounds '
                f'the assumption rather than measuring an error.')
        else:
            findings.append(
                f'The sample of {len(self.sampleData)} is too small for a distribution-free bound '
                f'at {self.basis}-basis, which needs '
                f'{distributionFree["requiredSampleSize"]}. **The normality assumption is doing '
                f'all of the work and nothing here can say how much that is worth.**')

        if normalRejected:
            findings.append(
                '**Anderson-Darling rejects normality on this sample at five per cent.** On '
                'metallic strength data that usually means the sample mixes product forms, heats '
                'or test temperatures rather than that the metal is non-normal, and the fix is to '
                'split the sample rather than to change the distribution.')

        if np.isfinite(poolingCost):
            findings.append(
                f'Pooling the lots is worth {poolingCost:+.1%} against the ANOVA route, on '
                f'{len(np.unique(self.batchIdentifiers))} lots with a between-lot deviation of '
                f'{anova["betweenLotDeviation"] / 1.0e6:.1f} MPa against a within-lot '
                f'{anova["withinLotDeviation"] / 1.0e6:.1f} MPa. **Pooling is unconservative '
                f'whenever between-lot variation is real**, because it counts lot scatter as if it '
                f'were specimen scatter.')
        else:
            findings.append(
                '**No lot identifiers, so the pooling assumption cannot be checked at all.** A '
                'sample from one lot supports a basis value for that lot and says nothing about '
                'the next one.')

        self.findings = findings

        return {'basis':             self.basis,
                'normalTheoryValue': normal,
                'distributionFreeValue': distributionFree['value'],
                'anovaValue':        anova['anovaBasisValue'] if anova else None,
                'normalityCost':     normalityCost,
                'poolingCost':       poolingCost,
                'normalityRejected': normalRejected,
                'lotCount':          (len(np.unique(self.batchIdentifiers))
                                      if self.batchIdentifiers is not None else 0),
                'findings':          findings}

    def applyKnockdowns(self) -> dict:

        '''

        Walk the ordered knockdown chain from the tolerance limit to the design value.

        Knockdowns compound multiplicatively and the chain is recorded step by step, because a
        design value that arrives with no audit trail cannot be defended and cannot be revisited
        when one of its assumptions changes.

        '''

        if np.isnan(self.toleranceLimit):
            self.calculateBasisValue()

        self.knockdownChain = [{'step': 'Sample mean (typical)', 'factor': None,
                                'value': self.mean, 'basis': f'{self.sampleSize} specimens'}]

        self.knockdownChain.append({
            'step': f'{self.basis}-basis tolerance limit',
            'factor': self.toleranceLimit / self.mean,
            'value': self.toleranceLimit,
            'basis': f'k = {self.kFactor:.3f} at n = {self.sampleSize}, '
                     f'{self.selectedDistribution} distribution'})

        running = self.toleranceLimit

        for name, specification in self.knockdowns.items():

            if isinstance(specification, str):
                entry = STANDARD_KNOCKDOWNS.get(specification)
                if entry is None:
                    raise InvalidInputError(
                        message       = f'Unknown standard knockdown \'{specification}\'.',
                        parameterName = 'knockdowns', value = specification,
                        validRange    = str(sorted(STANDARD_KNOCKDOWNS.keys()))
                    )
                factor      = entry['factor']
                explanation = entry['basis']
            else:
                factor      = float(specification)
                explanation = 'User supplied factor'
                if not 0.0 < factor <= 1.0:
                    raise InvalidInputError(
                        message       = f'Knockdown \'{name}\' has factor {factor}. A knockdown '
                                        f'must reduce the value, so it lies in (0, 1].',
                        parameterName = 'knockdowns', value = factor, validRange = '(0, 1]'
                    )

            running *= factor
            self.knockdownChain.append({'step': name, 'factor': factor, 'value': running,
                                        'basis': explanation})

        self.designValue = running

        totalFactor = self.designValue / self.mean
        self.knockdownChain.append({'step': 'Design value', 'factor': totalFactor,
                                    'value': self.designValue,
                                    'basis': f'{(1.0 - totalFactor) * 100.0:.1f} percent below the '
                                             f'typical value in total'})

        if totalFactor < 0.5:
            self.allowableNotes.append(
                f'The chain removes {(1.0 - totalFactor) * 100.0:.0f} percent of the typical '
                f'value. That is a large number and it is worth asking whether one of the '
                f'knockdowns can be bought back: qualifying a casting process, adding a post-weld '
                f'heat treatment, or machining an additive surface each remove one link.')

        return {'designValue': self.designValue, 'totalFactor': totalFactor,
                'chain': self.knockdownChain}

    def selectDesignValue(self) -> dict:

        '''

        Choose A or B basis from the load path, and report the cost of the choice.

        A single load path means failure of one element causes loss of structural integrity, and it
        requires A-basis. Redundant structure that can redistribute load permits B-basis. A pressure
        vessel wall is single load path, which is why the He bottle in the worked example is sized
        on A-basis and pays for it.

        '''

        if not self.basisValues:
            self.calculateBasisValue()

        required = 'A' if self.loadPath == 'single' else 'B'

        aValue = self.basisValues['A']['value']
        bValue = self.basisValues['B']['value']

        result = {'loadPath': self.loadPath, 'requiredBasis': required,
                  'aBasis': aValue, 'bBasis': bValue,
                  'selected': self.basisValues[required]['value'],
                  'costOfSingleLoadPath': (bValue - aValue) / bValue}

        self.basis          = required
        self.kFactor        = self.basisValues[required]['kFactor']
        self.toleranceLimit = self.basisValues[required]['value']

        self.allowableNotes.append(
            f'A {self.loadPath} load path requires {required}-basis. Choosing A over B costs '
            f'{result["costOfSingleLoadPath"] * 100.0:.1f} percent of the allowable at this sample '
            f'size, and that gap narrows as n grows: it is partly a material property and partly a '
            f'statement about how much testing was done.')

        return result

    def calculateMarginOfSafety(self, appliedStress: float, factorOfSafety: float = 1.5) -> dict:

        '''

        Margin of safety against the design value.

            MS = designValue / (appliedStress * factorOfSafety) - 1

        Positive is acceptable. Reported alongside the applied stress and the factor so the three
        cannot be separated from each other in a summary table.

        '''

        if np.isnan(self.designValue):
            self.applyKnockdowns()

        if appliedStress <= 0.0:
            raise InvalidInputError(
                message       = 'Applied stress must be positive.',
                parameterName = 'appliedStress', value = appliedStress, validRange = 'Greater than 0'
            )

        margin = self.designValue / (appliedStress * factorOfSafety) - 1.0

        if margin < 0.0:
            self.allowableNotes.append(
                f'Negative margin of safety: {margin:+.3f}. The applied stress of '
                f'{appliedStress / 1.0e6:.1f} MPa with a factor of {factorOfSafety} exceeds the '
                f'design value of {self.designValue / 1.0e6:.1f} MPa.')

        return {'appliedStress': appliedStress, 'factorOfSafety': factorOfSafety,
                'designValue': self.designValue, 'marginOfSafety': margin,
                'acceptable': margin >= 0.0}

    def calculateRequiredSampleSize(self, targetRatio: float) -> dict:

        '''

        How many specimens are needed for the basis value to reach a target fraction of the mean.

        Inverts the tolerance factor relation. Given an observed coefficient of variation,

            targetRatio = 1 - k(n) * CV        so        k(n) = (1 - targetRatio) / CV

        and n follows by solving that. The answer is frequently discouraging, and that is the useful
        part: it converts an aspiration about the allowable into a testing budget.

        '''

        if np.isnan(self.coefficientOfVariation):
            self.calculateBasisValue()

        if not 0.0 < targetRatio < 1.0:
            raise InvalidInputError(
                message       = 'Target ratio is the basis value as a fraction of the mean.',
                parameterName = 'targetRatio', value = targetRatio, validRange = '(0, 1)'
            )

        targetFactor = (1.0 - targetRatio) / self.coefficientOfVariation

        limitFactor = BASIS_QUANTILE[self.basis]

        if targetFactor <= limitFactor:
            return {'targetRatio': targetRatio, 'requiredKFactor': targetFactor,
                    'requiredSampleSize': None, 'achievable': False,
                    'limitingRatio': 1.0 - limitFactor * self.coefficientOfVariation,
                    'note': f'Unreachable at any sample size. Even with infinite data the '
                            f'{self.basis}-basis factor cannot fall below {limitFactor:.3f}, which '
                            f'caps the ratio at '
                            f'{1.0 - limitFactor * self.coefficientOfVariation:.3f} for this '
                            f'coefficient of variation. Reducing process scatter is the only route.'}

        def residual(size: float) -> float:
            return toleranceFactorNatrella(max(int(round(size)), 5), self.basis) - targetFactor

        try:
            solved = secantSolve(residual, 30.0, 60.0, tolerance = 1.0e-4, maximumIterations = 200)
            required = max(MINIMUM_SAMPLE_SIZE, int(np.ceil(solved)))
        except Exception:
            required = None
            for candidate in range(MINIMUM_SAMPLE_SIZE, 5000):
                if toleranceFactorNatrella(candidate, self.basis) <= targetFactor:
                    required = candidate
                    break

        return {'targetRatio': targetRatio, 'requiredKFactor': targetFactor,
                'requiredSampleSize': required, 'achievable': required is not None,
                'currentSampleSize': self.sampleSize,
                'currentRatio': self.toleranceLimit / self.mean}

    def generateReport(self, outputDir: str = None) -> str:

        '''

        Build a formatted results table with the full knockdown chain.

        '''

        if not self.basisValues:
            self.calculateBasisValue()

        rows = [
            ['Property',            f'{self.propertyName}'],
            ['Sample size',         f'{self.sampleSize} specimens'
                                    + (f' across {self.batchCount} lots' if self.batchCount else '')],
            ['Distribution',        f'{self.selectedDistribution}'],
            ['Mean',                f'{self.mean / 1.0e6:.1f} MPa'],
            ['Standard deviation',  f'{self.standardDeviation / 1.0e6:.1f} MPa'],
            ['Coefficient of variation', f'{self.coefficientOfVariation * 100.0:.2f} %'],
            ['k-factor method',     f'{self.kFactorMethod}'],
            ['A-basis',             f'{self.basisValues["A"]["value"] / 1.0e6:.1f} MPa '
                                    f'(k = {self.basisValues["A"]["kFactor"]:.3f}, '
                                    f'{self.basisValues["A"]["ratioToMean"] * 100.0:.1f} % of mean)'],
            ['B-basis',             f'{self.basisValues["B"]["value"] / 1.0e6:.1f} MPa '
                                    f'(k = {self.basisValues["B"]["kFactor"]:.3f}, '
                                    f'{self.basisValues["B"]["ratioToMean"] * 100.0:.1f} % of mean)'],
            ['Load path',           f'{self.loadPath}, requires {self.basis}-basis']
        ]

        if not np.isnan(self.designValue):
            rows.append(['Design value', f'{self.designValue / 1.0e6:.1f} MPa'])

        report = formatReportTable(rows, ['Quantity', 'Value'], title = 'DESIGN ALLOWABLE REPORT')

        if self.knockdownChain:
            chainRows = [[entry['step'],
                          '' if entry['factor'] is None else f'{entry["factor"]:.4f}',
                          f'{entry["value"] / 1.0e6:.1f}',
                          entry['basis']] for entry in self.knockdownChain]
            report += '\n\n' + formatReportTable(
                chainRows, ['Step', 'Factor', 'Value [MPa]', 'Basis'],
                title = 'ALLOWABLES LADDER')

        for note in self.allowableNotes:
            report += f'\nCAUTION: {note}\n'

        if outputDir is not None:
            import os
            os.makedirs(outputDir, exist_ok = True)
            with open(os.path.join(outputDir, 'allowablesReport.txt'), 'w') as fileHandle:
                fileHandle.write(report)

        return report

    # -------------------------------------------------------------------------------------------- #
    # -- Private Methods -- #
    # -------------------------------------------------------------------------------------------- #

    def _validateInputs(self) -> None:

        '''

        Physical sanity checks on the inputs.

        '''

        if self.sampleSize < 2:
            raise InvalidInputError(
                message       = 'At least two specimens are needed to estimate a standard deviation.',
                parameterName = 'sampleData', value = self.sampleSize, validRange = 'At least 2'
            )

        if np.any(self.sampleData <= 0.0):
            raise InvalidInputError(
                message       = 'Sample data must be positive. A negative strength is a data error.',
                parameterName = 'sampleData', value = float(np.min(self.sampleData)),
                validRange    = 'All values greater than 0'
            )

        if self.basis not in BASIS_QUANTILE:
            raise InvalidInputError(
                message       = f'Unknown basis \'{self.basis}\'. This class computes A and B basis; '
                                f'an S-basis is a specification minimum and is not computed from data.',
                parameterName = 'basis', value = self.basis, validRange = "'A' or 'B'"
            )

        if self.distribution != 'auto' and self.distribution not in SUPPORTED_DISTRIBUTIONS:
            raise InvalidInputError(
                message       = f'Unknown distribution \'{self.distribution}\'.',
                parameterName = 'distribution', value = self.distribution,
                validRange    = str(SUPPORTED_DISTRIBUTIONS + ('auto',))
            )

        if self.loadPath not in ('single', 'redundant'):
            raise InvalidInputError(
                message       = f'Unknown load path \'{self.loadPath}\'.',
                parameterName = 'loadPath', value = self.loadPath,
                validRange    = "'single' or 'redundant'"
            )

        if np.size(self.batchIdentifiers) > 0 and \
           np.size(self.batchIdentifiers) != self.sampleSize:
            raise InvalidInputError(
                message       = 'batchIdentifiers must have one entry per specimen.',
                parameterName = 'batchIdentifiers', value = np.size(self.batchIdentifiers),
                validRange    = f'Exactly {self.sampleSize} entries'
            )
