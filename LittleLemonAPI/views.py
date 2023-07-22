from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes , throttle_classes
from . import models
from django.core.paginator import Paginator, EmptyPage
from .perm import isManager , isDelivery
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from .serializers import *
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from datetime import date


@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle,AnonRateThrottle])

def menuitems(request):
    if request.user.is_authenticated :
        if request.method == 'GET':
            items = models.MenuItem.objects.select_related('category').all()
            category_name = request.query_params.get('category')
            to_price = request.query_params.get('to_price')
            search = request.query_params.get('search')
            ordering = request.query_params.get('ordering')
            page = request.query_params.get('page', default=1)
            per_page = request.query_params.get('perpage', default=3)

            if category_name:
                items = items.filter(category__name=category_name)
            if to_price:
                items = items.filter(price__lte=to_price)
            if search:
                items = items.filter(title__startswith=search)
            if ordering:
                items = items.order_by(*ordering.split(','))

            paginator = Paginator(items, per_page=per_page)
            try:
                items_page = paginator.page(number=page)
            except EmptyPage:
                items_page = paginator.page(number=paginator.num_pages)

            serializer = MenuItemSerializer(items_page, many=True)
            
            next_page = items_page.next_page_number() if items_page.has_next() else None
            previous_page = items_page.previous_page_number() if items_page.has_previous() else None

            res = {
                'count': paginator.count,
                'next_page': request.build_absolute_uri(f"?page={next_page}&perpage={per_page}") if next_page else None,
                'previous_page': request.build_absolute_uri(f"?page={previous_page}&perpage={per_page}") if previous_page else None,
                'results': serializer.data
            }
            
            return Response(res)
        elif request.method == 'POST' and isManager(request.user):
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        else:
            return Response({'error':'method not allowed'},status=403)
    else:
        return Response({'message': 'Authentication required.'})


@api_view(['GET', 'POST', 'DELETE', 'PATCH', 'PUT'])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
@permission_classes([IsAuthenticated])
def menuitem(request , pk):
    try:
        item = models.MenuItem.objects.get(pk=pk)
    except models.MenuItem.DoesNotExist:
        return Response({'error':'not found'},status=404)
    if request.method == 'GET':
        serializer = MenuItemSerializer(item)
        return Response(serializer.data)
    elif request.method == 'POST' and isManager(request.user):
        serializer = MenuItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    elif request.method == 'DELETE' and isManager(request.user):
        item.delete()
        return Response({'success':'deleted'},status=204)
    elif (request.method == 'PATCH' or request.method == 'PUT') and isManager(request.user):
        if request.method == 'PATCH':
            serializer = MenuItemSerializer(item, data=request.data, partial=True)
        else:
            serializer = MenuItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    else:
        return Response({'error':'method not allowed'},status=403)


@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
@permission_classes([IsAuthenticated])
def managers(request):
    if isManager(request.user):
        if request.method == 'GET':
            delivery_crews = User.objects.filter(groups__name='Manager')
            data = UserSerializer(delivery_crews, many=True)
            return Response(data.data)
        elif request.method == 'POST':
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'error':'user not found'},status=404)
            
            user.groups.add(Group.objects.get(name='Manager'))
            return Response({'success':'user added to managers group'},status=201)
        else:
            return Response({'error':'method not allowed'},status=403)
        
@api_view(['DELETE'])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
@permission_classes([IsAuthenticated])
def remove_manager(request,pk):
    if isManager(request.user):
        if request.method == 'DELETE':
            try:
                user =  User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response({'error':'user not found'},status=404)
            
            user.groups.remove(Group.objects.get(name='Manager'))
            return Response({'success':'removed'},status=200)
        else:
            return Response({'error':'method not allowed'},status=403)




@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
@permission_classes([IsAuthenticated])
def delivery_crew(request):
    if isManager(request.user):
        if request.method == 'GET':
            delivery_crews = User.objects.filter(groups__name='Delivery crew')
            data = UserSerializer(delivery_crews, many=True)
            return Response(data.data)
        elif request.method == 'POST':
            username = request.data.get('username')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'error':'user not found'},status=404)
            
            user.groups.add(Group.objects.get(name='Delivery crew'))
            return Response({'success':'user added to delivery crew'},status=201)
        else:
            return Response({'error':'method not allowed'},status=403)
        
@api_view(['DELETE'])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
@permission_classes([IsAuthenticated])
def remove_delivery(request,pk):
    if isManager(request.user):
        if request.method == 'DELETE':
            try:
                user =  User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response({'error':'user not found'},status=404)
            
            user.groups.remove(Group.objects.get(name='Delivery crew'))
            return Response({'success':'removed'},status=200)
        else:
            return Response({'error':'method not allowed'},status=403)


