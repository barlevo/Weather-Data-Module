
import click
from weather_module.pipeline import run_pipeline
from weather_module.config import get_settings
from weather_module.logging_config import setup_logging, get_logger

logger = get_logger("cli")


@click.group()
def cli():
    """Weather processing CLI.

    Tools for reading a CSV of locations, fetching weather data,
    and writing enriched CSV outputs.
    """
    pass


@cli.command()
@click.argument("input_csv", type=click.Path(exists=True, readable=True))
@click.argument("output_csv", type=click.Path(writable=True))
@click.option(
    "--units",
    type=click.Choice(["C", "F","K","both", "ALL"], case_sensitive=False),
    default="C",
    show_default=True,
    help="Temperature units to use in the output.",
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable caching of weather results.",
)
@click.option(
    "--ttl",
    "cache_ttl",
    type=int,
    default=900,
    show_default=True,
    help="Cache TTL in seconds (if cache is enabled).",
)
@click.option(
    "--max-rows",
    type=int,
    default=None,
    help="Process at most this many rows from the input CSV.",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output.",
)
@click.option(
    "--bulk",
    "use_bulk",
    is_flag=True,
    help="Use WeatherAPI bulk endpoint instead of per-location requests.",
)
@click.option(
    "--detailed",
    is_flag=True,
    default=False,
    help="Include detailed weather data (pressure, humidity, UV, etc.) in output.",
)
def run(
    input_csv: str,
    output_csv: str,
    units: str,
    no_cache: bool,
    cache_ttl: int,
    max_rows: int | None,
    verbose: bool,
    use_bulk: bool,
    detailed: bool,
):
    """Run the main weather processing pipeline.

    INPUT_CSV: Path to input CSV containing locations.
    OUTPUT_CSV: Path to output CSV that will contain weather results.
    """
    use_cache = not no_cache
    
    settings = get_settings()
    log_level = "DEBUG" if verbose else settings.log_level
    setup_logging(
        level=log_level, 
        log_file=settings.log_file,
        log_to_console=settings.log_to_console
    )

    logger.info("CLI run command invoked")
    
    if verbose:
        click.echo(f"➡️  Running pipeline:")
        click.echo(f"    input:   {input_csv}")
        click.echo(f"    output:  {output_csv}")
        click.echo(f"    units:   {units}")
        click.echo(f"    cache:   {'on' if use_cache else 'off'} (ttl={cache_ttl}s)")
        click.echo(f"    detailed: {'on' if detailed else 'off'}")
        if max_rows is not None:
            click.echo(f"    max rows: {max_rows}")

    try:
        run_pipeline(
            input_csv=input_csv,
            output_csv=output_csv,
            units=units.upper(),
            use_cache=use_cache,
            cache_ttl=cache_ttl,
            max_rows=max_rows,
            verbose=verbose,
            use_bulk=use_bulk,
            detailed=detailed,
        )
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)

    logger.info("CLI run command completed successfully")
    if verbose:
        click.echo("✅ Done.")


def main():
    """Main entry point for CLI. Initializes logging before running CLI."""
    settings = get_settings()
    setup_logging(
        level=settings.log_level, 
        log_file=settings.log_file,
        log_to_console=settings.log_to_console
    )
    logger.info("Weather Module CLI initialized")
    cli()


if __name__ == "__main__":
    main()
