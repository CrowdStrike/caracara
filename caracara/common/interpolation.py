"""
Caracara: Variable Interpolation Logic.

The functions within this file allow for interpolation of variables based on
the contents of environment variables, similar to how Docker allows for
strings such as ${SOME_VALUE} within Dockerfiles.

You can then do something along the lines of:
client = Client(
    client_id="${FALCON_CLIENT_ID}",
    client_secret="${FALCON_CLIENT_SECRET}",
    cloud_name="${FALCON_CLOUD_NAME}",
)

Whilst this is somewhat an antipattern in the example code provided, it does
allow for the examples to be configured with values provided as environment variables.
It may also be advantageous for some scripting implementations, where the user may wish
to configure Caracara dynamically or interactively by using environment variables.
"""
import logging
import os
import re


class VariableInterpolator:  # pylint: disable=too-few-public-methods
    """
    Variable interpolation class.

    We define this as a class rather than a standalone function so that we only have to
    compile the regex pattern ones. This gives a (very slight) performance gain when performing
    interpolation against a long list of variables.
    """

    def __init__(self):
        """
        Configure the interpolation regex pattern.

        The pattern will search for all instances of ${text} in a string, but
        will not match on $${text}. This allows a double dollar sign to act as
        an escape character.
        The pattern will return just the inner text (without the $ or {}).
        """
        self._pattern = re.compile(r'(?<!\$)\$\{(\w+)\}')

        self.logger = logging.getLogger(__name__)
        self.logger.debug("Instantiating a Variable Interpolator")

    def interpolate(self, input_string: str) -> str:
        """
        Take an input string and swap interpolation strings with environment variables.

        Since the regex pattern only returns the inner text, we need to re-add the
        $ and {} to the matched string to find the string to replace.
        This allows us to look up the inner text as an environment variable name, and still
        have the full interpolation string for replacement purposes.
        """
        if not input_string:
            return None

        matches = self._pattern.findall(input_string)
        output_string = input_string
        for match in matches:
            """
            text -> ${text}
            Triple curly braces are used as we need a double curly brace for the
            actual curly brace character, plus a third curly brace for the
            f-string variable name.
            """
            interpolation_str = f'${{{match}}}'
            self.logger.debug("Interpolating the environment variable: %s", match)
            output_string = output_string.replace(
                interpolation_str,
                os.environ.get(match, match)
            )

        # Unescape by replacing double dollar signs with single dollar signs
        output_string = output_string.replace("$$", "$")

        return output_string