@api_view(['GET','POST','DELETE'])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
def cart(request):
    if request.user.is_authenticated :
        if not isDelivery(request.user) and not isManager(request.user):
            items = models.Cart.objects.filter(user=request.user).select_related('menuitem')
            if request.method == 'GET':
                items = CartSerializer(items, many=True)
                return Response(items.data)
            if request.method == 'POST':
                id = request.data['menuitem']
                quantity = request.data['quantity']
                item = models.MenuItem.objects.get(id=id)
                price = item.price * int(quantity)
                try:
                    Cart.objects.create(user=request.user, quantity=quantity, unit_price= item.price,price = price, menuitem_id=id)
                except:
                    return Response(status=409, data={'message':'Item already in cart'})
                return Response(status=201, data={'message':'Item added to cart!'})  
            if request.method == 'DELETE':
                items.delete()
                return Response({'message': 'All menu items in the cart have been deleted.'})
    else: 
        return Response({'message': 'Authentication required.'})



@api_view(['GET','POST'])
@throttle_classes([UserRateThrottle,AnonRateThrottle])
def orders(request):
    if request.user.is_authenticated :
        if not isDelivery(request.user) and not isManager(request.user):
            if request.method == 'GET':
                items = models.Order.objects.filter(user=request.user)
                return myorders(request,items)
            
            if request.method == 'POST':
                cart = models.Cart.objects.filter(user=request.user)
                total = 0
                for item in cart:
                    total += item.price
                order = Order.objects.create(user=request.user, status=False, total=total, date=date.today())
                for item in cart:
                    OrderItem.objects.create(order=order, menuitem=item.menuitem, quantity=item.quantity, price=item.price)
                cart.delete()
                return Response(status=201, data={'message':'Order placed successfully!'})
        elif isManager(request.user):
            if request.method == 'GET':
                items = models.Order.objects.all()
                return myorders(request,items)
        elif isDelivery(request.user):
            if request.method == 'GET':
                items = models.Order.objects.filter(delivery_crew=request.user)
                return myorders(request,items)
        else:
            return Response({'error':'method not allowed'},status=403)
    else:
        return Response({'message': 'Authentication required.'})
    

@api_view(['GET','PUT','PATCH','DELETE'])
@throttle_classes([AnonRateThrottle,UserRateThrottle])
def SingleOrder(request , pk):
    if request.user.is_authenticated :
        if not isDelivery(request.user) and not isManager(request.user) :
            if request.method == 'GET':
                order = Order.objects.filter(pk=pk, user=request.user).first()
                if order:
                    serial = OrderSerializer(order)
                    return Response(serial.data)
                else:
                    return Response({'message': 'You do not have permission to access this order.'}, status=403)
        else:
            return Response({'message': 'Authentication required.'})

        if isManager(request.user):
            if request.method == 'PATCH' or request.method == 'PUT':
                status = request.data.get('status')
                delivery = request.data.get('delivery_crew_id')
                order = Order.objects.filter(pk=pk).first()
                delivery = User.objects.get(pk=delivery)
                if order :
                    if delivery:
                        order.delivery_crew = delivery
                    if status:
                        order.status = status
                    order.save()
                    return Response({'message': 'Order updated successfully!'})
                else:
                    return Response({'message': 'Order not found!'}, status=404)
            if request.method == 'DELETE':
                order = Order.objects.filter(pk=pk).first()
                if order:
                    order.delete()
                    return Response({'message': 'Order deleted successfully!'})
                else:
                    return Response({'message': 'Order not found!'}, status=404)
        elif isDelivery(request.user):
            if request.method == 'GET':
                order = Order.objects.filter(pk=pk, delivery_crew=request.user)
                serial = OrderSerializer(order , many=True)
                return Response(serial.data)
            elif request.method == 'PATCH':
                order = Order.objects.filter(pk=pk, delivery_crew=request.user).first()
                serializer = OrderPUTSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                status = request.data['status']
                order.status = status
                order.save()
                return Response({'message': 'Order updated successfully!'},status=200)
    else:
        return Response({'message': 'Authentication required.'})
        


def myorders(request , items):
    category_name = request.query_params.get('category')
    to_price = request.query_params.get('to_price')
    search = request.query_params.get('search')
    ordering = request.query_params.get('ordering')
    page = request.query_params.get('page', default=1)
    per_page = request.query_params.get('perpage', default=3)

    if category_name:
        items = items.filter(category__name=category_name)
    if to_price:
        items = items.filter(price__lte=to_price)
    if search:
        items = items.filter(title__startswith=search)
    if ordering:
        items = items.order_by(*ordering.split(','))

    paginator = Paginator(items, per_page=per_page)
    try:
        items_page = paginator.page(number=page)
    except EmptyPage:
        items_page = paginator.page(number=paginator.num_pages)

    serializer = OrderSerializer(items_page, many=True)
    
    next_page = items_page.next_page_number() if items_page.has_next() else None
    previous_page = items_page.previous_page_number() if items_page.has_previous() else None
    res = {
        'count': paginator.count,
        'next_page': request.build_absolute_uri(f"?page={next_page}&perpage={per_page}") if next_page else None,
        'previous_page': request.build_absolute_uri(f"?page={previous_page}&perpage={per_page}") if previous_page else None,
        'results': serializer.data
    }
    return Response(res)
