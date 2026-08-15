
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

# How strong a check a comparison actually is. Recording this stops a weaker check being described
# as a stronger one, which is the failure mode that made this directory necessary in the first
# place.
VALIDATION_LEVELS = {
    'hardware': 'Compared against measured or specified performance of real hardware. The '
                'strongest available and the only one that can catch a wrong model',
    'standard': 'Reproduces a published standard formula or tabulated level exactly. Catches an '
                'implementation error and cannot catch an error in the standard',
    'internal': 'Checked only against other parts of this repository. Catches drift and catches '
                'nothing else',
    'unvalidated': 'No external anchor. Recorded with what depends on it',
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

    'raoWallAngles': {
        'source': 'Rao 1958, Exhaust nozzle contour for optimum thrust; the wall angle chart '
                  'reproduced as Huzel and Huang figure 4-16',
        'kind': 'estimate',
        'band': 1.0,
        'bandUnit': 'degrees',
        'bias': 'none',
        'note': 'The logarithmic fit reproduces the published chart to about a degree between area '
                'ratios of 10 and 100. It is a fit to design data rather than a derivation, and '
                'the length fraction correction outside 0.6 to 1.0 is an extrapolation. A degree '
                'of exit angle is worth roughly 0.1 per cent of divergence efficiency at these '
                'angles, so the band is not negligible; it is smaller than the error the lookup '
                'table it replaced was making, which was three and a half degrees.'},
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

    'filmCoolingPenalty': {
        'domain': 'propulsion/combustionDevices',
        'calculation': 'The c* efficiency penalty per unit film fraction, 0.3 to 0.5',
        'reason': 'A commonly quoted range with no single sourced value found. The real penalty '
                  'depends on how much of the film propellant reaches the core and burns, which '
                  'depends on the element pattern and the chamber length.',
        'consequence': 'The worked example trades film fraction against cooling closure, and the '
                       'trade moves with this number. An earlier version of the Injector class '
                       'asserted the penalty equalled the film fraction, which is the pessimistic '
                       'end of the range stated as a value and overstates it by two to three '
                       'times.',
        'nextStep': 'Hot fire data relating measured c* efficiency to film fraction on a single '
                    'chamber.'},

    'bellWettedArea': {
        'domain': 'propulsion/combustionDevices, using propulsion/nozzles',
        'calculation': 'The nozzle wetted area that the cooling circuit is sized against',
        'reason': 'combustionDevices treats the nozzle as a cone frustum from throat to exit. A '
                  'Rao bell bulges outward from that straight line, so it has more wetted area, '
                  'and NozzleContour integrates the real contour to get it. Neither number has '
                  'been checked against a measured wetted area, because published engines give '
                  'channel counts rather than areas.',
        'consequence': 'On the reference booster the integrated area is 4308 cm^2 against a '
                       'frustum estimate of 3928 cm^2, a ratio of 1.097. The nozzle is about two '
                       'thirds of the wetted area, so the total is understated by about 6.6 per '
                       'cent and the integrated heat load rises from 8.13 to roughly 8.66 MW. '
                       'That circuit already fails to close, so the direction is safe and the '
                       'correction has been recorded rather than propagated into the '
                       'combustionDevices example.',
        'nextStep': 'Either propagate the contour area into RegenerativeCooling, which couples the '
                    'two sub-domains, or accept the frustum as a stated conservatism in the wrong '
                    'direction. The second is the current position and it is a position, not an '
                    'oversight.'},

    'ignitionOverpressureBound': {
        'domain': 'propulsion/ignitionAndStart',
        'calculation': 'The constant-volume ignition overpressure, as accumulated mass over steady '
                       'chamber gas mass',
        'reason': 'Hard start pressure spikes are recorded on test stands and essentially never '
                  'published with the geometry, the flow schedule and the ignition delay needed to '
                  'reconstruct them. Nothing found states all four.',
        'consequence': 'The bound is loose in a known direction and by an unknown amount. It '
                       'assumes everything admitted is at the right mixture ratio, fully '
                       'vaporised, burns to completion, and burns faster than the nozzle vents. '
                       'None of those holds, so the absolute spike is an overestimate. What the '
                       'sub-domain uses it for is the RANKING of ignition delays and start flow '
                       'fractions, which is robust to all four assumptions because they scale '
                       'every case the same way.',
        'nextStep': 'A hot fire record with chamber geometry, measured ignition delay, the valve '
                    'schedule and the recorded spike. Failing that, restrict every claim to the '
                    'ranking, which is what the tests assert.'},

    'igniterEnergy': {
        'domain': 'propulsion/ignitionAndStart',
        'calculation': 'The energy figures in IGNITER_TYPES',
        'reason': 'Order of magnitude figures for what each device delivers, with no single '
                  'sourced value found per type.',
        'consequence': 'They must not be used to size an igniter. They exist to support the '
                       'statement that every device on the list delivers far more than the '
                       'minimum ignition energy of the mixture, which is the point being made, '
                       'and no selection in this sub-domain depends on them.',
        'nextStep': 'Either source delivered energy per device type or remove the numbers and keep '
                    'the qualitative statement.'},

    'shutdownImpulseScatter': {
        'domain': 'propulsion/ignitionAndStart',
        'calculation': 'The tailoff impulse efficiency of 0.5 and the run-to-run scatter of 15 per '
                       'cent',
        'reason': 'The dribble volume burns at a falling and badly controlled mixture ratio, in a '
                  'collapsing chamber, through a separating nozzle. No published figure was found '
                  'for either the efficiency or its repeatability.',
        'consequence': 'The residual impulse magnitude moves directly with the first number. The '
                       'conclusion the sub-domain draws does NOT: it is that the scatter rather '
                       'than the magnitude reaches the trajectory, and that holds for any scatter '
                       'that is not zero.',
        'nextStep': 'Flight or stand data on cutoff impulse repeatability for a single engine '
                    'type. This is measured routinely and rarely published.'},

    'chillDownMeanSpecificHeat': {
        'domain': 'propulsion/ignitionAndStart',
        'calculation': 'UNFITTED_SPECIFIC_HEAT, for the two metals with no published curve',
        'reason': 'Closed for stainless and aluminium and open for two metals. The NIST cryogenic '
                  'material properties database publishes specific heat curve fits over 4 to 300 K '
                  'for 304 stainless, 316 stainless and 6061-T6 aluminium, and those are now '
                  'integrated over the range each chill-down actually traverses rather than '
                  'tabulated as a mean. The database carries thermal conductivity and linear '
                  'expansion for Ti-6Al-4V and Inconel 718 and NO specific heat, so those two keep '
                  'a constant mean over roughly 90 to 300 K.',
        'consequence': 'Confined to those two metals, and the direction is known. A constant mean '
                       'quoted over the oxygen range never sees the part of the curve below 90 K '
                       'where specific heat collapses, so it overstates a hydrogen chill-down. On '
                       'stainless, where both routes exist, the overstatement is 16 per cent. '
                       'Aluminium 2219 is mapped onto the 6061-T6 curve rather than left constant, '
                       'which is a stated approximation: specific heat per kilogram in a dilute '
                       'substitutional alloy is set by the base lattice, and the heavier copper '
                       '2219 carries means the substitution should run a few per cent high.',
        'nextStep': 'A published cryogenic specific heat curve for Ti-6Al-4V and for Inconel 718, '
                    'from NIST Monograph 177 or an equivalent compilation. Neither is in the open '
                    'NIST cryogenics database, which is why this entry did not close entirely.'},

    'instrumentUncertainty': {
        'domain': 'propulsion/propulsionTesting',
        'calculation': 'INSTRUMENT_UNCERTAINTY, the per-channel relative uncertainties',
        'reason': 'Representative of good practice on a development stand rather than taken from '
                  'any calibration certificate. A real budget comes from the certificates and '
                  'from an in-situ calibration, neither of which is a published quantity.',
        'consequence': 'Every uncertainty this sub-domain reports scales with them. The two '
                       'conclusions drawn do not: that specific impulse must not be computed as '
                       'c* times Cf with independent uncertainties is exact algebra, and that a '
                       'one per cent effect is unresolvable while a four per cent effect is '
                       'marginal holds for any plausible set of channel figures.',
        'nextStep': 'Calibration certificates from a real stand, and an in-situ thrust '
                    'calibration at flight line pressure to quantify the load path bias, which is '
                    'the term most often missing.'},

    'stabilityDampCriterion': {
        'domain': 'propulsion/propulsionTesting',
        'calculation': 'Not performed. The pass or fail verdict of a dynamic stability rating',
        'reason': 'The CPIA combustion stability guidelines specify how quickly a perturbation '
                  'must decay for an engine to be rated stable. They were first published in 1971, '
                  'the current revision was as of 2021 nearly 25 years old and being updated, and '
                  'they are not openly available. The criterion has not been read.',
        'consequence': 'HotFireTest.checkStabilityRating() reports the perturbation adequacy and '
                       'the device viability, both of which are sourced, and deliberately does '
                       'NOT report a pass or a fail. Stating a damp time from memory would put an '
                       'unsourced number into the one part of this repository whose purpose is to '
                       'prevent exactly that.',
        'nextStep': 'Obtain the current CPIA guideline and carry its criterion with its citation. '
                    'Until then the tool checks what it can and says what it cannot.'},

    'testSettlingTimes': {
        'domain': 'propulsion/propulsionTesting',
        'calculation': 'CHAMBER_SETTLING_RESIDENCE_TIMES and WALL_SETTLING_TIME',
        'reason': 'Representative time constants rather than measured ones. The wall constant in '
                  'particular depends on the wall thickness, the material and the cooling '
                  'circuit, none of which this class takes as an input.',
        'consequence': 'The usable thermal window in a burn scales with the second of them. The '
                       'conclusion drawn is that the two settling times differ by three orders of '
                       'magnitude and that a short burn gives a valid performance number and an '
                       'invalid wall temperature, and that ordering is robust to any plausible '
                       'value.',
        'nextStep': 'Compute the wall constant from the thermalManagement lumped capacitance '
                    'model for the actual chamber, which is tractable and would replace a '
                    'constant with a calculation.'},

    'ascentLossModel': {
        'domain': 'vehicleArchitecture',
        'calculation': 'The gravity, drag and steering loss correlations in AscentTrajectory',
        'reason': 'Representative reference losses and power-law exponents rather than a '
                  'trajectory integration. A real ascent loss comes from optimising a trajectory '
                  'with a steering law, atmospheric data and a vehicle aerodynamic model, none of '
                  'which this repository carries.',
        'consequence': 'The absolute loss total, and therefore the delta-V target every vehicle '
                       'here is sized to, moves with these numbers. The conclusion drawn does not: '
                       'that the loss-minimising thrust to weight sits far above the practical '
                       'band, so the loss budget sets a floor rather than a target, holds for any '
                       'exponent pair where gravity loss falls faster than drag loss rises, which '
                       'is the whole plausible range.',
        'nextStep': 'A trajectory integration, or published loss breakdowns for several vehicles '
                    'with their liftoff thrust to weight stated alongside.'},

    'nonTankDryFraction': {
        'domain': 'vehicleArchitecture',
        'calculation': 'NON_TANK_DRY_FRACTION, everything in a stage that is not tank',
        'reason': 'Engines, thrust structure, avionics, feed lines, separation hardware and skirts '
                  'as a single fraction of propellant mass. That is how a conceptual estimate is '
                  'made before any of it exists, and it is not a measurement.',
        'consequence': 'It is doing as much work as the tank model in setting the structural '
                       'coefficient, and unlike the tank model it is a constant rather than a '
                       'calculation. The mass chain amplification is insensitive to it because it '
                       'is a difference rather than a level, but the closed vehicle mass is not.',
        'nextStep': 'Build it from the domains that own the parts: engine mass from propulsion, '
                    'thrust structure from aerospaceStructures, feed lines from fluidSystems. '
                    'Every one of those already exists in this repository, which makes this the '
                    'most tractable gap in the register.'},

    'massGrowthAllowance': {
        'domain': 'vehicleArchitecture',
        'calculation': 'MASS_GROWTH_ALLOWANCE and DEFAULT_MARGIN_POLICY',
        'reason': 'The shape follows AIAA and ANSI mass properties practice, where an allowance is '
                  'applied by design maturity because estimates at that maturity have historically '
                  'grown by about that much. The specific percentages here were not taken from the '
                  'standard, which was not read.',
        'consequence': 'Every predicted mass and every margin verdict scales with them. The '
                       'distinction the domain actually makes, that growth allowance and margin '
                       'are different things and adding one while calling it the other leaves a '
                       'programme with neither, is structural and does not depend on the values.',
        'nextStep': 'Obtain AIAA S-120 or the ANSI/AIAA mass properties standard and carry its '
                    'table with the citation, replacing the representative percentages.'},

    'pyroshockMagnitude': {
        'domain': 'mechanismsAndSeparation',
        'calculation': 'Not performed. The shock response spectrum produced by a band release or a '
                       'pyrotechnic device',
        'reason': 'Pyroshock prediction is a test-derived discipline. The response depends on the '
                  'joint, the structure behind it, the path and the mounting of whatever is being '
                  'protected, and no analytic model in the open literature predicts it to better '
                  'than an order of magnitude.',
        'consequence': 'ClampBand computes the released strain energy and deliberately stops '
                       'there. The energy is the right quantity to compare designs against each '
                       'other and against a device with a measured signature; a shock response '
                       'spectrum from this library would carry more authority than it earns.',
        'nextStep': 'A measured shock signature for a comparable device, which turns the energy '
                    'into a scaling parameter rather than an absolute. Failing that, keep the '
                    'boundary where it is.'},

    'preloadRelaxation': {
        'domain': 'mechanismsAndSeparation',
        'calculation': 'PRELOAD_RELAXATION, the embedment, short-term and storage losses',
        'reason': 'Representative fractions rather than measured ones. Real relaxation depends on '
                  'the surface finish, the coating, the contact pressure and the temperature '
                  'history, none of which this class takes as an input.',
        'consequence': 'Every retained preload and every joint margin scales with them. The '
                       'conclusion the domain draws does not: that the losses compound rather than '
                       'add, that storage is the term nobody plans for because it depends on a '
                       'schedule, and that a margin has to be carried against the relaxed preload '
                       'rather than the installed one, all hold for any non-zero values.',
        'nextStep': 'Preload retention test data on a representative joint, which is a standard '
                    'bolted-joint test and is the most tractable gap in this domain.'},

    'springRateTolerance': {
        'domain': 'mechanismsAndSeparation',
        'calculation': 'SPRING_RATE_TOLERANCE, and the statistical tipoff model built on it',
        'reason': 'Ten per cent is a common commercial spring rate tolerance and it is not a '
                  'measurement of any particular supply. The statistical combination also assumes '
                  'the rate errors are independent, which springs from a single production lot '
                  'are not.',
        'consequence': 'The tipoff rate scales with the tolerance directly. The deterministic '
                       'worst case is independent of spring count and the statistical case falls '
                       'as one over its root, and BOTH of those structural results are '
                       'independent of the value. The independence assumption is the weaker of '
                       'the two and the domain says so: a lot-correlated set has bought the '
                       'statistical case and specified the worst one.',
        'nextStep': 'Measured rate distributions for a real spring supply, and a correlation '
                    'coefficient within a lot. The second is what decides whether the statistical '
                    'model is usable at all.'},

    'wireAmpacity': {
        'domain': 'electricalPower',
        'calculation': 'SINGLE_WIRE_AMPACITY, BUNDLE_DERATING and ALTITUDE_DERATING',
        'reason': 'AS50881 gives these as curves rather than tables and the standard is not '
                  'openly available. The values here are consistent with common practice and are '
                  'not read from it.',
        'consequence': 'The ampacity-limited gauge moves with them. The conclusion the domain '
                       'draws does NOT: that voltage drop rather than ampacity chooses the gauge '
                       'on a launch vehicle harness is a resistance calculation, and the AWG '
                       'resistance is exact. The derating would have to be wrong by several gauge '
                       'steps to change which constraint binds.',
        'nextStep': 'Obtain AS50881 and carry its curves with the citation. The bundle derating is '
                    'the larger of the two effects and the one worth getting first.'},

    'batteryDerating': {
        'domain': 'electricalPower',
        'calculation': 'DEPTH_OF_DISCHARGE, TEMPERATURE_CAPACITY_FACTOR, PACK_FRACTION and the '
                       'BATTERY_CHEMISTRIES specific energies',
        'reason': 'Representative values across a chemistry class rather than a specific cell '
                  'datasheet. Real capacity against temperature is a measured curve per part '
                  'number, and pack fraction depends on the mechanical and thermal design.',
        'consequence': 'The pack mass scales with all of them. The structural result does not: '
                       'that the nameplate is close to twice the energy delivered once depth of '
                       'discharge and cold multiply, and that neither factor is a margin, holds '
                       'for any plausible values.',
        'nextStep': 'Partly closed. BATTERY_CELLS carries the Panasonic NCR18650BF datasheet, '
                    'which brackets the chemistry table rather than replacing it: the library '
                    'carries 200 W h/kg for lithium ion against 248 measured, so the class figure '
                    'is conservative by 19 per cent, which is the direction a figure covering '
                    'older and higher rate chemistries should err in. What the datasheet does NOT '
                    'supply is the capacity against temperature curve, which is published as a '
                    'chart rather than a table, so TEMPERATURE_CAPACITY_FACTOR is still '
                    'representative. It also revealed a limit the library does not carry at all: '
                    'the cell cannot be charged below +10 C while it discharges to -20 C.'},

    'harnessRoutingAllowance': {
        'domain': 'electricalPower',
        'calculation': 'ROUTING_ALLOWANCE, INSULATION_MASS_FACTOR and the connector masses',
        'reason': 'Representative. Real routed length depends on the structure, and insulation '
                  'mass depends on the wire specification and the wall thickness.',
        'consequence': 'The harness mass scales with them, and harness mass is reliably '
                       'underestimated. The domain argues that counting runs and connectors beats '
                       'taking a fraction of dry mass, and that argument is about the METHOD '
                       'rather than about these numbers: a counted estimate with imperfect factors '
                       'converges and a fractional one does not.',
        'nextStep': 'Measure a real harness. This is the one gap in the repository that could be '
                    'closed with a set of scales.'},

    'imuGrades': {
        'domain': 'avionicsAndGNC',
        'calculation': 'IMU_GRADES and the AIDING_SOURCES bounds',
        'reason': 'Representative of a sensor class rather than of any part number. Real bias, '
                  'random walk and scale factor come from a specific unit datasheet and from its '
                  'calibration, and the aiding bounds depend on the receiver and the environment.',
        'consequence': 'Every absolute error figure scales with them. The structural results do '
                       'not: that the gyro bias term grows as the cube of time while the '
                       'accelerometer bias grows as the square, and therefore that the gyro term '
                       'overtakes early in a flight, follows from the integration order rather '
                       'than from any value. The crossover TIME moves with the grade and its '
                       'existence does not.',
        'nextStep': 'A datasheet for a specific IMU, which every manufacturer publishes and none '
                    'of them serves to a script. This was attempted for the Analog Devices '
                    'ADIS16507 on 14 August 2026 through the manufacturer, two distributors and '
                    'two mirrors, and every route returned a block page or timed out. Secondary '
                    'summaries quoting an in-run bias stability near 2.3 deg/hr and an angular '
                    'random walk near 0.13 deg/sqrt(hr) were found and are NOT recorded as a '
                    'reference, because this repository has been wrong three times by trusting a '
                    'summary of a document it had not read. The gap stays open until the datasheet '
                    'itself is read.'},

    'controlDisturbances': {
        'domain': 'avionicsAndGNC',
        'calculation': 'THRUST_MISALIGNMENT, CG_OFFSET_FRACTION, TRIM_ALLOWANCE and the '
                       'TVC_ARRANGEMENTS gimbal ranges',
        'reason': 'Representative values. Thrust misalignment is an engine and mounting tolerance, '
                  'the centre of gravity offset is a mass properties outcome, and the gimbal range '
                  'is a specific actuator installation.',
        'consequence': 'The trim angle and therefore the pass or fail verdict scale with them. '
                       'The conclusion drawn does not: that the governing disturbance changes '
                       'between the atmospheric and vacuum phases holds for any values where the '
                       'aerodynamic term is present in one and absent in the other, which is '
                       'always. The trim allowance of a third is explicitly a convention.',
        'nextStep': 'Engine thrust vector alignment tolerance from the propulsion supplier, and a '
                    'mass properties statement giving the lateral centre of gravity offset. Both '
                    'exist on any real programme.'},

    'telemetryOverhead': {
        'domain': 'avionicsAndGNC',
        'calculation': 'FRAMING_OVERHEAD and LINK_MARGIN',
        'reason': 'Representative. Real framing overhead depends on the telemetry standard, the '
                  'error correction coding and the frame structure, and the link margin depends on '
                  'the antenna pattern, the range and the ground station.',
        'consequence': 'The utilisation figure moves with them and the pass or fail on a marginal '
                       'plan moves with it. The result the domain reports, that a handful of '
                       'high-rate channels dominate a list of dozens, is a property of the '
                       'measurement list rather than of the overhead.',
        'nextStep': 'The telemetry standard the programme uses, which fixes the framing, and a '
                    'link budget, which fixes the margin. Neither is a research problem.'},

    'loadingPhaseFractions': {
        'domain': 'groundSystemsAndOperations',
        'calculation': 'LOADING_PHASES rate fractions and load fractions, and DEFAULT_DETANK_RECOVERY',
        'reason': 'Representative of cryogenic tanking practice rather than taken from a procedure. '
                  'Real phase rates come from the vehicle tank geometry, the geyser and water '
                  'hammer limits on the transfer line, and the level sensor arrangement, and the '
                  'detank recovery depends on whether the ground tank can accept warm return flow '
                  'at all.',
        'consequence': 'The tanking duration and the phase that dominates it both scale with them. '
                       'The structural result does not: chill-down runs at a fraction of the '
                       'transfer rate BECAUSE the point of it is to boil, so it takes a share of '
                       'the elapsed time out of all proportion to the mass it moves. That holds '
                       'for any rate fraction below one.',
        'nextStep': 'A tanking procedure with its phase transitions and rates, which every '
                    'programme writes and none publishes. The transfer line limits are already '
                    'computable in fluidSystems, so half of this could be closed internally.'},

    'scrubCauseSplit': {
        'domain': 'groundSystemsAndOperations',
        'calculation': 'SCRUB_CAUSES, and the launch commit criteria violation rates in the '
                       'worked example asset',
        'reason': 'The weather share is BOUNDED rather than unvalidated: roughly half of scrubs '
                  'at the Eastern Range across three decades were weather, which is a published '
                  'record. The split of the remaining half, and every individual criterion '
                  'violation rate, are representative.',
        'consequence': 'The per-attempt go probability and therefore the whole campaign figure '
                       'scale with the violation rates. The two results the domain reports do '
                       'not. That independent criteria multiply rather than average is arithmetic. '
                       'That attempts beat criteria as a lever follows from the cumulative '
                       'probability being one minus a product, and it holds for any rates.',
        'nextStep': 'Published launch commit criteria violation statistics by criterion, which '
                    'the range weather squadrons compile and which appear in conference papers '
                    'rather than in a standard.'},

    'weatherCorrelation': {
        'domain': 'groundSystemsAndOperations',
        'calculation': 'DEFAULT_CORRELATION and the two state chain in '
                       'LaunchAvailability.calculateCampaign',
        'reason': 'The chain is internally exact: its two conditional probabilities reproduce the '
                  'unconditional rate and give a lag one correlation coefficient of exactly the '
                  'input, and a test asserts both. The VALUE of the correlation is representative, '
                  'and a two state chain is a coarse model of a weather system in any case.',
        'consequence': 'The gap between the independent and correlated campaign figures scales '
                       'with it, and that gap is offered as the honest uncertainty in the answer '
                       'rather than as a result. The direction does not scale: correlation always '
                       'costs campaign probability, because a scrub makes the next attempt less '
                       'likely than the unconditional rate.',
        'nextStep': 'Day to day persistence of launch commit criteria violations from range '
                    'climatology, which is exactly what a launch weather officer computes.'},

    'exchangeRatios': {
        'domain': 'recoveryAndReusability',
        'calculation': 'DRY_MASS_EXCHANGE_RATIO and RESERVE_EXCHANGE_RATIO in RecoveryBudget',
        'reason': 'Largely closed, and what is left is narrow enough to state exactly. Both ratios '
                  'are now computed by StagedVehicle.exchangeRatios from the published Falcon 9 '
                  'Block 5 stage masses rather than assumed, and the RATIO between them is not an '
                  'estimate at all: differentiating the stage contribution gives dry / reserve = '
                  '1 - 1/R on the first stage mass ratio, exactly, and a test asserts the measured '
                  'value against the closed form on four vehicles. What remains unvalidated is '
                  'that the ABSOLUTE values need the two specific impulses, which that register '
                  'entry states are not published in the same source as the masses.',
        'consequence': 'Small and bounded. Swinging both specific impulses by five per cent moves '
                       'each ratio by under three per cent and moves the ratio between them not at '
                       'all, because the first stage mass ratio is fixed by the published masses '
                       'and the published payload. Nothing structural depends on either.',
        'nextStep': 'A sourced specific impulse for the Merlin 1D and the Merlin vacuum, from the '
                    'same document as the stage masses, would close the remainder. Note that '
                    'wiring the two domains together REVERSED the ordering this entry previously '
                    'assumed: the reserve costs more per kilogram than the dry mass, not less, '
                    'and the class guard that enforced the old ordering would have rejected the '
                    'correct pair. The assumed reasoning, that a reserve is carried for less of '
                    'the burn, does not survive being written down, because a recovery reserve is '
                    'spent after separation.'},

    'lifeDamageRates': {
        'domain': 'recoveryAndReusability',
        'calculation': 'LIFE_LIMITED_ITEMS damage per flight, and INSPECTION_LEVELS relative cost',
        'reason': 'Representative of the items that usually set a refurbishment interval rather '
                  'than measured for any article. A real damage per flight comes from a stress '
                  'spectrum through a fatigue curve, which aerospaceMaterials owns, applied to a '
                  'measured flight environment, which almost nothing records.',
        'consequence': 'Every flight count in the domain scales with them. The structural results '
                       'do not: that one item limits and extending it buys the gap to the next is '
                       'the same arithmetic as a turnaround driver, and that the limiting item is '
                       'not the one that looks worst after a flight is a statement about '
                       'appearance and damage rate being unrelated. Both hold for any rates.',
        'nextStep': 'A stress spectrum per flight and a fatigue curve per item, which '
                    'aerospaceStructures and aerospaceMaterials can supply between them. The '
                    'harder half is the measured flight environment, which is a telemetry '
                    'requirement rather than an analysis one.'},

    'recoveryModeFractions': {
        'domain': 'recoveryAndReusability',
        'calculation': 'RECOVERY_MODES reserve propellant and hardware dry fractions, and the '
                       'ABSORBER_EFFICIENCY table in LandingLoads',
        'reason': 'Representative. A real reserve comes from integrating the boost-back, entry and '
                  'landing burns on a specific trajectory, and a real absorber efficiency comes '
                  'from a measured force-stroke curve.',
        'consequence': 'The penalty by mode scales with the reserve fractions and the load factor '
                       'scales with the efficiency. The orderings do not: a return to the launch '
                       'site costs more than a downrange landing because it has to cancel and '
                       'reverse the downrange velocity, and a crushable core fills its '
                       'force-stroke rectangle better than a damper because a damper force follows '
                       'the velocity and falls as the vehicle stops. Both are mechanisms rather '
                       'than values.',
        'nextStep': 'A landing trajectory integration for the reserve, which is a guidance problem '
                    'this repository has declined twice for stated reasons, and a force-stroke '
                    'curve from a drop test for the efficiency. The second is far the more '
                    'tractable.'},

    'inspectionCapability': {
        'domain': 'manufacturingAndAssembly',
        'calculation': 'The a50 and sigma values in NDE_METHODS',
        'reason': 'Representative of a method rather than of any qualified procedure. A real a90 '
                  'or a90/95 comes from a demonstration on the actual geometry, material, surface '
                  'finish and access, and MIL-HDBK-1823A is emphatic that all four move it. The '
                  'MODEL is the standard and exact; the numbers put into it are not.',
        'consequence': 'Every absolute flaw size the domain reports scales with them, and so does '
                       'the verdict on whether a given inspection clears a given critical flaw. '
                       'The structural results do not. That the ratio of a90 to a50 is nine to the '
                       'power sigma follows from the logit of 0.9 being log 9. That an inspection '
                       'whose reliably detectable size exceeds the critical flaw establishes '
                       'nothing follows from the definition of both. And that the ranking by a90 '
                       'is not the ranking by usefulness follows from what each method cannot '
                       'reach, which is a mechanism rather than a value.',
        'nextStep': 'A POD demonstration report for the actual procedure, which any programme with '
                    'a fracture critical part already has, or a published one from the NTIAC '
                    'collection the handbook cites. This is the most tractable gap in the domain.'},

    'learningRates': {
        'domain': 'manufacturingAndAssembly',
        'calculation': 'LEARNING_RATES by process class',
        'reason': 'Representative by process class rather than measured for any programme. A real '
                  'learning rate is fitted to that programme cost history, and vehicleArchitecture '
                  'names both the rate and a cost estimating relationship as gaps it does not '
                  'fill.',
        'consequence': 'Every cost figure scales with them, and the flatness of the curve decides '
                       'whether a programme of ten units is near its asymptote. The structural '
                       'results do not: that every doubling costs a fixed fraction is Wright law, '
                       'that the absolute saving per doubling falls follows from it, and that the '
                       'cumulative average lags the unit cost follows from the average carrying '
                       'the early units. The ORDERING is also structural, because the more labour '
                       'a process carries the more there is to learn.',
        'nextStep': 'A cost history from a real production run, which is the same input a cost '
                    'estimating relationship needs. Neither exists in this repository and both are '
                    'named as gaps rather than assumed.'},

    'processTolerances': {
        'domain': 'manufacturingAndAssembly',
        'calculation': 'PROCESS_TOLERANCES as a fraction of nominal, and the station cycle times '
                       'in the worked example asset',
        'reason': 'Representative achievable tolerance by process for a feature of launch vehicle '
                  'size, and representative cycle times. Real numbers come from a shop and a '
                  'machine.',
        'consequence': 'The absolute stack and the absolute capacity scale with them. Neither '
                       'result does. That a k sigma statistical stack exceeds the arithmetic worst '
                       'case above a crossover of sum over root sum of squares is algebra, and it '
                       'is exactly root n for equal contributors. That capacity is the slowest '
                       'station rather than the sum follows from the stations running in parallel '
                       'on different units. Both hold for any values.',
        'nextStep': 'Process capability data from a shop, which every manufacturer holds and none '
                    'publishes. The tolerance ORDERING is textbook and is not in doubt.'},

    'casualtyAreas': {
        'domain': 'rangeSafetyAndFTS',
        'calculation': 'CASUALTY_AREA by fragment class and POPULATION_DENSITY by land use',
        'reason': 'Representative. A real casualty area comes from a fragment mass, velocity and '
                  'impact angle through a lethality model, and a real population comes from a '
                  'gridded census product rather than a land use class.',
        'consequence': 'Every casualty expectation scales linearly with both, so the margin '
                       'against the 1e-4 criterion moves with them. The structural results do '
                       'not: that risk follows population rather than impact probability follows '
                       'from the product form, and that a casualty area is far larger than a '
                       'fragment footprint is a definition rather than a value.',
        'nextStep': 'A gridded population product, which is public, and a lethality model, which '
                    'is not. DebrisDispersion now computes the impact velocity of every fragment '
                    'class, which is one of the three inputs a lethality model needs; the other '
                    'two are the impact angle and an injury criterion. The population half is the '
                    'tractable one and would replace the land use classes entirely.'},

    'impactProbabilities': {
        'domain': 'rangeSafetyAndFTS',
        'calculation': 'The regional impact probabilities and the vehicle failure probability in '
                       'the worked example asset',
        'reason': 'Representative. A real impact probability comes from propagating a debris '
                  'catalogue through an atmosphere with a wind field, from every failure time '
                  'along the trajectory, which is a Monte Carlo rather than a closed form. The '
                  'failure probability comes from a reliability argument the vehicle does not '
                  'have yet.',
        'consequence': 'The whole casualty expectation scales with them, and the failure '
                       'probability multiplies everything else, which is why the class sweeps it '
                       'and reports the value at which the criterion stops being met. **The risk '
                       'analysis inherits the reliability estimate whole**, and that is the '
                       'weakest number in it.',
        'nextStep': 'Largely closed, and by a different route than this entry expected. '
                    'DebrisDispersion propagates a fragment catalogue from the break-up state to '
                    'the ground through an exponential atmosphere with a wind, disperses each '
                    'class about its impact point, and reports the impact probability per region. '
                    'The impact probabilities in the worked example are computed rather than '
                    'assumed, and every assumed value turned out to be the wrong size. What '
                    'remains unvalidated is the CATALOGUE rather than the propagation: the '
                    'fragment counts, masses and drag areas are representative of a small two '
                    'stage vehicle and a real one comes from a structural break-up analysis of a '
                    'specific article. The vehicle failure probability is a separate matter and '
                    'is still the weakest number in the analysis.'},

    'betaFactors': {
        'domain': 'reliabilityAndMissionAssurance',
        'calculation': 'BETA_FACTORS by sharing class, and DEFAULT_COVERAGE',
        'reason': 'Representative. A real beta factor is estimated from operating experience on a '
                  'specific redundant configuration, and the published estimates for it vary by a '
                  'factor of several across industries and analysts. The MODEL is standard and its '
                  'form is not in doubt; the values are.',
        'consequence': 'Every absolute redundancy figure scales with them, and the verdict on '
                       'whether a redundant set meets a requirement moves with them. The '
                       'structural results do not. That the common cause term does not fall as '
                       'units are added is algebra. That adding a third unit buys almost nothing '
                       'once common cause dominates follows from it. And the ORDERING of the '
                       'sharing classes is a mechanism rather than a value: units that share a '
                       'design share its design errors.',
        'nextStep': 'Operating experience on a specific configuration, or one of the published '
                    'beta factor estimation methods applied to a real installation. Neither is a '
                    'research problem and both need a programme rather than a repository.'},

    'componentFailureRates': {
        'domain': 'reliabilityAndMissionAssurance',
        'calculation': 'FAILURE_RATES, and the subsystem reliabilities in the worked example asset',
        'reason': 'Representative. A component failure rate comes from operating experience or '
                  'from a parts count prediction, and the prediction handbooks have a long and '
                  'well documented history of being optimistic. Generating one here would give it '
                  'more authority than it earns, which is why the domain declines to.',
        'consequence': 'Every probability the domain reports scales with them. The structural '
                       'results do not: that series reliability multiplies, that item count is a '
                       'reliability parameter, that single point failures dominate a fault tree '
                       'and that the importance ranking differs from the probability ranking are '
                       'all consequences of the form rather than the values. The ORDERING is also '
                       'structural, because single-shot devices are non-redundant by construction.',
        'nextStep': 'Operating experience, which is the only honest source. The domain says so '
                    'explicitly rather than substituting a handbook prediction, and the basis '
                    'audit in ReliabilityBudget exists to make the difference visible.'},

    'ordinalScales': {
        'domain': 'reliabilityAndMissionAssurance',
        'calculation': 'SEVERITY_CLASSES, DETECTION_CLASSES and OCCURRENCE_BANDS in FMECA',
        'reason': 'These are conventions rather than measurements, and different programmes use '
                  'different scales. They cannot be validated because there is nothing to validate '
                  'them against: an ordinal rank is a definition.',
        'consequence': 'Every risk priority number and criticality figure depends on them, and a '
                       'different scale reorders the table. **That is the point the domain makes '
                       'rather than a weakness it has**: multiplying ordinals produces something '
                       'that sorts and does not measure, which is why criticality is reported '
                       'alongside the risk priority number and why the mandatory review filter '
                       'uses no arithmetic at all.',
        'nextStep': 'Nothing closes this, because there is nothing to close. The correct response '
                    'is to read an ordinal product as a sort rather than a measurement, and the '
                    'class is built to make that difficult to forget.'},

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


# ------------------------------------------------------------------------------------------------ #
# -- Environments: published test levels -- #
# ------------------------------------------------------------------------------------------------ #

# GEVS is unusually good validation material, because it publishes both a spectrum and the Grms that
# spectrum integrates to. The Grms is therefore an independent check on the spectrum, and a tool
# that computes one from the other sits in the middle of a closed loop.
#
# It also resolved a contradiction between two secondary sources during this work. One quoted a
# 0.16 g^2/Hz plateau at 14.1 Grms, another quoted 0.016 g^2/Hz at 10.0 Grms. Integrating the first
# gives 14.14 Grms, which matches; integrating the second gives 6.18, which does not. The 10.0 in
# the second source is the acceptance level, qualification less 3 dB, which is 14.14 / sqrt(2) =
# 10.00 exactly. Both sources were right about different things and neither said which.
RANDOM_VIBRATION_LEVELS = {

    'GEVS qualification, 22.7 kg or less': {
        'source': 'GSFC-STD-7000A, General Environmental Verification Standard, Table 2.4-3; '
                  'https://experiorlabs.com/wp-content/uploads/2019/10/'
                  'GSFC-STD-7000A-General-Environmental-Verification-Standard-GEVS-for-GSFC-'
                  'Flight-Programs-and-Projects-4-22-2013.pdf, accessed 08 August 2026',
        'kind': 'specification',
        'level': 'hardware',
        'breakpoints': [(20.0, 0.026), (50.0, 0.16), (800.0, 0.16), (2000.0, 0.026)],
        'overallRms': 14.1,
        'acceptanceRms': 10.0,
        'note': 'The generalised level a component qualifies to before flight data exists. The '
                'plateau is reached by a +6 dB per octave slope from 20 Hz, and 0.026 x (50/20)^2 '
                '= 0.1625, so the table is self-consistent. Acceptance is qualification less 3 dB, '
                'which is a factor of sqrt(2) in Grms rather than in density.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Structures: published empirical factors -- #
# ------------------------------------------------------------------------------------------------ #

# The shell buckling knockdown is the most consequential empirical factor in this repository. It is
# a curve fitted to test scatter in the 1960s, it is still what everyone uses, and it turns a
# classical buckling stress that is wrong by a factor of five into a design value.
#
# The anchor is the 2020 revision rather than the 1968 original, and reading it settled four things
# the library had wrong or missing.
#
# **The formula is unchanged after fifty two years.** Rev 2 restates Eq. 9 and Eq. 10 exactly as the
# 1968 document had them and keeps recommending them, which is a stronger statement than the
# original made: a curve that survives a full revision by the organisation that owns it has been
# re-examined rather than merely inherited.
#
# **It carries two bounds the library did not.** The parameter applies for r/t < 1500, and the
# library was allowing 3000. The correlation is unverified by experiment above L/r = 5, and the
# library said nothing.
#
# **The direction of its conservatism is now sourced rather than assumed.** Rev 2 states the curve
# is likely to bound aerospace-quality cylinders and that testing has shown buckling loads higher
# than it. That is a published statement about how hardware behaves relative to the curve, and it
# is what makes the factor safe to use without being accurate.
#
# **What is still not validated is the magnitude of that conservatism.** Knowing the curve is a
# lower bound is not knowing how far below the data it sits, and Rev 2 does not reproduce the test
# scatter in a form that can be re-fitted. That remains the difference between this entry and a
# hardware-level one.
SHELL_BUCKLING = {

    'NASA SP-8007 knockdown': {
        'source': 'NASA/SP-8007-2020/REV 2, Buckling of Thin-Walled Circular Cylinders, December '
                  '2020, section 4.1.1.1 and Eq. 9 and 10. Read from https://shellbuckling.com/'
                  'papers/classicNASAReports/NASA-SP-8007-2020Rev2FINAL.pdf, accessed '
                  '15 August 2026',
        'kind': 'derived',
        'level': 'standard',

        'formula': 'gamma = 1 - 0.901 (1 - exp(-phi)), phi = (1/16) sqrt(r/t)',
        'points': {100.0: 0.5813, 300.0: 0.4042, 500.0: 0.3217, 1000.0: 0.2238, 1500.0: 0.1791},

        # The bounds the revision states on the correlation itself.
        'maximumRadiusToThickness': 1500.0,     # [-], Eq. 10 is written for r/t below this
        'correlatedLengthToRadius':    5.0,     # [-], unverified by experiment above this

        # The other two correlations the same section recommends, both of which the library had
        # carried at the wrong value.
        'torsionCorrelationThreeQuarter': 0.67,   # [-], gamma^(3/4), Eq. 35
        'externalPressureShort':          0.5625, # [-], sqrt(gamma) = 0.75, Eq. 28
        'externalPressureLong':           0.90,   # [-], Eq. 29, the two-lobe oval mode

        'conservatismNote': 'Rev 2 states that the knockdown factor equation is likely to bound '
                            'what is expected in the design of aerospace-quality cylinders which '
                            'have well-controlled manufacturing processes, and that testing has '
                            'shown buckling loads higher than the lower bound design curve, '
                            'attributed to greater quality control minimising initial geometric '
                            'imperfections and loading nonuniformities. So the DIRECTION of the '
                            'error is published and the MAGNITUDE is not.',

        'boundsNote': 'Two bounds, and they fail differently. Above r/t = 1500 the correlation '
                      'returns a number that means nothing, which is a refusal. Above L/r = 5 the '
                      'correlation is simply unverified, and the classical prediction it '
                      'multiplies has a separate problem in the same regime: Donnell cannot see '
                      'the interaction between shell buckling and column buckling, so it becomes '
                      'UNCONSERVATIVE for long cylinders. A long shell needs a column check too.',

        'note': 'A knockdown of 0.22 at r/t 1000 means the classical stress overpredicts by a '
                'factor of four and a half, which is the reason the factor exists. Reproducing the '
                'closed form validates the implementation and not the correlation.'},

    'SP-8007 pressure stabilization': {
        'source': 'NASA/SP-8007-2020/REV 2, Eq. 48 and Figure 4-5',
        'kind': 'derived',
        'level': 'unvalidated',

        'formula': 'P_press = 2 pi E t^2 (0.605 gamma + d_gamma) + p pi r^2',
        'parameter': '(p / E) (r / t)^2',

        'note': 'The library uses the document\'s non-dimensional pressure parameter and NOT its '
                'd_gamma curve, because Figure 4-5 is a figure and reading values off it would be '
                'worse provenance than saying so. What the library carries instead is a saturating '
                'recovery of the lost knockdown with the right shape and no published points '
                'behind it. Rev 2 warns that applying its d_gamma data to other configurations or '
                'alongside less conservative knockdown factors can produce unconservative designs, '
                'and the same warning applies to a substitute curve. Closing this needs the '
                'digitised figure or the data behind it.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Thermal: published constants and optical properties -- #
# ------------------------------------------------------------------------------------------------ #

# A flat plate normal to the sun with no other load reaches (alpha/eps x G / sigma)^0.25. Every term
# is a published constant or a published property, so the equilibrium temperature is a closed-form
# check on the radiation implementation and on the optical property table together.
THERMAL_EQUILIBRIUM = {

    'solar constant': {
        'source': 'ASTM E490 solar spectral irradiance, total solar irradiance at 1 AU',
        'kind': 'measured',
        'level': 'hardware',
        'value': 1361.0,    # [W/m^2]
        'note': 'The measured total solar irradiance at one astronomical unit. It varies by about '
                '0.1 per cent over a solar cycle, which is far below anything this repository '
                'resolves.'},

    'Stefan-Boltzmann constant': {
        'source': 'CODATA 2018, exact by the 2019 SI redefinition',
        'kind': 'measured',
        'level': 'hardware',
        'value': 5.670374419e-8,    # [W/m^2 K^4]
        'note': 'Exact by definition since the 2019 SI revision, so an implementation that '
                'disagrees is simply wrong rather than approximate.'},

    'white paint equilibrium': {
        'source': 'NASA-HDBK-2001 optical properties, with the equilibrium computed from them',
        'kind': 'derived',
        'level': 'standard',
        'absorptivity': 0.20,
        'emissivity': 0.88,
        'equilibrium': 271.8,    # [K]
        'note': 'A flat plate normal to the sun at 1 AU with no other heat load. The check is on '
                'the fourth-power balance and the property table together, and it is a standard '
                'level check because the properties are tabulated rather than measured here.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Fluids: exact relations and property ground truth -- #
# ------------------------------------------------------------------------------------------------ #

# Fluid systems is the one domain that already had external ground truth before this directory
# existed, because REFPROP and CoolProp are independent implementations of measured equations of
# state. A property lookup that agrees with them is validated in a way nothing else here is.
FLUID_RELATIONS = {

    'Joukowsky surge': {
        'source': 'Joukowsky 1898, and every water hammer text since. dP = rho a dV',
        'kind': 'derived',
        'level': 'standard',
        'formula': 'dP = rho a dV',
        'note': 'Exact for instantaneous valve closure and an upper bound for any real closure. '
                'A tool that exceeds it has an error rather than a conservative answer.'},

    'water at standard conditions': {
        'source': 'IAPWS-95 through REFPROP or CoolProp, both independent implementations',
        'kind': 'measured',
        'level': 'hardware',
        'temperature': 293.15,    # [K]
        'pressure': 101325.0,     # [Pa]
        'density': 998.2,         # [kg/m^3]
        'note': 'The property backend is itself the external reference, which is why this domain '
                'started ahead of the others. The check is that the repository calls it correctly '
                'rather than that the equation of state is right.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Measured throat heat flux -- #
# ------------------------------------------------------------------------------------------------ #

# The nearest thing to an anchor found for the heat transfer side. Not a single case to reproduce,
# but a measured range that a computed peak flux has to fall inside to be credible.
#
# This is a bounding check rather than a validation. It can catch a result that is wrong by an order
# of magnitude and it cannot catch one that is wrong by fifty per cent, which is roughly the size of
# the disagreement that started this directory.
THROAT_HEAT_FLUX = {

    'measured range, open literature': {
        'source': 'Pizzarelli et al., Overview and analysis of the experimentally measured throat '
                  'heat transfer in liquid rocket engine thrust chambers, Acta Astronautica 184 '
                  '(2021) 46, and the accompanying dataset in Data in Brief; plus individual test '
                  'campaign values surfaced alongside it. Accessed 08 August 2026',
        'kind': 'measured',
        'level': 'hardware',
        'lower': 18.0e6,    # [W/m^2]
        'upper': 54.0e6,    # [W/m^2]
        'anchorPoint': {'flux': 54.0e6, 'chamberPressure': 41.4e5, 'mixtureRatio': 6.0,
                        'note': 'a specific test configuration, hydrogen at 41.4 bar'},
        'note': 'The survey collects roughly 500 experimental points from hot-fire tests. The band '
                'quoted here spans individual reported values: 18 MW/m^2 as a maximum in one '
                'campaign, 54 MW/m^2 at the throat in another at 41.4 bar and a mixture ratio of '
                '6.0. The full dataset was not retrievable, so this is the range rather than a '
                'distribution, and the two endpoints are different propellants at different scales '
                'and pressures. Use it to bound, not to validate.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Turbopumps -- #
# ------------------------------------------------------------------------------------------------ #

# The RS-25 turbopumps are the best documented in the open literature, and unusually for this
# repository the published data includes shaft speed AND shaft power, which between them close the
# loop on a pump model.
TURBOPUMPS = {

    'RS-25 HPFTP': {
        'source': 'https://en.wikipedia.org/wiki/RS-25 and the NASA SSME orientation training '
                  'material it cites, accessed 09 August 2026',
        'kind': 'specification',
        'level': 'hardware',
        'propellant': 'LH2',
        'density': 71.0,               # [kg/m^3]
        'shaftSpeed': 35360.0,         # [rpm]
        'shaftPower': 51.45e6,         # [W], 69 000 hp
        'dischargePressure': 41.0e6,   # [Pa], approximately 6000 psia
        'stages': 3,
        'note': 'The stage count is the critical field. A pump model given the overall specific '
                'speed of a multi-stage pump underpredicts its efficiency badly, because each '
                'stage runs at a much higher specific speed than the machine as a whole. Given '
                'one stage this library overpredicts the shaft power by 50 per cent; given the '
                'published three it overpredicts by 9 per cent.'},

    'RS-25 HPOTP': {
        'source': 'as HPFTP, accessed 09 August 2026',
        'kind': 'specification',
        'level': 'hardware',
        'propellant': 'LOX',
        'shaftSpeed': 36000.0,         # [rpm]
        'shaftPower': 18.64e6,         # [W], 25 000 hp
        'note': 'Carried for the shaft speed rather than for a power comparison, because the '
                'HPOTP drives a preburner boost stage on the same shaft and its published power '
                'is not a single pump duty.'},

    'RS-25 LPFTP': {
        'source': 'as HPFTP, accessed 09 August 2026',
        'kind': 'specification',
        'level': 'hardware',
        'propellant': 'LH2',
        'shaftSpeed': 5150.0,          # [rpm]
        'inletPressure': 0.2e6,        # [Pa]
        'dischargePressure': 1.9e6,    # [Pa]
        'geometry': 'axial',
        'note': 'Retained as the case that shows where the classical specific speed to geometry '
                'mapping does NOT apply. At a dimensionless specific speed of 0.285 the classical '
                'chart says radial, and the real machine is axial. A rocket boost pump is axial '
                'for cavitation reasons rather than for specific speed reasons, and reading the '
                'industrial chart across gets it wrong.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Start and shutdown transients -- #
# ------------------------------------------------------------------------------------------------ #

# The RS-25 is the only large liquid engine whose start and shutdown sequences are published to the
# hundredth of a second, which makes this the anchor for the whole ignitionAndStart sub-domain.
#
# Everything here is quoted from Biggs and nothing is inferred. The numbers themselves live in
# ignitionUtils as SSME_START_SEQUENCE, SSME_SHUTDOWN_LIMITS and SSME_SEQUENCE_TOLERANCE; this entry
# records where they came from and what they can and cannot validate.
START_SEQUENCES = {

    'RS-25': {
        'source': 'Biggs, Space Shuttle Main Engine: The First Ten Years, part 3, Start and '
                  'Shutdown. Originally presented at the Liquid Rocket Propulsion History '
                  'Colloquium, AAS Annual Meeting, November 1989, published in History of Liquid '
                  'Rocket Engine Development in the United States 1955-1980, AAS History Series '
                  'volume 13, pages 69-122. Retrieved from enginehistory.org, accessed 09 August '
                  '2026',
        'kind': 'specification',
        'level': 'hardware',

        'timeToRatedPower':   5.0,       # [s]
        'mainChamberPrime':   1.5,       # [s]
        'primeSpacing':       0.1,       # [s], the three combustors prime about a tenth apart
        'damagingTimingError': 0.1,      # [s]
        'damagingValveError': 2.0,       # [per cent], and one per cent for the OPOV
        'speedCheckTime':     1.25,      # [s]
        'speedCheckThreshold': 4600.0,   # [rpm]

        'thrustDecayLimit':   700.0e3,   # [lbf/s], an orbiter structural limit, not an engine one
        'oxidiserCloseRate':  45.0,      # [per cent per second]
        'boiloutSafeSpeed':   7000.0,    # [rpm]

        'note': 'What this validates and what it does not. It validates that the sub-domain\'s '
                'sequencing constants are the published ones, and it anchors the statement that '
                'the design prime spacing and the damaging timing error are the same number, '
                'which is the sub-domain\'s central claim about how little margin a start sequence '
                'has. It does NOT validate the accumulation model, because the source gives no '
                'ignition delay and no overpressure. A start sequence is a schedule; this '
                'repository models the accumulation that a schedule controls, and the two meet '
                'only qualitatively.',

        'boundingUse': 'The thrust decay limit is a vehicle structural limit and it transfers to '
                       'no other vehicle. It is carried as the one published example of a decay '
                       'rate being owned by the airframe rather than the engine, which is the '
                       'point the shutdown document makes.'},
}

# Hypergolic ignition delay, from drop test and impinging jet measurements at ambient conditions.
#
# Carried as a range rather than a value because the scatter between methods is larger than the
# scatter within any one of them. The liquid phase induction time is tens of microseconds; the
# observed delay is milliseconds, and the difference is physical transport and heat transfer, which
# is why the delay depends on the injector rather than only on the chemistry.
IGNITION_DELAYS = {

    'MMH/NTO': {
        'source': 'Comparative reviews of conventional and green hypergolic propellant ignition '
                  'delays at ambient conditions, drop test and impinging jet methods; searched 09 '
                  'August 2026',
        'kind': 'measured',
        'level': 'standard',
        'lower': 1.0,     # [ms]
        'upper': 5.0,     # [ms]
        'representative': 1.45,   # [ms], a commonly cited controlled drop test value
        'note': 'The primary source was not directly retrievable and the values are taken from a '
                'search summary of it, which is weaker than the RS-25 sequence above and is '
                'recorded as such. The sub-domain uses the range to bound the permitted start '
                'flow, and that use is insensitive to which end of the range is taken because the '
                'competing case, a spark igniter at tens of milliseconds, is an order of magnitude '
                'away.'},
}

# ------------------------------------------------------------------------------------------------ #
# -- Stability rating devices -- #
# ------------------------------------------------------------------------------------------------ #

# What a stability rating perturbation has to be, and which device can deliver it.
#
# This is the sourced half of stability rating. The unsourced half, the damp criterion that decides
# a pass, is registered in UNVALIDATED as stabilityDampCriterion.
STABILITY_RATING = {

    'MSFC pulse gun development': {
        'source': 'Osborne, Hulka, McCay, Casiano and Dumbacher, Development and Testing of Pulse '
                  'Guns for Combustion Instability Testing, AIAA Propulsion and Energy Forum and '
                  'Exposition 2021, NASA Marshall Space Flight Center. '
                  'https://ntrs.nasa.gov/api/citations/20210017842, accessed 09 August 2026',
        'kind': 'measured',
        'level': 'hardware',

        'testCount': 44,
        'testChamberPressure': 2300.0,          # [psig], gaseous nitrogen
        'overpressureLower': 0.37,              # [-] zero to peak, as a fraction of mean pressure
        'overpressureUpper': 0.58,              # [-]
        'bestBreechDiameter': 0.0102,           # [m], 0.40 inch
        'bestCharge': 15.5,                     # [grains] of gunpowder
        'burstDiskRating': 24000.0,             # [psid]

        'pulseGunDiameterLimit': 0.3048,        # [m], about 12 inches
        'instabilityFluxMultiplierInjector': (5.0, 10.0),
        'instabilityFluxMultiplierThroat': 2.0,

        'note': 'The overpressure band is stated by the source as adequate for typical combustion '
                'stability rating, so the lower end is used as a floor rather than as a '
                'specification. The diameter limit is stated as probable rather than exact: above '
                'roughly 12 inches a pulse gun may be unable to produce an adequate response and a '
                'bomb becomes necessary, which is a procurement and handling consequence more than '
                'a technical one.',

        'crossDomain': 'The flux multipliers are the reason a stability rating is a hardware '
                       'survival requirement rather than a performance measurement. '
                       'combustionDevices computes a cooling circuit that does not close with '
                       'comfortable margin at nominal flux; at five to ten times nominal near the '
                       'injector face there is no circuit at all.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- Launch vehicles -- #
# ------------------------------------------------------------------------------------------------ #

# Published stage masses for real launch vehicles, which is the only external anchor the
# vehicleArchitecture domain has.
#
# What these validate is the BOOKKEEPING rather than any model: each stage lifts everything above
# it, and getting that wrong produces a plausible number rather than an obvious error. Put the
# published masses and engine performance through the rocket equation and the answer has to land
# near the delta-V a real mission needs, or the accounting is wrong.
#
# They do not validate a mass estimating relationship, because these are the answers rather than
# the inputs. A domain that predicted these masses from a payload requirement would be validated by
# them; this one takes them as given.
LAUNCH_VEHICLES = {

    'Falcon 9 Block 5': {
        'source': 'https://en.wikipedia.org/wiki/Falcon_9_Block_5, accessed 09 August 2026, and '
                  'the SpaceX specifications it cites',
        'kind': 'specification',
        'level': 'hardware',
        'propellant': 'LOX/RP-1',

        'stageOneDryMass':    22200.0,     # [kg]
        'stageOneGrossMass':  433100.0,    # [kg]
        'stageOneOxidiser':   287400.0,    # [kg]
        'stageOneFuel':       123500.0,    # [kg]
        'stageOneThrust':     7607.0e3,    # [N] sea level, nine engines
        'stageOneEngineCount': 9,

        'stageTwoDryMass':    4000.0,      # [kg]
        'stageTwoGrossMass':  111500.0,    # [kg]
        'stageTwoOxidiser':   75200.0,     # [kg]
        'stageTwoFuel':       32300.0,     # [kg]
        'stageTwoThrust':     934.0e3,     # [N] vacuum

        'payloadToLeoExpended': 22800.0,   # [kg] 28.5 degree inclination
        'payloadToLeoReusable': 18500.0,   # [kg]
        'payloadToGtoExpended': 8300.0,    # [kg]
        'payloadToGtoReusable': 5500.0,    # [kg]

        'note': 'The mixture ratios implied by the tabulated propellant loads are 2.327 and 2.328 '
                'on the two stages, which agree to three figures and are a useful check that the '
                'four masses were read from a consistent source. The structural coefficients '
                'against GROSS mass are 0.0513 and 0.0359. Note the denominator: some sources use '
                'propellant mass and the two differ by enough to change a design.',

        'engineNote': 'Specific impulse is NOT published in the same source and the values used in '
                      'this repository, about 297 s effective for the first stage and 348 s for '
                      'the second, are widely cited rather than sourced alongside the masses. They '
                      'carry lower confidence than the masses do, and the delta-V check is '
                      'therefore a check to a few per cent rather than to one.',

        'reuseNote': 'The expended and reusable payloads come from the same source, so their '
                     'RATIO is a sourced quantity even though neither is a measurement this '
                     'repository can reproduce. Recovery costs 18.9 per cent of low Earth orbit '
                     'payload and 33.7 per cent of geostationary transfer payload, and the '
                     'difference between those two is the recovery propellant being a larger '
                     'share of a smaller margin.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- Mechanism standards -- #
# ------------------------------------------------------------------------------------------------ #

# NASA-STD-5017B, read directly from the standard rather than from a summary of it.
#
# That distinction earned its keep immediately. A search summary of this same standard reported the
# required torque margin as 1.0 or greater. The standard says a margin greater than or equal to
# ZERO indicates the requirement is met, because the reserve is inside the safety factors rather
# than applied on top of the result. Building the library on the summary would have made every
# mechanism in it look twice as marginal as it is.
MECHANISM_STANDARDS = {

    'NASA-STD-5017B': {
        'source': 'NASA-STD-5017B, Design and Development Requirements for Mechanisms, approved '
                  '06 December 2022. Read from the standard PDF at '
                  'https://ntrs.nasa.gov/api/citations/20220014671, accessed 09 August 2026',
        'kind': 'specification',
        'level': 'standard',

        'marginEquation': 'margin = T_avail / (sum FSf Tf + sum FSv Tv + sum FSa Ta) - 1',
        'requiredMargin': 0.0,

        'torqueMarginFactors': {
            'theory or analysis':        {'variable': 3.00, 'fixed': 1.50, 'acceleration': 1.25},
            'development test':          {'variable': 2.50, 'fixed': 1.35, 'acceleration': 1.15},
            'qualification test':        {'variable': 2.50, 'fixed': 1.35, 'acceleration': 1.15},
            'lot acceptance test':       {'variable': 2.50, 'fixed': 1.35, 'acceleration': 1.15},
            'acceptance test, ambient':  {'variable': 2.50, 'fixed': 1.35, 'acceleration': 1.15},
            'acceptance test, extremes': {'variable': 2.00, 'fixed': 1.25, 'acceleration': 1.10},
            'one spring out':            {'variable': 1.00, 'fixed': 1.00, 'acceleration': 1.00},
        },

        'bearingContactAllowable': {
            '440C':  {'quiet': 2310.0e6, 'nonQuiet': 2760.0e6},
            '52100': {'quiet': 2480.0e6, 'nonQuiet': 2960.0e6},
            'M50':   {'quiet': 2480.0e6, 'nonQuiet': 2960.0e6},
            'M62':   {'quiet': 3790.0e6, 'nonQuiet': 4070.0e6},
        },

        'requirements': {
            'DDMR 9':  'Torque margin applied under worst-case conditions throughout life',
            'DDMR 10': 'Torque multipliers meet margin at BOTH input and output',
            'DDMR 11': 'All torque margins verified during acceptance test at the highest '
                       'possible level of assembly',
            'DDMR 12': 'Static torque margin greater than zero within the full range of motion',
            'DDMR 13': 'Dynamic torque margin greater than zero',
            'DDMR 14': 'Holding torque margin greater than zero at the specified positions',
            'DDMR 29': 'The mechanism remains functional after exposure to stall at any point',
            'DDMR 30': 'Non-jamming mechanical stops where over-travel would be detrimental',
            'DDMR 31': 'Positive margin with full design factors under worst-case transient loads '
                       'from mechanical stop impact',
        },

        'correctionNote': 'A web search summary of this standard reported the required margin as '
                          '1.0 or greater. The standard itself states that a margin greater than '
                          'or equal to zero indicates the requirements are met, and that setting '
                          'the safety factors to unity represents the torque at which no reserve '
                          'is available. Reading the standard rather than the summary changed '
                          'every margin verdict in this domain.',

        'scopeNote': 'The standard is explicit that torque margin does NOT apply to mechanisms '
                     'required to provide a specific value within a narrow tolerance rather than '
                     'a minimum, and it names an ejection mechanism requiring a specific '
                     'separation velocity as an example. That is exactly the SeparationSystem '
                     'case, which is why that class computes velocities and clearances rather '
                     'than margins.',

        'holdingNote': 'For holding margin the available torque is the INTENTIONAL holding torque '
                       'only. The standard excludes incidental, unreliable and uncharacterised '
                       'contributors such as joint friction, harness bending and blanket rubbing, '
                       'which is the opposite of what a conservative analyst might assume.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- Wire gauge -- #
# ------------------------------------------------------------------------------------------------ #

# The American Wire Gauge definition, which is exact rather than tabulated.
#
# 36 AWG is exactly 0.005 inches and each gauge step multiplies the diameter by the 39th root of 92.
# Combined with the standard copper resistivity that makes every wire resistance in the
# electricalPower library a computed quantity, and it reproduces published resistance tables to
# four figures across the whole range.
#
# This is one of very few places in this repository where a validation is exact rather than
# bounded, and it is worth having for that reason: it anchors the voltage drop calculation, which
# is the calculation the domain's central result rests on.
WIRE_GAUGE = {

    'AWG definition': {
        'source': 'The American Wire Gauge definition, and the standard annealed copper '
                  'resistivity of 1.724e-8 ohm m at 20 C. Both are long-established standard '
                  'values rather than a single retrievable document',
        'kind': 'specification',
        'level': 'standard',

        'referenceGauge':    36,
        'referenceDiameter': 0.127e-3,     # [m], 0.005 inches exactly
        'ratio':             92.0,
        'steps':             39.0,
        'copperResistivity': 1.724e-8,     # [ohm m] at 20 C

        # published resistance per kilometre at 20 C, for the computed values to reproduce
        'publishedResistance': {
            10: 3.277,     # [ohm/km]
            12: 5.211,
            14: 8.286,
            16: 13.17,
            18: 20.95,
            20: 33.31,
            22: 52.96,
            24: 84.22,
        },

        'note': 'The computed values reproduce these to four significant figures, which is the '
                'tightest agreement anywhere in this repository. That matters because the '
                'electricalPower domain concludes that voltage drop rather than ampacity chooses '
                'the wire gauge on a launch vehicle, and voltage drop is a pure resistance '
                'calculation: the exact half of the comparison is the half the conclusion rests '
                'on, and the representative half, ampacity, would have to be wrong by several '
                'gauge steps to overturn it.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- Explosives siting, read from DESR 6055.09 and NASA-STD-8719.12A -- #
# ------------------------------------------------------------------------------------------------ #

# The groundSystemsAndOperations anchor, and it is a strong one: both the equivalence table and the
# K factor table were read from the standards themselves rather than from a summary.
#
# Reading them turned up two things a summary would not have. The first is that the widely quoted
# sixty per cent equivalence for LO2/LH2 is not the siting rule at all. The standard's rule is the
# larger of a sublinear term and a flat fourteen per cent, and it is the sublinear term that governs
# for anything smaller than a heavy lift core stage.
#
# The second is a unit inconsistency inside the standard, recorded below.
EXPLOSIVE_SITING = {

    'DESR-6055.09': {
        'source': 'DESR 6055.09, Defense Explosives Safety Regulation, Edition 1 Change 1, '
                  '23 February 2024, Volume 5 Enclosure 4 Table V5.E4.T5 and footnote f. Read '
                  'from the PDF at https://www.denix.osd.mil/ddes/denix-files/sites/32/2021/08/'
                  'DESR-6055.09-Edition1.pdf, accessed 10 August 2026. Reproduced identically as '
                  'NASA-STD-8719.12A Table 5-29, and its K factors as Table E-1, read from '
                  'https://standards.nasa.gov/sites/default/files/standards/NASA/A/2/'
                  'nasa-std-871912a_with_change_2.pdf',
        'kind':  'specification',
        'level': 'standard',

        # Hopkinson-Cranz cube root scaling, in the units the standard is written in.
        'scalingLaw': 'd = K * W ** (1/3), d in feet, W in pounds of TNT equivalent',

        'kFactors': {
            'lungRupture':               {'k':  1.79, 'psi': 386.9},
            'lungRuptureThreshold':      {'k':  3.33, 'psi': 107.1},
            'eardrum99':                 {'k':  3.90, 'psi':  74.4},
            'barricadedIntermagazine':   {'k':  6.00, 'psi':  27.0},
            'eardrum50':                 {'k':  8.00, 'psi':  15.0},
            'barricadedIntraline':       {'k':  9.00, 'psi':  12.0},
            'unbarricadedIntermagazine': {'k': 11.00, 'psi':   8.0},
            'unbarricadedIntraline':     {'k': 18.00, 'psi':   3.5},
            'publicTrafficRoute':        {'k': 24.00, 'psi':   2.3},
            'publicTrafficRouteLarge':   {'k': 30.00, 'psi':   1.7},
            'inhabitedBuilding':         {'k': 40.00, 'psi':   1.2},
            'inhabitedBuildingRelaxed':  {'k': 50.00, 'psi':   0.9},
        },

        # Range launch column. The static test stand column is lower for two entries, because a
        # stand can be built to keep the propellants apart in a way a vehicle cannot.
        'equivalence': {
            'LO2/RP-1':       {'rangeLaunch': 0.20, 'staticTest': 0.10,
                               'breakMass': 226795.0, 'excessFraction': 0.10},
            'IRFNA/UDMH':     {'rangeLaunch': 0.10, 'staticTest': 0.10},
            'N2O4/UDMH+N2H4': {'rangeLaunch': 0.10, 'staticTest': 0.05},
            'N2O4/PBAN':      {'rangeLaunch': 0.15, 'staticTest': 0.15},
            'nitromethane':   {'rangeLaunch': 1.00, 'staticTest': 1.00},
        },

        'hydrogenRule': {
            'form':             'max(8 * W ** (2/3), 0.14 * W), W in pounds',
            'sublinearCoefficient': 8.0,
            'flatFraction':     0.14,
            'crossoverPounds':  186588.92,
            'crossoverKg':      84635.31,
        },

        'correctionNote': 'The sixty per cent TNT equivalence commonly quoted for LO2/LH2 is a '
                          'yield figure from the Project PYRO test series and an evaluation of '
                          'shuttle on-pad operations. It is NOT the siting rule. The standard '
                          'sites launch vehicles on the larger of 8 W**(2/3) and fourteen per '
                          'cent, and below 186,589 lb the sublinear term governs, which makes the '
                          'effective fraction rise as the load falls. Building the library on the '
                          'sixty per cent figure would have overstated every distance by a factor '
                          'of about three for a small stage and understated the shape of the rule '
                          'entirely.',

        'unitNote': 'The standard prints the hydrogen rule as 8 W**(2/3) with W in pounds and, in '
                    'brackets, 4.13 Q**(2/3) with Q in kilograms. Those are not the same rule. '
                    'Converting the English form exactly gives 6.147 Q**(2/3), and the two differ '
                    'by a factor of 1.488 with the published metric form the smaller. An analyst '
                    'working natively in SI from the bracketed coefficient therefore gets a '
                    'shorter siting distance than the form the table is built on, which is '
                    'non-conservative. The discrepancy is present in both DESR 6055.09 Edition 1 '
                    'Change 1 and NASA-STD-8719.12A. This library computes in the English form '
                    'and converts, and asserts the discrepancy in a test rather than silently '
                    'correcting it.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- Entry environment: Allen-Eggers and Sutton-Graves -- #
# ------------------------------------------------------------------------------------------------ #

# The recoveryAndReusability anchor. Both halves are closed forms rather than measurements, which
# makes this standard level rather than hardware level, but the Sutton-Graves half was pinned
# against published entry cases because its published UNITS are wrong in several sources.
ENTRY_ENVIRONMENT = {

    'Allen-Eggers': {
        'source': 'H. J. Allen and A. J. Eggers, A Study of the Motion and Aerodynamic Heating of '
                  'Ballistic Missiles Entering the Earth Atmosphere at High Supersonic Speeds, '
                  'NACA Report 1381, 1958. Relations reproduced from the NASA TFAWS 2012 '
                  'aerothermodynamics course notes, '
                  'https://tfaws.nasa.gov/TFAWS12/Proceedings/Aerothermodynamics%20Course.pdf, '
                  'accessed 10 August 2026',
        'kind': 'closed form',
        'level': 'standard',

        'velocityProfile': 'V(rho) = V_e exp(-rho H / (2 beta sin|gamma|))',

        'peakDeceleration': 'a_max = V_e**2 sin|gamma| / (2 e H), INDEPENDENT of beta',
        'peakDecelerationVelocityFraction': 0.6065306597126334,   # exp(-1/2)
        'peakDecelerationDensity': 'rho = beta sin|gamma| / H',

        'peakHeatingVelocityFraction': 0.8464817248906141,        # exp(-1/6)
        'peakHeatingDensity': 'rho = beta sin|gamma| / (3 H)',
        'peakHeatFluxScaling': 'q_max ~ sqrt(beta sin|gamma| / Rn) V_e**3',
        'heatLoadScaling':     'Q ~ V_e**2 sqrt(pi beta H / (Rn sin|gamma|))',

        'altitudeSeparation': 'h_q - h_g = H ln(3), exactly, for every entry',

        'correctionNote': 'The course notes state that peak heating sits at about 1.1 times the '
                          'altitude of peak deceleration. That RATIO holds only for an orbital '
                          'entry, where the deceleration peak is high enough that the separation '
                          'is a tenth of it. The separation itself is H ln(3), about 7.9 km, and '
                          'it is the same for every entry of every vehicle. On a booster returning '
                          'from a lofted suborbital trajectory the peaks are near 16 and 24 km and '
                          'the ratio is 1.5 rather than 1.1. This library reports the separation.',

        'scopeNote': 'The solution assumes a constant flight path angle, an exponential '
                     'atmosphere and no lift. It is a shape rather than a trajectory: which '
                     'quantity peaks first, what each depends on, and which of them is '
                     'independent of the vehicle. A single scale height is a coarse fit at the '
                     '40 to 70 km altitudes where an orbital entry peaks.'},

    'Sutton-Graves': {
        'source': 'K. Sutton and R. A. Graves, A General Stagnation Point Convective Heating '
                  'Equation for Arbitrary Gas Mixtures, NASA TR R-376, 1971. Constant read from '
                  'the NASA TFAWS 2012 aerothermodynamics course notes',
        'kind': 'correlation',
        'level': 'bounded',

        'equation': 'q = k sqrt(rho / Rn) V**3',
        'constantEarth': 1.7415e-4,

        'unitNote': 'The units on this constant are quoted inconsistently and it matters by four '
                    'orders of magnitude. Several sources state that the expression returns W/cm2 '
                    'with density in kg/m3, nose radius in metres and velocity in m/s. Reproducing '
                    'published entry cases shows the raw expression is W/m2: Stardust at 12.6 km/s '
                    'with a 0.23 m nose radius gives 1,027 W/cm2 against a published peak '
                    'convective heating around 1,200, and Apollo at 11.1 km/s with a 4.69 m radius '
                    'gives 196 against a published convective component of 200 to 250. Read as '
                    'W/cm2 both are absurd by 1e4. The library works in W/m2 and converts, and a '
                    'test asserts the two cases rather than the units statement.',

        'boundedNote': 'This is BOUNDED rather than validated: the two cases bracket the '
                       'correlation to within tens of per cent, and the densities used are read '
                       'off a standard atmosphere at the published peak heating altitudes rather '
                       'than taken from the flight reconstructions. It is enough to fix the units '
                       'convention, which is what it was done for, and not enough to claim the '
                       'correlation itself is reproduced.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- Inspection capability, read from MIL-HDBK-1823A -- #
# ------------------------------------------------------------------------------------------------ #

# The manufacturingAndAssembly anchor. The probability of detection model and the demonstration
# sizes were read from the handbook itself.
#
# The distinction that reading it settled is between a90 and a90/95, which are used
# interchangeably in casual discussion and are different kinds of number. a90 is a property of the
# inspection. a90/95 is a confidence bound on an ESTIMATE of a90, so it depends on how many
# specimens the demonstration used, and the handbook notes it has become a de facto design
# criterion. The size a programme designs to is therefore partly a statement about how many
# specimens somebody paid for.
INSPECTION_CAPABILITY = {

    'MIL-HDBK-1823A': {
        'source': 'MIL-HDBK-1823A, Nondestructive Evaluation System Reliability Assessment, '
                  '7 April 2009. Section 4.5.2.2 for the demonstration sizes and appendix G for '
                  'the model. Read from the PDF at https://statistical-engineering.com/'
                  'wp-content/uploads/2017/10/MIL-HDBK-1823A2009.pdf, accessed 10 August 2026',
        'kind':  'specification',
        'level': 'standard',

        # The log-odds link, one of the four generalised linear model links the handbook lists
        # alongside probit, complementary log-log and log-log.
        'model':      'log( POD / (1 - POD) ) = ( log(a) - mu ) / sigma',
        'linkFunctions': ['logit', 'probit', 'cloglog', 'loglog'],

        'a50': 'the flaw size having 50 per cent probability of detection',
        'a90': 'the flaw size having 90 per cent probability of detection',
        'a90over95': 'the 95 per cent confidence bound on the estimate of a90',

        # logit(0.9) = log(9), so a90 / a50 = 9 ** sigma exactly.
        'logitAtNinety': 2.1972245773362196,

        # Section 4.5.2.2.
        'minimumHitMissTargets': 60,
        'minimumSignalTargets':  40,
        'unflawedSiteRatio':     3,
        'preciseHitMissTargets': 120,

        'confidenceNote': 'a90 is a property of the inspection and a90/95 is a confidence bound on '
                          'an estimate of it, so a90/95 falls as the demonstration grows for the '
                          'same technique. The handbook states that a90/95 has become a de facto '
                          'design criterion and that 120 binary inspection opportunities give a '
                          'significantly more precise a50 and therefore a smaller a90/95 than the '
                          '60 target minimum. The flaw size a programme designs to is therefore '
                          'partly a statement about how many specimens somebody paid for, which is '
                          'not how a design criterion is usually understood.',

        'targetSizingNote': 'The handbook records a change of practice: target sizes were once '
                            'spaced uniformly on a log scale and the current recommendation is '
                            'uniform Cartesian spacing, because a90/95 is the criterion and the '
                            'ninetieth percentile is therefore the part of the curve worth '
                            'estimating precisely. It also warns that demonstrations tend to '
                            'contain too many large targets, because small ones are hard to make.',

        'scopeNote': 'The model is the standard and it is exact. The a50 and sigma values in this '
                     'library are representative of a method rather than of a qualified procedure, '
                     'and are registered as unvalidated. The handbook is explicit that geometry, '
                     'material, surface finish and access all move them.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- Range safety criteria, read from 14 CFR Part 450 -- #
# ------------------------------------------------------------------------------------------------ #

# The rangeSafetyAndFTS anchor, and the strongest kind available to that domain: the criteria are
# not a model of anything, they are the numbers a launch is licensed against.
#
# Two things are worth carrying out of reading the regulation rather than a summary of it.
#
# Collective and individual risk are SEPARATE tests and both apply. A launch can meet the
# collective criterion by spreading a small risk thinly over a large population and still fail the
# individual one for the person nearest the trajectory. The individual limit exists to stop exactly
# that trade.
#
# And 450.145's design reliability of 0.999 at 95 per cent confidence cannot be demonstrated by
# test. The zero-failure binomial says it takes 2,994 successful firings of a single-use ordnance
# system, so the claim is argued from design rather than demonstrated.
RANGE_SAFETY_CRITERIA = {

    '14-CFR-450': {
        'source': '14 CFR Part 450, Launch and Reentry License Requirements. Section 450.101 for '
                  'the launch safety criteria and 450.145 for the highly reliable flight safety '
                  'system, read from https://www.law.cornell.edu/cfr/text/14/450.101 and '
                  'https://www.law.cornell.edu/cfr/text/14/450.145, accessed 10 August 2026',
        'kind':  'regulation',
        'level': 'standard',

        'launchCriteria': {
            'publicCollective':       {'limit': 1.0e-4, 'measure': 'expected casualties'},
            'neighbouringCollective': {'limit': 2.0e-4, 'measure': 'expected casualties'},
            'publicIndividual':       {'limit': 1.0e-6, 'measure': 'probability of casualty'},
            'neighbouringIndividual': {'limit': 1.0e-5, 'measure': 'probability of casualty'},
            'aircraft':               {'limit': 1.0e-6, 'measure': 'probability of impact'},
        },

        'flightSafetyReliability': 0.999,
        'flightSafetyConfidence':  0.95,

        # ln(0.05) / ln(0.999), the zero-failure binomial.
        'zeroFailureTests': 2994.23,

        'demonstrationNote': 'The 0.999 at 95 per cent confidence in 450.145 cannot be '
                             'demonstrated by test. With zero failures in n trials the lower '
                             'confidence bound on reliability is (1 - C) ** (1/n), so the claim '
                             'needs 2,994 successful firings of a single-use ordnance system. '
                             'Nobody has done that and nobody will: the articles are consumed by '
                             'the test and a lot that size would not be the lot that flies. The '
                             'claim is therefore argued from redundancy, parts history, '
                             'environmental margin and an end-to-end test of the flight article, '
                             'rather than demonstrated by a reliability trial. That is not a '
                             'weakness in the regulation, it is the only available answer.',

        'criteriaNote': 'Collective and individual risk are separate tests and both apply. The '
                        'neighbouring operations personnel limits are looser than the public ones '
                        'by exactly a factor of two on the collective side and ten on the '
                        'individual side, which is the regulation distinguishing people who chose '
                        'to be there from people who did not.',

        'scopeNote': 'These are limits rather than targets. A launch above any of them does not '
                     'get a licence, and there is no engineering argument that trades one against '
                     'another. That is why the classes raise rather than reporting a margin.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- One-sided tolerance limit factors, read from the NIST/SEMATECH e-Handbook -- #
# ------------------------------------------------------------------------------------------------ #

# The aerospaceMaterials anchor, and the one that domain went longest without.
#
# An A-basis or B-basis allowable is `mean - k * s`, and everything the domain says about material
# strength rests on k. Three routes to k are implemented and a test asserted they agreed with each
# other, which is the exact failure this file exists to prevent: three implementations of one
# formula agreeing establishes that the formula was typed the same way three times.
#
# The handbook supplies a fully worked one-sided example with every intermediate printed, so the
# comparison reaches the noncentral t quantile itself rather than stopping at the answer. That
# matters because the answer is a ratio and a compensating pair of errors in delta and in the
# quantile would survive a comparison against k alone.
#
# Two things fall out of reproducing it that were not visible from inside.
#
# The Natrella approximation is NON-CONSERVATIVE against the exact route, everywhere, and by the
# most at the smallest sample the library will accept. A low k is a high allowable, so the
# approximation reports material as stronger than the statistics support. It is small, and it is
# in the wrong direction, and the library therefore defaults to the exact route.
#
# The published MMPDS closed form goes the other way below about twenty specimens and then crosses
# over. The crossover is a fitted curve doing what fitted curves do and the residual above it is
# under a tenth of a per cent, which is well inside anything a real allowable is known to.

TOLERANCE_FACTORS = {

    'NIST-SEMATECH-1.3.5.2': {
        'source': 'NIST/SEMATECH e-Handbook of Statistical Methods, section 7.2.6.3, Tolerance '
                  'intervals for a normal distribution, one-sided case. Read from '
                  'https://www.itl.nist.gov/div898/handbook/prc/section2/prc263.htm, accessed '
                  '13 August 2026. The approximation is attributed there to Natrella, 1963',
        'kind':  'published-specification',
        'level': 'standard',

        # The worked example: 43 silicon wafers, 90 per cent coverage, 99 per cent confidence.
        'sampleSize':  43,
        'coverage':    0.90,
        'confidence':  0.99,

        # Quantiles the handbook uses, to the four figures it prints them to.
        'coverageQuantile':   1.2816,      # [-], z_p at p = 0.90
        'confidenceQuantile': 2.3263,      # [-], z_a at 99 per cent

        # Natrella: k1 = ( z_p + sqrt( z_p**2 - a b ) ) / a
        #           a  = 1 - z_a**2 / ( 2 ( N - 1 ) )
        #           b  = z_p**2 - z_a**2 / N
        'natrellaA':      0.9356,
        'natrellaB':      1.5165,
        'natrellaFactor': 1.8752,

        # Noncentral t: k1 = t( alpha, N - 1, delta ) / sqrt(N),  delta = z_p sqrt(N)
        'noncentrality':      8.4037,
        'noncentralTQuantile': 12.28834,
        'exactFactor':         1.8740,

        'intermediateNote': 'The handbook prints a, b, delta and the noncentral t quantile as well '
                            'as the answer, which is why this entry asserts all four. k is a ratio '
                            'of two computed quantities and a compensating error in the '
                            'noncentrality parameter and in the quantile would reproduce k while '
                            'getting both halves wrong.',

        'directionNote': 'The Natrella approximation returns a smaller k than the exact route at '
                         'every sample size, and a smaller k is a larger allowable. The deviation '
                         'reaches 1.4 per cent on B-basis and 1.0 per cent on A-basis at n = 10, '
                         'which is the smallest sample this library will accept, and falls below '
                         '0.1 per cent by n = 100. It is an approximation erring in the '
                         'unconservative direction, so the exact route is the default and the '
                         'approximation exists to be compared against rather than used.',

        'mmpdsNote': 'The MMPDS closed form is conservative below about twenty specimens, by up to '
                     '0.9 per cent on A-basis at n = 10, and crosses over to non-conservative '
                     'above it by less than 0.07 per cent at worst. Both are far inside the '
                     'uncertainty of any real allowable and neither is a transcription error, '
                     'which is what the comparison was run to rule out.',

        'scopeNote': 'The handbook example is 43 silicon wafers and the library computes material '
                     'allowables. The quantity is identical: a one-sided tolerance limit on a '
                     'normal population is the same statistic whatever was measured, which is why '
                     'a semiconductor worked example validates a metallurgical one. What it does '
                     'not validate is the assumption of normality, the pooling of lots, or any '
                     'knockdown applied afterwards.',

        'assumptionNote': 'The first two of those are now bounded rather than merely named. '
                          'Allowables.compareBasisRoutes runs the same sample through the '
                          'normal-theory route, an order statistic route that assumes no '
                          'distribution, and an ANOVA route that separates within-lot from '
                          'between-lot variance, and reports what each assumption is worth. On the '
                          'six-lot reference sample normality is worth 1.0 per cent of the basis '
                          'value and pooling is worth 1.8 per cent, both in the unconservative '
                          'direction. **That is an internal cross-check and not a validation**: '
                          'the distribution-free route is a different estimator with its own '
                          'conservatism, so the comparison bounds how much the assumption is worth '
                          'rather than measuring an error in it. The knockdown chain remains '
                          'unbounded by anything.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- Smooth pipe friction, from the Princeton Superpipe -- #
# ------------------------------------------------------------------------------------------------ #

# The fluidSystems line pressure drop anchor, and it is not the one that was planned.
#
# The retrofit list called for Crane TP-410 worked examples. TP-410 is not openly available and the
# search for a reproducible worked example from it failed, so the anchor is the thing TP-410's
# friction chart is itself an approximation to: measured smooth pipe friction from the Princeton
# Superpipe, over 31,000 to 35,500,000 in Reynolds number.
#
# That is a better reference than the one it replaces. A TP-410 example would check that this
# library implements Colebrook the way Crane does. The Superpipe fit checks whether Colebrook is
# right, and the answer is that it is close and consistently low.
#
# **Every method in this library under-predicts measured smooth pipe friction, and the shortfall
# grows with Reynolds number.** A low friction factor is a low pressure drop, so a line sized on it
# has less margin than its number says, by up to three per cent at the top of the range. That is
# small against the other uncertainties in a feed system and it is in the wrong direction, which is
# worth knowing rather than assuming.
#
# The Reynolds numbers a launch vehicle feed line runs at sit near the middle of this range, so the
# figure that matters is the one to two per cent in the 1e5 to 1e7 decade rather than the worst case
# at the top.

FRICTION_FACTOR = {

    'Princeton Superpipe': {
        'source': 'McKeon, Zagarola and Smits, A new friction factor relationship for fully '
                  'developed pipe flow, Journal of Fluid Mechanics 538, 429-443, 2005. Relation '
                  'and error bounds read from the reproduction in Yang and Joseph, Virginia '
                  'Polytechnic / University of Minnesota, https://dept.aem.umn.edu/~./faculty/'
                  'joseph/PL-correlations/docs-ln/S1-JFM-Submission-f-Re-Smooth-Pipe.pdf, '
                  'accessed 13 August 2026',
        'kind':  'measured',
        'level': 'hardware',

        # 1/sqrt(lambda) = 1.930 log10( Re sqrt(lambda) ) - 0.537
        'logSlope':     1.930,
        'logIntercept': 0.537,

        'reynoldsRange':     (3.13e4, 3.55e7),   # [-] the range the fit covers
        'fitError':          1.25,               # [per cent] over the whole range
        'fitErrorHighRange': 0.5,                # [per cent] over 3.0e5 to 1.36e7

        # The classical smooth pipe law the Colebrook equation reduces to at zero roughness, for
        # comparison. The Superpipe work is what moved 2.0 and 0.8 to 1.930 and 0.537.
        #
        # The intercept is usually quoted as 0.8 and the Colebrook equation does not produce 0.8:
        # setting roughness to zero leaves 2 log10( Re sqrt(lambda) / 2.51 ), so the intercept is
        # 2 log10(2.51) = 0.799347. The rounding is in the textbook rather than in the equation and
        # it is worth 0.08 per cent on the intercept, which is nothing next to the 1.930 against
        # 2.0 on the slope.
        'prandtlSlope':     2.0,
        'prandtlIntercept': 0.799347,
        'prandtlInterceptQuoted': 0.8,

        # Deviation of each method in this library from the fit, over the fit's own range.
        'colebrookWorst': -2.91,     # [per cent] at Re = 3.55e7
        'churchillWorst': -2.11,     # [per cent] at Re = 2.96e6
        'haalandWorst':   -2.31,     # [per cent] at Re = 2.48e6

        'directionNote': 'All three methods are low across the whole range and none crosses over. '
                         'A low friction factor is a low pressure drop, so a line sized on one has '
                         'less margin than its number says. The deviation is under one per cent '
                         'below Re = 1e5 and grows monotonically above it.',

        'scopeNote': 'This is a smooth pipe fit and it validates the friction factor only. The '
                     'roughness branch is not anchored by it, and neither are the fitting loss '
                     'coefficients, which are a table rather than a model and remain the largest '
                     'unanchored part of a line pressure drop.'},

    'Hagen-Poiseuille': {
        'source': 'Closed form for fully developed laminar flow in a circular pipe, '
                  'dP = 128 mu Q L / (pi D**4)',
        'kind':  'derived',
        'level': 'standard',

        'formula': 'dP = 128 mu Q L / (pi D**4)',

        'note': 'The only place in this domain where a pressure drop has an exact answer, which '
                'makes it the check on the whole chain rather than on one term. Velocity from mass '
                'flow, Reynolds number, the 64/Re friction factor and the Darcy-Weisbach '
                'assembly all have to be right together to reproduce it, and no tolerance is '
                'needed: the library matches to one part in a million, and the residual is the '
                'density being re-evaluated along the marched line rather than an error.'},

    'Blasius': {
        'source': 'Blasius 1913, the classical smooth pipe correlation, lambda = 0.3164 Re**-0.25',
        'kind':  'derived',
        'level': 'standard',

        'formula':       'lambda = 0.3164 * Re ** -0.25',
        'reynoldsRange': (1.0e4, 9.0e4),         # [-] the interval McKeon et al. quote it over
        'colebrookWorst': -2.76,                 # [per cent] at Re = 1.68e4

        'note': 'Carried as the low Reynolds bracket, where the Superpipe fit is below its own '
                'range. McKeon et al. state their 2005 form agrees with Blasius to two per cent '
                'over 1e4 to 9e4; this library sits 2.8 per cent below Blasius at worst over the '
                'same interval, and below it almost everywhere, which is the same direction as the '
                'Superpipe comparison at the other end of the range. Blasius is itself a '
                'correlation rather than a measurement, so this brackets rather than validates.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- A specific lithium ion cell, from the manufacturer's datasheet -- #
# ------------------------------------------------------------------------------------------------ #

# The electricalPower anchor. The battery tables in that domain are representative of a CHEMISTRY
# rather than of a part number, which is the right shape for a sizing library and is also a claim
# that nothing checked. This entry is one real cell, so the claim can be checked: a class figure is
# only useful if a real part sits near it and on the conservative side of it.
#
# Two things fall out of the datasheet that are worth more than the numbers.
#
# The two published energy densities both reproduce EXACTLY from the rated capacity and the bare
# cell dimensions, and neither reproduces from the typical capacity. So a specific energy on a cell
# datasheet is built from the rated figure at 20 C, not from the typical figure at 25 C, and taking
# a nameplate energy density and multiplying it by a typical capacity double counts five per cent.
#
# The cell discharges to -20 C and cannot be CHARGED below +10 C. That asymmetry is thirty degrees
# wide, it is not a derating curve but a hard limit, and the library carries only the discharge
# side of it. A vehicle cold-soaked on the pad can run its battery and cannot top it up, which is
# an operational constraint rather than a sizing one and is the kind of thing a chemistry-level
# table cannot express.

BATTERY_CELLS = {

    'Panasonic NCR18650BF': {
        'source': 'Panasonic NCR18650BF cell specifications, read from the manufacturer datasheet '
                  'at https://api.pim.na.industrial.panasonic.com/file_stream/main/fileversion/'
                  '3446, accessed 14 August 2026',
        'kind':  'specification',
        'level': 'hardware',

        'ratedCapacity':      3.200,     # [A h] at 20 C
        'minimumCapacity':    3.250,     # [A h] at 25 C
        'typicalCapacity':    3.350,     # [A h] at 25 C
        'nominalVoltage':     3.6,       # [V]
        'chargeVoltage':      4.20,      # [V], constant current then constant voltage
        'maximumMass':        0.0465,    # [kg] bare cell, without tube

        'gravimetricEnergyDensity': 248.0,   # [W h/kg]
        'volumetricEnergyDensity':  677.0,   # [W h/l]

        'height':   0.06510,     # [m] maximum, bare cell
        'diameter': 0.01824,     # [m] maximum, bare cell

        'chargeTemperatureRange':    (10.0, 45.0),     # [C]
        'dischargeTemperatureRange': (-20.0, 60.0),    # [C]
        'storageTemperatureRange':   (-20.0, 50.0),    # [C]

        'densityBasisNote': 'Both published densities reproduce from the RATED capacity of 3.200 '
                            'A h and not from the typical 3.350. Rated times nominal voltage is '
                            '11.52 W h, which over 46.5 g is 247.7 W h/kg and over the bare cell '
                            'volume of 17.01 mL is 677.2 W h/l. Neither is a coincidence and both '
                            'are asserted, because the difference between the two capacities is '
                            'five per cent and a nameplate energy density multiplied by a typical '
                            'capacity counts it twice.',

        'chargeLimitNote': 'The cell discharges to -20 C and cannot be charged below +10 C. That '
                           'is a hard limit rather than a derating curve, the two ranges differ by '
                           'thirty degrees, and the chemistry tables in electricalPower carry only '
                           'the discharge side. The consequence is operational: a vehicle cold '
                           'soaked on the pad can run its battery and cannot top it up.',

        'scopeNote': 'One cell of one chemistry from one manufacturer. It cannot validate a class '
                     'table and it can say whether the class table is conservative against a '
                     'current part, which is the only question a representative figure has to '
                     'answer. The 200 W h/kg the library carries for lithium ion sits 19 per cent '
                     'below this cell, and a class figure has to cover older and higher rate '
                     'chemistries as well, so conservative is the direction it should err in.'},
}


# ------------------------------------------------------------------------------------------------ #
# -- Rough pipe friction, from Nikuradse's sand-grain experiments -- #
# ------------------------------------------------------------------------------------------------ #

# The other half of the fluidSystems friction anchor. The Princeton Superpipe covers smooth pipe;
# this covers the branch that switches on once relative roughness matters, which is the branch an
# additive-manufactured channel lives in.
#
# Nikuradse glued sifted sand of a known grain size to the inside of six pipes, which is why this is
# the reference: the roughness is not an equivalent value inferred from a pressure drop, it is a
# measured grain diameter. He established that in the fully rough regime the resistance stops
# depending on Reynolds number entirely and becomes a function of r/k alone.
#
# **The check comes out almost exact, and the reason is that it is the same constant twice.** The
# Colebrook equation's 3.7 is Nikuradse's 1.74 re-expressed: taking Colebrook to the fully rough
# limit leaves 2 log10(r/k) + 2 log10(7.4), and 2 log10(7.4) is 1.7385 against the 1.74 Nikuradse
# fitted. Reproducing it therefore validates that the library implements the roughness term as the
# measurement intended rather than establishing anything new about the measurement.
#
# **What this does NOT cover is the transition region**, and that is not a limitation of the data.
# Nikuradse used uniform sand grain, where the resistance dips below the fully rough value before
# rising back to it. Commercial pipe has a distribution of roughness heights and shows no dip, and
# Colebrook fitted commercial pipe. **The two genuinely disagree in the transition and the library
# follows Colebrook**, which is the right choice for drawn tube and the wrong one for a surface that
# really is uniform grains.

ROUGH_PIPE = {

    'Nikuradse sand-grain': {
        'source': 'J. Nikuradse, Laws of Flow in Rough Pipes, NACA TM 1292, November 1950, a '
                  'translation of Stroemungsgesetze in rauhen Rohren, VDI-Forschungsheft 361, '
                  '1933. The fully rough resistance law, stated in the text on page 21 of the '
                  'translation. Read from https://ntrs.nasa.gov/api/citations/19930093938/'
                  'downloads/19930093938.pdf, accessed 15 August 2026',
        'kind':  'measured',
        'level': 'hardware',

        # 1 / sqrt(lambda) = 1.74 + 2 log10(r / k)
        'lawConstant': 1.74,
        'lawSlope':    2.0,

        # The six pipes, from the table headings. The document prints log(r/k) alongside each and
        # they agree with the ratios, which is a free check that these were read correctly.
        'relativeRadii': [15.0, 30.6, 60.0, 126.0, 252.0, 507.0],

        # Colebrook's rough asymptote constant, for comparison with lawConstant.
        'colebrookConstant': 1.73846,      # [-], 2 log10(7.4)

        'equivalenceNote': 'Colebrook taken to the fully rough limit is '
                           '1/sqrt(lambda) = -2 log10(k / (3.7 d)), which for d = 2r is '
                           '2 log10(r/k) + 2 log10(7.4). The 3.7 and the 1.74 are the same '
                           'constant expressed two ways and they agree to 0.09 per cent, so this '
                           'check establishes that the library implements the roughness term '
                           'correctly rather than that Nikuradse was right.',

        'scopeNote': 'The fully rough branch only. Nikuradse used uniform sand grain, whose '
                     'resistance dips below the fully rough value in the transition before rising '
                     'back to it; commercial pipe has a distribution of roughness heights, shows '
                     'no dip, and is what Colebrook fitted. The library follows Colebrook, which '
                     'is right for drawn tube and wrong for a surface that really is uniform '
                     'grains. Nikuradse\'s own tabulation of 1/sqrt(lambda) - 2 log10(r/k) '
                     'approaches 1.74 from ABOVE, starting near 1.95, which is that transition.',

        'roughnessNote': 'k here is a measured sand grain diameter. Every roughness in '
                         'common/materials.py is an equivalent sand-grain roughness inferred from '
                         'pressure drop measurements on real surfaces, which is a different '
                         'quantity that happens to be defined so it can be used in the same '
                         'formula. That substitution is the unvalidated step in any rough pipe '
                         'calculation this repository does, and it is not closed by this entry.'},
}
