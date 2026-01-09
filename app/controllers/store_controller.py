import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from app.models.order import Order  # noqa: E501
from app import util


def delete_order(order_id):  # noqa: E501
    """Delete purchase order by identifier.

    For valid response try integer IDs with value &lt; 1000. Anything above 1000 or non-integers will generate API errors. # noqa: E501

    :param order_id: ID of the order that needs to be deleted
    :type order_id: int

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'OK!', {'Content-Type': 'application/json'}


def get_inventory():  # noqa: E501
    """Returns pet inventories by status.

    Returns a map of status codes to quantities. # noqa: E501


    :rtype: Union[Dict[str, int], Tuple[Dict[str, int], int], Tuple[Dict[str, int], int, Dict[str, str]]
    """
    return 'OK!', {'Content-Type': 'application/json'}


def get_order_by_id(order_id):  # noqa: E501
    """Find purchase order by ID.

    For valid response try integer IDs with value &lt;&#x3D; 5 or &gt; 10. Other values will generate exceptions. # noqa: E501

    :param order_id: ID of order that needs to be fetched
    :type order_id: int

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    return 'OK!', {'Content-Type': 'application/json'}


def place_order(body=None):  # noqa: E501
    """Place an order for a pet.

    Place a new order in the store. # noqa: E501

    :param order: 
    :type order: dict | bytes

    :rtype: Union[Order, Tuple[Order, int], Tuple[Order, int, Dict[str, str]]
    """
    order = body
    if connexion.request.is_json:
        order = Order.from_dict(connexion.request.get_json())  # noqa: E501
    return 'OK!', {'Content-Type': 'application/json'}
