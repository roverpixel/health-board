#!/usr/bin/env python3
import click
import requests
import json

BASE_URL = "http://127.0.0.1:5000/api"

@click.group()
def board():
    """A CLI client to interact with the Health Dashboard API."""
    pass

# --- API Interaction Functions ---

def handle_response(response):
    """Helper function to handle API responses."""
    if response.ok:
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

def api_get_health():
    return requests.get(f"{BASE_URL}/health")

def api_checkpoint():
    return requests.post(f"{BASE_URL}/checkpoint")

def api_restore():
    return requests.post(f"{BASE_URL}/restore")

def api_create_category(category_name):
    return requests.post(f"{BASE_URL}/categories", json={"category_name": category_name})

def api_delete_category(category_name):
    return requests.delete(f"{BASE_URL}/categories/{category_name}")

def api_create_item(category_name, item_name):
    return requests.post(f"{BASE_URL}/categories/{category_name}/items", json={"item_name": item_name})

def api_delete_item(category_name, item_name):
    return requests.delete(f"{BASE_URL}/categories/{category_name}/items/{item_name}")

def api_update_item(category_name, item_name, status=None, message=None, url=None):
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

# --- CLI Commands ---

@board.group()
def create():
    """Create a new category or item."""
    pass

@create.command(name="category")
@click.argument('category_name')
def create_category(category_name):
    """Create a new category."""
    click.echo(f"Creating category: {category_name}...")
    response = api_create_category(category_name)
    handle_response(response)

@create.command(name="item")
@click.argument('category_name')
@click.argument('item_name')
def create_item(category_name, item_name):
    """Create a new item within a category."""
    click.echo(f"Creating item '{item_name}' in category '{category_name}'...")
    response = api_create_item(category_name, item_name)
    handle_response(response)

@board.group()
def remove():
    """Remove a category or item."""
    pass

@remove.command(name="category")
@click.argument('category_name')
def remove_category(category_name):
    """Remove a category and all its items."""
    click.echo(f"Removing category: {category_name}...")
    # It might be good to add a confirmation prompt here in a real CLI
    response = api_delete_category(category_name)
    handle_response(response)

@remove.command(name="item")
@click.argument('category_name')
@click.argument('item_name')
def remove_item(category_name, item_name):
    """Remove an item from a category."""
    click.echo(f"Removing item '{item_name}' from category '{category_name}'...")
    response = api_delete_item(category_name, item_name)
    handle_response(response)

# Placeholder for update command
@board.command()
@click.argument('category_name')
@click.argument('item_name')
@click.option('--status', help="The new status for the item (e.g., running, down, passing, failing, unknown, up).")
@click.option('--message', help="A descriptive message for the item's status.")
@click.option('--url', help="A URL related to the item for more details.")
def update(category_name, item_name, status, message, url):
    """Update an item's status, message, or URL."""
    if not status and not message and not url:
        click.echo(click.style("Error: At least one of --status, --message, or --url must be provided.", fg="red"))
        # You might want to show help here or exit with an error code
        # For now, just printing and returning
        return

    click.echo(f"Updating item '{item_name}' in category '{category_name}'...")
    response = api_update_item(category_name, item_name, status, message, url)
    if response: # api_update_item returns None if no parameters were given
        handle_response(response)

# Placeholder for save command
@board.command()
def save():
    """Save the current board data to a checkpoint file (health_data.json)."""
    click.echo("Saving (checkpointing) board data...")
    response = api_checkpoint()
    handle_response(response)

# Placeholder for restore command
@board.command()
def restore():
    """Restore the board data from the checkpoint file (health_data.json)."""
    click.echo("Restoring board data from checkpoint...")
    response = api_restore()
    handle_response(response)

# Placeholder for show command
@board.command()
def show():
    """Show the current board data."""
    click.echo("Fetching current board data...")
    response = api_get_health()
    handle_response(response) # This will print the JSON nicely


if __name__ == '__main__':
    board()
