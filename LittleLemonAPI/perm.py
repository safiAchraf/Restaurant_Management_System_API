def isManager(user):
    return user.is_authenticated and user.groups.filter(name='Manager').exists()
def isDelivery(user):
    return user.is_authenticated and user.groups.filter(name='Delivery crew').exists()