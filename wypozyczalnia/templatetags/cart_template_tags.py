from django import template
from wypozyczalnia.models import Order

register = template.Library()


@ register.filter
def cart_count(user):
    if user.is_authenticated:
        order_qs = Order.objects.filter(user=user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            return order.items.count()
    return 0
