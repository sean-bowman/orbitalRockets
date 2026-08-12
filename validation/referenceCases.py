
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
        'calculation': 'MEAN_SPECIFIC_HEAT, the mean metal specific heat over the chill-down range',
        'reason': 'Representative means over roughly 90 to 300 K rather than integrated from '
                  'measured cp curves.',
        'consequence': 'The chill-down mass scales linearly with them. They are deliberately not '
                       'the room-temperature values in common/materials.py, which would overstate '
                       'the stored enthalpy by roughly a third, and a test asserts they stay '
                       'different so the correction is not undone by someone tidying up.',
        'nextStep': 'Integrate NIST cryogenic specific heat curves over the range per material. '
                    'This is tractable and simply has not been done.'},

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
        'nextStep': 'A cell datasheet for the actual part, which turns every one of these into a '
                    'measured curve. This is the most tractable gap in the domain because the '
                    'data is published by every cell manufacturer.'},

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
        'nextStep': 'A datasheet for a specific IMU, which every manufacturer publishes. Same '
                    'shape of gap as the battery cell datasheet in electricalPower and equally '
                    'tractable.'},

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
# What can be checked here is that the implementation reproduces the published formula at stated
# radius-to-thickness ratios. What cannot be checked is the formula itself, because the test scatter
# it was fitted to is not in the document in a form that can be re-fitted. That distinction is the
# difference between the 'standard' and 'hardware' levels.
SHELL_BUCKLING = {

    'NASA SP-8007 knockdown': {
        'source': 'NASA SP-8007, Buckling of Thin-Walled Circular Cylinders, 1968 revision. The '
                  'correlation factor for axially compressed cylinders',
        'kind': 'derived',
        'level': 'standard',
        'formula': 'gamma = 1 - 0.901 (1 - exp(-phi)), phi = (1/16) sqrt(R/t)',
        'points': {100.0: 0.5813, 300.0: 0.4042, 500.0: 0.3217, 1000.0: 0.2238, 1500.0: 0.1791},
        'note': 'Values computed from the published closed form at each radius-to-thickness ratio. '
                'This validates the implementation and cannot validate the correlation, which was '
                'fitted to test scatter the document does not reproduce in re-fittable form. A '
                'knockdown of 0.22 at R/t 1000 means the classical stress overpredicts by a factor '
                'of four and a half, which is the reason the factor exists.'},
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
