def cart_item_count(request):
    cart = request.session.get('cart', {})
    total_items = 0
    
    for quantity in cart.values():
        # Handle cases where quantity might not be a number
        if isinstance(quantity, (int, float)):
            total_items += quantity
        elif isinstance(quantity, str) and quantity.isdigit():
            total_items += int(quantity)
        # Skip any other types (like dictionaries)
    
    return {'cart_item_count': total_items}