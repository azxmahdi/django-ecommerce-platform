from cart.services.cart import CartService
from .storage import SessionStorage


def cart_processor(request):
    cart = CartService(SessionStorage(request.session))
    return {"cart": cart}
