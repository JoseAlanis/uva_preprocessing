"""General utility functions that are re-used in different scripts."""

import click
from mne.utils import logger


@click.command()
@click.option("--subj", type=int, help="Subject number")
@click.option("--overwrite", default=False, type=bool, help="Overwrite?")
@click.option("--interactive", default=False, type=bool, help="Interactive?")
def get_inputs(
        subj,
        overwrite,
        interactive,
):
    """Parse inputs in case script is run from command line.
    See Also
    --------
    parse_overwrite
    """
    # collect all in dict
    inputs = dict(
        sub=subj,
        overwrite=overwrite,
        interactive=interactive,
    )

    return inputs


def parse_overwrite(defaults):
    """Parse which variables to overwrite."""
    logger.info("\nParsing command line options...\n")

    # invoke `get_inputs()` as command line application
    inputs = get_inputs.main(standalone_mode=False, default_map=defaults)

    # check if any defaults should be overwritten
    overwrote = 0
    for key, val in defaults.items():
        if val != inputs[key]:
            logger.info(f"    > Overwriting default '{key}': {val} -> {inputs[key]}")  # noqa
            defaults[key] = inputs[key]
            overwrote += 1
    if overwrote > 0:
        logger.info(f"\nOverwrote {overwrote} variables with command line options.\n")  # noqa
    else:
        logger.info("Nothing to overwrite, use defaults defined in script.\n")

    return defaults
