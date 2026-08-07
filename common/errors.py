
# -- Error Handling [orbitalRockets common] -- #

'''

The shared exception hierarchy.

EngineeringError is the base for every error raised anywhere in this repository. Each domain
defines its own base as a subclass so that the boxed banner names the domain, and adds its own
domain-specific errors below that.

Every error carries a context dictionary, so a failed calculation reports what went wrong and
what the physical limit was rather than just that it failed.

Author: Sean Bowman
Date:   08/06/2026

'''

from typing import Any, Dict, Optional

#--------------------------------------------------------------------------------------------------------------------------#
# -- Base Error -- #
#--------------------------------------------------------------------------------------------------------------------------#

class EngineeringError(Exception):

    '''

    Base exception class for every error raised anywhere in orbitalRockets.

    All custom exceptions inherit from this class so that a caller can catch the whole family with a
    single except clause when that is what they want, or an individual failure mode when it is not.

    Each domain sets domainLabel on its own base class so the boxed banner names the domain that
    raised: FLUID SYSTEM ERROR, STRUCTURES ERROR, and so on. The label is cosmetic; the hierarchy is
    what matters.

    Attributes:
        message (str): Human-readable error message
        context (dict): Additional context about the error (component, variable values, etc.)

    '''

    domainLabel = 'ENGINEERING'

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):

        '''

        Initialize the exception.

        Args:
            message: Human-readable description of the error
            context: Dictionary containing relevant state information when the error occurred

        '''

        self.message = message
        self.context = context if context is not None else {}

        # Build detailed error message
        fullMessage  = f'\n{"=" * 80}\n'
        fullMessage += f'{self.domainLabel} ERROR\n'
        fullMessage += f'{"=" * 80}\n'
        fullMessage += f'{message}\n'

        if self.context:
            fullMessage += f'\nError Context:\n'
            fullMessage += f'{"-" * 80}\n'
            for key, value in self.context.items():
                fullMessage += f'  {key}: {value}\n'

        fullMessage += f'{"=" * 80}\n'

        super().__init__(fullMessage)

    def getContext(self) -> Dict[str, Any]:

        '''

        Retrieve the error context dictionary.

        '''

        return self.context

#--------------------------------------------------------------------------------------------------------------------------#
# -- Generic Errors -- #
#--------------------------------------------------------------------------------------------------------------------------#

class InvalidInputError(EngineeringError):

    '''

    Exception raised when an input parameter is missing, out of range, or physically nonsensical.

    Common causes:
        - A required configuration key was not supplied
        - A negative diameter, absolute pressure or absolute temperature
        - Downstream pressure above upstream pressure
        - A material or fluid name not in the lookup tables

    '''

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None,
                 parameterName: Optional[str] = None, value: Optional[Any] = None,
                 validRange: Optional[str] = None):

        if context is None:
            context = {}

        if parameterName is not None:
            context['parameterName'] = parameterName
        if value is not None:
            context['value'] = value
        if validRange is not None:
            context['validRange'] = validRange

        super().__init__(message, context)

class ConvergenceFailureError(EngineeringError):

    '''

    Exception raised when an iterative solver fails to converge within its iteration limit.

    Common causes:
        - Incompatible design constraints (a target pressure drop that no diameter can produce)
        - Poor initial guess leading to oscillation
        - The operating point sitting on a discontinuity, most often the onset of choking

    '''

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None,
                 iterations: Optional[int] = None, tolerance: Optional[float] = None,
                 residual: Optional[float] = None):

        if context is None:
            context = {}

        if iterations is not None:
            context['iterations'] = iterations
        if tolerance is not None:
            context['tolerance'] = tolerance
        if residual is not None:
            context['residual'] = residual

        super().__init__(message, context)

class CompatibilityError(EngineeringError):

    '''

    Exception raised when a material, seal or lubricant is incompatible with the service fluid.

    This is a hard error rather than a warning by deliberate choice. Titanium in LOX, aluminum in
    N2O4 above 60 degC, Buna-N in hydrazine, hydrocarbon grease in a GOX system: every one of these
    has destroyed hardware or killed someone, and none of them should be a line you can scroll past.

    '''

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None,
                 material: Optional[str] = None, fluid: Optional[str] = None):

        if context is None:
            context = {}

        if material is not None:
            context['material'] = material
        if fluid is not None:
            context['fluid'] = fluid

        super().__init__(message, context)

class NumericalInstabilityError(EngineeringError):

    '''

    Exception raised when a calculation produces NaN, infinity, or a value outside the range the
    governing correlation was fit over.

    '''

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None,
                 variableName: Optional[str] = None, value: Optional[float] = None):

        if context is None:
            context = {}

        if variableName is not None:
            context['variableName'] = variableName
        if value is not None:
            context['value'] = value

        super().__init__(message, context)

#--------------------------------------------------------------------------------------------------------------------------#
# -- Context Helper -- #
#--------------------------------------------------------------------------------------------------------------------------#

def createErrorContext(component: Optional[str] = None, fluid: Optional[str] = None,
                       massFlow: Optional[float] = None, upstreamPressure: Optional[float] = None,
                       downstreamPressure: Optional[float] = None, temperature: Optional[float] = None,
                       **additionalContext) -> Dict[str, Any]:

    '''

    Build a standard error context dictionary from the state variables that are almost always
    relevant when a fluid system calculation fails.

    Keeps the raise sites short and the error output consistent across every component class.

    '''

    context = {}

    if component is not None:
        context['component'] = component
    if fluid is not None:
        context['fluid'] = fluid
    if massFlow is not None:
        context['massFlow [kg/s]'] = massFlow
    if upstreamPressure is not None:
        context['upstreamPressure [Pa]'] = upstreamPressure
    if downstreamPressure is not None:
        context['downstreamPressure [Pa]'] = downstreamPressure
    if temperature is not None:
        context['temperature [K]'] = temperature

    context.update(additionalContext)

    return context
