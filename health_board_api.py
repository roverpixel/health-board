import requests
from typing import Optional, Dict, Any

class HealthBoard:
    """
    A Python client for the Health Board API.
    """

    def __init__(self, base_url: str = "http://127.0.0.1:5000/api"):
        """
        Initializes the HealthBoard API client.

        Args:
            base_url: The base URL of the Health Board API.
        """
        self.base_url = base_url

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        A helper method to make requests to the API.

        Args:
            method: The HTTP method to use (e.g., 'GET', 'POST').
            endpoint: The API endpoint to target.
            **kwargs: Additional arguments to pass to the requests call.

        Returns:
            The response object from the requests call.

        Raises:
            requests.exceptions.RequestException: For connection errors or timeouts.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()  # Raise an exception for bad status codes
            return response
        except requests.exceptions.RequestException as e:
            # Re-raise the exception to be handled by the caller
            raise e

    def get_health(self) -> Dict[str, Any]:
        """Fetches the overall health status."""
        response = self._request('GET', 'health')
        return response.json()

    def checkpoint(self) -> Dict[str, Any]:
        """Saves the current board state."""
        response = self._request('POST', 'checkpoint')
        return response.json()

    def restore(self) -> Dict[str, Any]:
        """Restores the board state from a checkpoint."""
        response = self._request('POST', 'restore')
        return response.json()

    def create_category(self, category_name: str) -> Dict[str, Any]:
        """Creates a new category."""
        response = self._request('POST', 'categories', json={"category_name": category_name})
        return response.json()

    def delete_category(self, category_name: str) -> requests.Response:
        """Deletes a category."""
        return self._request('DELETE', f'categories/{category_name}')

    def create_item(self, category_name: str, item_name: str, upsert: bool = True) -> Dict[str, Any]:
        """
        Creates an item within a category.

        Args:
            category_name: The name of the category.
            item_name: The name of the item to create.
            upsert: If True, the category will be created if it does not exist.

        Returns:
            The JSON response from the API.
        """
        if upsert:
            self.create_category(category_name)

        endpoint = f'categories/{category_name}/items'
        response = self._request('POST', endpoint, json={"item_name": item_name})
        return response.json()

    def delete_item(self, category_name: str, item_name: str) -> requests.Response:
        """Deletes an item."""
        endpoint = f'categories/{category_name}/items/{item_name}'
        return self._request('DELETE', endpoint)

    def update_item(self, category_name: str, item_name: str, status: Optional[str] = None, message: Optional[str] = None, url: Optional[str] = None, upsert: bool = True) -> Dict[str, Any]:
        """
        Updates an item's status, message, or URL.

        Args:
            category_name: The name of the category.
            item_name: The name of the item to update.
            status: The new status for the item.
            message: The new message for the item.
            url: The new URL for the item.
            upsert: If True, the category and item will be created if they do not exist.

        Returns:
            The JSON response from the API.
        """
        if upsert:
            # This will create the category and item if they don't exist.
            # If the item already exists, this will effectively do nothing.
            try:
                self.create_item(category_name, item_name, upsert=True)
            except requests.exceptions.HTTPError as e:
                # Ignore 409 Conflict errors, which indicate the item already exists.
                if e.response.status_code != 409:
                    raise

        endpoint = f'categories/{category_name}/items/{item_name}'
        payload = {}
        if status is not None:
            payload['status'] = status
        if message is not None:
            payload['message'] = message
        if url is not None:
            payload['url'] = url

        if not payload:
            # If no update parameters are provided, we might not need to do anything.
            # Depending on desired behavior, could return a message or the current item state.
            # For now, we'll proceed, which will effectively do a GET if the item exists.
            # Let's return a message for clarity.
            return {"message": "No update parameters provided. Item state unchanged."}


        response = self._request('PUT', endpoint, json=payload)
        return response.json()


class HealthBoardUpdater(HealthBoard):
    """
    A specialized HealthBoard client for updating a single item.
    """

    def __init__(self, base_url: str, category: str, item: str):
        """
        Initializes the HealthBoardUpdater.

        Args:
            base_url: The base URL of the Health Board API.
            category: The name of the category.
            item: The name of the item.
        """
        super().__init__(base_url)
        self.category = category
        self.item = item

    def update_item(self, status: Optional[str] = None, message: Optional[str] = None, url: Optional[str] = None, upsert: bool = True) -> Dict[str, Any]:
        """
        Updates the item's status, message, or URL.

        Args:
            status: The new status for the item.
            message: The new message for the item.
            url: The new URL for the item.
            upsert: If True, the category and item will be created if they do not exist.

        Returns:
            The JSON response from the API.
        """
        return super().update_item(self.category, self.item, status, message, url, upsert)


if __name__ == '__main__':
    # Example usage:
    # Make sure your Flask app is running before executing this script.

    # Using HealthBoard to manage categories and items
    client = HealthBoard(base_url="http://127.0.0.1:5000/api")
    try:
        print("Creating category 'services'...")
        client.create_category("services")
        print("Creating item 'database' in 'services'...")
        client.create_item("services", "database")
        print("Updating item 'database'...")
        client.update_item("services", "database", status="up", message="Database is running normally.")
        print("\nCurrent health status:")
        print(client.get_health())
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    # Using HealthBoardUpdater for a specific item
    item_updater = HealthBoardUpdater(base_url="http://127.0.0.1:5000/api", category="services", item="database")
    try:
        print("\nUpdating 'database' status to 'down' using HealthBoardUpdater...")
        item_updater.update_item(status="down", message="Database is offline for maintenance.")
        print("\nCurrent health status:")
        print(item_updater.get_health()) # Can still use other HealthBoard methods
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
