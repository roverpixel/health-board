#!/usr/bin/env python3
import click
import requests
import json
import os
import functools
from health_board_api import HealthBoard

@click.group()
@click.option('--verbose', '-v', is_flag=True, help="Enable verbose output.")
@click.option('--base-url', envvar='HEALTH_BOARD_URL', default='http://127.0.0.1:5000/api', help="Base URL for the Health Dashboard API. Can also be set via HEALTH_BOARD_URL env var.")
def board(verbose, base_url):
    """A CLI to interact with the Health Dashboard API."""
    # Store flags and resolved base_url in context for other commands to use
    ctx = click.get_current_context()
    ctx.obj = {
        'verbose': verbose,
        'base_url': base_url,
        'board': HealthBoard(base_url=base_url)
    }

# --- Error Handling Decorator ---

def handle_api_exceptions(func):
    """Decorator to catch and handle requests.exceptions.RequestException for API calls."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            click.echo(click.style(f"API Request Error: {e}", fg="red"), err=True)
            # Consider returning a specific error code or value if needed by the CLI framework
            # For now, it suppresses the exception and prints an error, commands will just terminate.
    return wrapper

# --- API Interaction Functions ---

def handle_response(response, verbose=False):
    """Helper function to handle API responses."""
    if response.ok:
        if verbose:
            try:
                click.echo(click.style("Success:", fg="green"))
                click.echo(json.dumps(response.json(), indent=2))
            except json.JSONDecodeError:
                # If no JSON body, just print a success message if that's the case
                if response.text:
                    click.echo(response.text)
                else:
                    click.echo(f"Status Code: {response.status_code} (No content)")
    else:
        click.echo(click.style(f"Error: {response.status_code}", fg="red"))
        try:
            error_data = response.json()
            click.echo(json.dumps(error_data, indent=2))
        except json.JSONDecodeError:
            click.echo(response.text or "No additional error information.")
    return response.ok # Return True if successful, False otherwise

# --- CLI Commands ---

# --- CLI Commands ---

@board.group()
def create():
    """Create a new category or item."""
    pass

@create.command(name="category")
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.pass_context
@handle_api_exceptions
def create_category(ctx, category_name):
    """Create a new category. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY env var."""
    verbose = ctx.obj['verbose']
    board = ctx.obj['board']

    if verbose:
        click.echo(f"Creating category: {category_name}...")
    response = board.create_category(category_name)
    click.echo(json.dumps(response, indent=2))

@create.command(name="item")
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.argument('item_name', envvar='HEALTH_BOARD_ITEM')
@click.pass_context
@handle_api_exceptions
def create_item(ctx, category_name, item_name):
    """Create a new item. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY and ITEM_NAME via HEALTH_BOARD_ITEM."""
    verbose = ctx.obj['verbose']
    board = ctx.obj['board']

    if verbose:
        click.echo(f"Creating item '{item_name}' in category '{category_name}'...")
    response = board.create_item(category_name, item_name)
    click.echo(json.dumps(response, indent=2))

@board.group()
def remove():
    """Remove a category or item."""
    pass

@remove.command(name="category")
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.pass_context
@handle_api_exceptions
def remove_category(ctx, category_name):
    """Remove a category. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY env var."""
    verbose = ctx.obj['verbose']
    board = ctx.obj['board']

    if verbose:
        click.echo(f"Removing category: {category_name}...")
    # It might be good to add a confirmation prompt here in a real CLI
    board.delete_category(category_name)
    click.echo(f"Category '{category_name}' removed.")

@remove.command(name="item")
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.argument('item_name', envvar='HEALTH_BOARD_ITEM')
@click.pass_context
@handle_api_exceptions
def remove_item(ctx, category_name, item_name):
    """Remove an item. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY and ITEM_NAME via HEALTH_BOARD_ITEM."""
    verbose = ctx.obj['verbose']
    board = ctx.obj['board']

    if verbose:
        click.echo(f"Removing item '{item_name}' from category '{category_name}'...")
    board.delete_item(category_name, item_name)
    click.echo(f"Item '{item_name}' from category '{category_name}' removed.")

# Placeholder for update command
@board.command()
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.argument('item_name', envvar='HEALTH_BOARD_ITEM')
@click.option('--status', help="The new status for the item (e.g., running, down, passing, failing, unknown, up).")
@click.option('--message', help="A descriptive message for the item's status.")
@click.option('--url', help="A URL related to the item for more details.")
@click.pass_context
@handle_api_exceptions
def update(ctx, category_name, item_name, status, message, url):
    """Update an item. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY and ITEM_NAME via HEALTH_BOARD_ITEM."""
    verbose = ctx.obj['verbose']
    board = ctx.obj['board']

    if not status and not message and not url:
        click.echo(click.style("Error: At least one of --status, --message, or --url must be provided.", fg="red"), err=True)
        # You might want to show help here or exit with an error code
        # For now, just printing and returning
        return

    if verbose:
        click.echo(f"Updating item '{item_name}' in category '{category_name}'...")
    response = board.update_item(category_name, item_name, status, message, url)
    if response: # api_update_item returns None if no parameters were given
        click.echo(json.dumps(response, indent=2))

# Placeholder for save command
@board.command()
@click.pass_context
@handle_api_exceptions
def save(ctx):
    """Save the current board data to a checkpoint file (health_data.json)."""
    verbose = ctx.obj['verbose']
    board = ctx.obj['board']
    if verbose:
        click.echo("Saving (checkpointing) board data...")
    response = board.checkpoint()
    click.echo(json.dumps(response, indent=2))

# Placeholder for restore command
@board.command()
@click.pass_context
@handle_api_exceptions
def restore(ctx):
    """Restore the board data from the checkpoint file (health_data.json)."""
    verbose = ctx.obj['verbose']
    board = ctx.obj['board']
    if verbose:
        click.echo("Restoring board data from checkpoint...")
    response = board.restore()
    click.echo(json.dumps(response, indent=2))

# Placeholder for show command
@board.command()
@click.pass_context
@handle_api_exceptions
def show(ctx):
    """Show the current board data."""
    verbose = ctx.obj['verbose']
    board = ctx.obj['board']
    if verbose:
        click.echo("Fetching current board data...")
    response = board.get_health()
    click.echo(json.dumps(response, indent=2))


if __name__ == '__main__':
    board()
