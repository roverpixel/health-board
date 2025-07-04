#!/usr/bin/env python3
import click
import requests
import json
import os

BASE_URL = "http://127.0.0.1:5000/api"

@click.group()
@click.option('--verbose', '-v', is_flag=True, help="Enable verbose output.")
@click.option('--base-url', envvar='HEALTH_BOARD_URL', default='http://127.0.0.1:5000/api', help="Base URL for the Health Dashboard API. Can also be set via HEALTH_BOARD_URL env var.")
def board(verbose, base_url):
    """A CLI to interact with the Health Dashboard API."""
    # Store flags and resolved base_url in context for other commands to use
    ctx = click.get_current_context()
    ctx.obj = {
        'verbose': verbose,
        'base_url': base_url
    }


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

def api_get_health(base_url):
    return requests.get(f"{base_url}/health")

def api_checkpoint(base_url):
    return requests.post(f"{base_url}/checkpoint")

def api_restore(base_url):
    return requests.post(f"{base_url}/restore")

def api_create_category(base_url, category_name):
    return requests.post(f"{base_url}/categories", json={"category_name": category_name})

def api_delete_category(base_url, category_name):
    return requests.delete(f"{base_url}/categories/{category_name}")

def api_create_item(base_url, category_name, item_name):
    return requests.post(f"{base_url}/categories/{category_name}/items", json={"item_name": item_name})

def api_delete_item(base_url, category_name, item_name):
    return requests.delete(f"{base_url}/categories/{category_name}/items/{item_name}")

def api_update_item(base_url, category_name, item_name, status=None, message=None, url=None):
    payload = {}
    if status is not None:
        payload['status'] = status
    if message is not None:
        payload['message'] = message
    if url is not None:
        payload['url'] = url

    if not payload:
        click.echo(click.style("No update parameters provided.", fg="yellow"))
        return None # Or some other indicator that no request was made

    return requests.put(f"{BASE_URL}/categories/{category_name}/items/{item_name}", json=payload)

# --- CLI Commands ---

@board.group()
def create():
    """Create a new category or item."""
    pass

@create.command(name="category")
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.pass_context
def create_category(ctx, category_name):
    """Create a new category. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY env var."""
    verbose = ctx.obj['verbose']
    base_url = ctx.obj['base_url']

    if verbose:
        click.echo(f"Creating category: {category_name}...")
    try:
        response = api_create_category(base_url, category_name)
        handle_response(response, verbose)
    except requests.exceptions.RequestException as e:
        click.echo(click.style(f"API Request Error: {e}", fg="red"), err=True)


@create.command(name="item")
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.argument('item_name', envvar='HEALTH_BOARD_ITEM')
@click.pass_context
def create_item(ctx, category_name, item_name):
    """Create a new item. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY and ITEM_NAME via HEALTH_BOARD_ITEM."""
    verbose = ctx.obj['verbose']
    base_url = ctx.obj['base_url']

    if verbose:
        click.echo(f"Creating item '{item_name}' in category '{category_name}'...")
    try:
        response = api_create_item(base_url, category_name, item_name)
        handle_response(response, verbose)
    except requests.exceptions.RequestException as e:
        click.echo(click.style(f"API Request Error: {e}", fg="red"), err=True)


@board.group()
def remove():
    """Remove a category or item."""
    pass

@remove.command(name="category")
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.pass_context
def remove_category(ctx, category_name):
    """Remove a category. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY env var."""
    verbose = ctx.obj['verbose']
    base_url = ctx.obj['base_url']


    if verbose:
        click.echo(f"Removing category: {category_name}...")
    # It might be good to add a confirmation prompt here in a real CLI
    try:
        response = api_delete_category(base_url, category_name)
        handle_response(response, verbose)
    except requests.exceptions.RequestException as e:
        click.echo(click.style(f"API Request Error: {e}", fg="red"), err=True)


@remove.command(name="item")
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.argument('item_name', envvar='HEALTH_BOARD_ITEM')
@click.pass_context
def remove_item(ctx, category_name, item_name):
    """Remove an item. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY and ITEM_NAME via HEALTH_BOARD_ITEM."""
    verbose = ctx.obj['verbose']
    base_url = ctx.obj['base_url']

    if verbose:
        click.echo(f"Removing item '{item_name}' from category '{category_name}'...")
    try:
        response = api_delete_item(base_url, category_name, item_name)
        handle_response(response, verbose)
    except requests.exceptions.RequestException as e:
        click.echo(click.style(f"API Request Error: {e}", fg="red"), err=True)


# Placeholder for update command
@board.command()
@click.argument('category_name', envvar='HEALTH_BOARD_CATEGORY')
@click.argument('item_name', envvar='HEALTH_BOARD_ITEM')
@click.option('--status', help="The new status for the item (e.g., running, down, passing, failing, unknown, up).")
@click.option('--message', help="A descriptive message for the item's status.")
@click.option('--url', help="A URL related to the item for more details.")
@click.pass_context
def update(ctx, category_name, item_name, status, message, url):
    """Update an item. CATEGORY_NAME can be set via HEALTH_BOARD_CATEGORY and ITEM_NAME via HEALTH_BOARD_ITEM."""
    verbose = ctx.obj['verbose']
    base_url = ctx.obj['base_url']


    if not status and not message and not url:
        click.echo(click.style("Error: At least one of --status, --message, or --url must be provided.", fg="red"), err=True)
        # You might want to show help here or exit with an error code
        # For now, just printing and returning
        return

    if verbose:
        click.echo(f"Updating item '{item_name}' in category '{category_name}'...")
    try:
        response = api_update_item(base_url, category_name, item_name, status, message, url)
        if response: # api_update_item returns None if no parameters were given
            handle_response(response, verbose)
    except requests.exceptions.RequestException as e:
        click.echo(click.style(f"API Request Error: {e}", fg="red"), err=True)


# Placeholder for save command
@board.command()
@click.pass_context
def save(ctx):
    """Save the current board data to a checkpoint file (health_data.json)."""
    verbose = ctx.obj['verbose']
    base_url = ctx.obj['base_url']
    if verbose:
        click.echo("Saving (checkpointing) board data...")
    try:
        response = api_checkpoint(base_url)
        handle_response(response, verbose)
    except requests.exceptions.RequestException as e:
        click.echo(click.style(f"API Request Error: {e}", fg="red"), err=True)


# Placeholder for restore command
@board.command()
@click.pass_context
def restore(ctx):
    """Restore the board data from the checkpoint file (health_data.json)."""
    verbose = ctx.obj['verbose']
    base_url = ctx.obj['base_url']
    if verbose:
        click.echo("Restoring board data from checkpoint...")
    try:
        response = api_restore(base_url)
        handle_response(response, verbose)
    except requests.exceptions.RequestException as e:
        click.echo(click.style(f"API Request Error: {e}", fg="red"), err=True)


# Placeholder for show command
@board.command()
@click.pass_context
def show(ctx):
    """Show the current board data."""
    verbose = ctx.obj['verbose']
    base_url = ctx.obj['base_url']
    if verbose:
        click.echo("Fetching current board data...")
    try:
        response = api_get_health(base_url)
        # For the show command, we always want to display the response if successful,
        # overriding the global verbose flag for the handle_response part.
        if response.ok:
            handle_response(response, verbose=True)
        else:
            handle_response(response, verbose=verbose) # For errors, respect global verbose for consistency
    except requests.exceptions.RequestException as e:
        click.echo(click.style(f"API Request Error: {e}", fg="red"), err=True)



if __name__ == '__main__':
    board()
