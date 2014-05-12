import logging
import os

from mongoengine import NotUniqueError, ValidationError
from orders.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import simplejson
from django.conf import settings

from settings import dao, render_menu, customer_mods, server_mods
from render.order import render_orders
from orders.forms import SectionForm, ItemForm, ItemInsert

logger = logging.getLogger('orders.views')

# TODO: perhaps we should have a centralized call to render so it
# includes the parent template as well as commons variables such as
# client_name.
def home(request):
    '''Home view with a signin and singup form'''

    return render(request, 'home_index.html',
                  {'title': 'Welcome',
                   'template': 'home.html'})

def signin(request):
    '''Sign In view'''
    if request.user.is_authenticated():
        '''If the user is already registered it goes
        to the manager screen'''
        return redirect('orders.views.manager')
    if request.method == 'POST':
        username = request.POST['session[username]']
        password = request.POST['session[password]']
        try:
            '''Tries to log in, if succeds it redirects to the
            manager view'''
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('orders.views.manager')
        except AttributeError:
            '''If it cant log in it gives a error message'''
            error = True
            error_value = 'Wrong username or password'
    else:
        error = False
        error_value = ''
        username = ''
    return render(request, 'home_index.html',
                  {'title': 'Sign In',
                   'template': 'signin.html',
                   'username': username,
                   'error': error,
                   'error_value': error_value})

def signup(request):
    if request.user.is_authenticated():
        '''If the user is already registered it goes
        to the manager screen'''
        return redirect('orders.views.manager')
    if request.method == 'POST':
        username = request.POST['user[name]']
        email = request.POST['user[email]']
        password = request.POST['user[user_password]']
        try:
            '''Tries to create a new client, if succeeds it logs in
            and redirects to the manager view'''
            User.create_user(username=username, email=email, password=password, manager=True)
            #dao.create_client(username)
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('orders.views.manager_items')
        except NotUniqueError, Argument:
            if 'username' in str(Argument):
                '''If the username is already registered it gives a
                error message'''
                error = {'username': True, 'email': False}
                error_value = 'Username already registered'
            elif 'email' in str(Argument):
                '''If the email is already registered it gives a
                error message'''
                error = {'username': False, 'email': True}
                error_value = 'Email already registered'
        except ValidationError:
            '''If the email submited doesnt have a valid form
            it gives a error message'''
            error = {'username': False, 'email': True}
            error_value = 'Not a valid email'
    else:
        error = {'username': False, 'email': False}
        error_value = username = email = ''
    return render(request, 'home_index.html',
                  {'title': 'Sign Up',
                   'template': 'signup.html',
                   'username': username,
                   'email': email,
                   'error': error,
                   'error_value': error_value})

def signout(request):
    '''Sign out view, it logs out and redirects to
    the home view'''
    logout(request)
    return redirect('orders.views.home')

def init_session(request, client_id, seat_id):
    '''Initializes the session with the client_id and seat_id of the
    user so it can be redirected to the right menu in the future. This
    takes the user to the top-level section of the client's active
    menu.'''
    # validate seat
    if not dao.is_valid_seat(client_id, seat_id):
        # TODO: in this case we should let the user browse the menu
        # but not place orders. For now we just error.
        raise Http404
    lmenu = dao.get_menu_of_seat(client_id, seat_id)
    if 'seat_id' not in request.session:
        request.session['seat_id'] = seat_id
    if 'client_id' not in request.session:
        request.session['client_id'] = client_id
    if 'menu_id' not in request.session:
        request.session['menu_id'] = lmenu
    if 'bill_n' not in request.session:
        dao.new_bill(client_id)
        bills = dao.get_bills(client_id)
        request.session['bill_n'] = bills

    return menu(request, lmenu)

def menu(request, menu_id, path = ''): 
    '''Main entry point for a menu. It takes the menu ID and the path
    within that menu the user is requesting. It uses the menu renderer
    configured in orders/settings.py'''
    logger.debug('menu_id: %s, path: %s', menu_id, path)
    client_id = request.session['client_id']
    m = dao.get_menu(menu_id)
    logger.info('with menu_id %s found: %s', menu_id, m)
    return render_menu(request, m, path, client_id)

def back_to_menu(request):
    '''Shortcut view for users to "return" back to the top of the menu
    they're browsing. Since client_id and seat_id are not provided,
    this only works if the user has a valid cookie that corresponds to
    a session where client_id and seat_id have already been recorded;
    this happens by default when they scan the QR code. If this is not
    true, a 404 is returned.'''
    if 'seat_id' in request.session and 'client_id' in request.session:
        cid = request.session['client_id']
        sid = request.session['seat_id']
        return init_session(request, cid, sid)
    raise Http404

def item(request, item_id):
    '''Renders a single item on a page that allows the customer to
    order one or more units of it.'''
    logger.debug({'item_id':item_id})
    item = dao.get_item(item_id)
    item['id'] = item['_id']
    logger.info('rendering item: %s', item)
    return render(request, 'index.html',
                 {'template':'item.html', 'title':item['name'], 'item':item})

def section(request, menu_id, *path):
    '''This view receives a tokenized path within a menu, and calls
    the menu renderer. Used by the basic menu template, but may be
    deprecated in the future for a more flexible view that doens't require the path 
    to be tokenized.'''
    logger.debug('mid: %s, path: %s', menu_id, path)
    menu = dao.get_menu(menu_id)
    logger.info('menu: %s, path: %s', menu, path)
    return render_menu(request, menu, '/'.join(path))

def menu_path(request, menu_id, path):
    '''This view receives a path that is not tokenized.'''
    pass

def manager_check():
    'Validates if the user is a manager'
    if not dao.is_manager(request.user.username):
        return redirect('orders.views.home')

@login_required
def manager(request):
    client_id = dao.get_client_id_from_username(request.user.username)
    client_name = dao.get_client_name(client_id)
    manager_check()
    
    return render(request, 'desktop_index.html',
                  {'template': 'manager.html',
                   'title': 'Manager',
                   'client': client_name})

@login_required
def manager_items(request):
    client_id = dao.get_client_id_from_username(request.user.username)
    items = dao.get_client_items(client_id)
    item_form = ItemForm()
    if request.method == 'POST':
        if request.is_ajax():
            if 'create_item' in request.POST:
                #This case handles the add items submit form
                item_form = ItemForm(request.POST)
                if item_form.is_valid():
                    #If the form is valid it enters here
                    cd = item_form.cleaned_data
                    name = cd['name']
                    price = cd['price']
                    description = cd['description']
                    dao.add_item(client_id, name, price, description)
            elif 'delete_item_id' in request.POST:
                #This case handles the delete item submit form
                item_id = request.POST['delete_item_id']
                dao.del_item(client_id, item_id)
            elif 'edit_item' in request.POST:
                #This case handles the updated items
                item_id = request.POST['item_id']
                name = request.POST['name']
                price = float(request.POST['price'])
                description = request.POST['description']
                dao.update_item(item_id, name = name, price = price, description = description)
            elif 'set_item_photo' in request.POST:
                #This case handles the upload item photo form
                dao.set_item_photo(request.POST['item_id'])
                
    return render(request, 'desktop_index.html',
                  {'items': items,
                   'item_form': item_form,
                   'template': 'manager_items.html',
                   'title': 'Manager',
                   'AWS_ACCESS_KEY_ID': settings.AWS_ACCESS_KEY_ID,
                   'policy': settings.POLICY,
                   'signature': settings.SIGNATURE,
                   'client': client_id})

@login_required
def manager_menus(request):
    client_id = dao.get_client_id_from_username(request.user.username)
    try:
        menus = dao.get_client_menus(client_id)
    except TypeError:
        menus = []
    item_form = ItemForm()
    items = dao.get_client_items(client_id)
    if request.method == 'POST':
        if request.is_ajax():
            if 'add_menu' in request.POST:
                "Adds new menu to the db"
                dao.add_menu(request.POST['menu_title'], client_id)
            elif 'save_menu' in request.POST:
                "Saves the selected menu to the db"
                menu = jstree2mongo(request.POST)
                dao.update_menu_title(menu['id'], menu['title'])
                dao.update_menu_structure(menu['id'], menu['structure'])
            elif 'item_form' in request.POST:
                item_form = ItemForm(request.POST)
                if item_form.is_valid():
                    cd = item_form.cleaned_data
                    name = cd['name']
                    price = cd['price']
                    description = cd['description']
                    if 'create_item' in request.POST:
                        dao.add_item(client_id, name, price, description)
                    elif 'edit_item' in request.POST:
                        item_id = request.POST['item_id']
                        dao.update_item(item_id, name = name, price = price, description = description)
    return render(request, 'desktop_index.html',
                  {'menus': menus, 'items': items,
                   'item_form': item_form,
                   'json_menus': mongo2jstree_list(menus),
                   'template': 'manager_menus.html',
                   'title': 'Manager'})

@login_required
def manager_seats(request):
    client_id = dao.get_client_id_from_username(request.user.username)
    if request.method == 'POST':
        if request.is_ajax():
            if 'create_room' in request.POST:
                'Creates a new room'
                menu_id = request.POST['menu']
                room_name = request.POST['room_name']
                dao.add_room(client_id, menu_id, room_name)
            elif 'delete_room' in request.POST:
                'Deletes a room'
                room_name = request.POST['room']
                dao.del_room(client_id, room_name)
            elif 'set_room_menu' in request.POST:
                'Sets the menu of a room'
                room_name = request.POST['room']
                menu_id = request.POST['menu']
                dao.set_room_menu(client_id, menu_id, room_name)
            elif 'create_seat' in request.POST:
                'Creates a new seat inside the room'
                room_name = request.POST['room']
                seat_name = request.POST['seat']
                dao.add_seat(client_id, room_name, seat_name)
            elif 'delete_seat' in request.POST:
                'Deletes a seat from a room'
                room_name = request.POST['room']
                seat_name = request.POST['seat']
                dao.del_seat(client_id, room_name, seat_name)
                
                
    seats = dao.get_seats(client_id)
    menus = dao.get_client_menus(client_id)
    return render(request, 'desktop_index.html',
                  {'template': 'manager_seats.html',
                   'title': 'Manager',
                   'seats': seats, 'client': client_id,
                   'menus': menus})

@login_required
def manager_profile(request):
    client_id = dao.get_client_id_from_username(request.user.username)
    client_name = dao.get_client_name(client_id)
    if request.method == 'POST':
        if request.is_ajax():
            if 'change_name_form' in request.POST:
                new_name = request.POST['name']
                dao.set_client_name(client_id, new_name)
            elif 'change_password_form' in request.POST:
                new_pass = request.POST['password']
                request.user.set_password(new_pass)                     

    return render(request, 'desktop_index.html',
                  {'template': 'manager_profile.html',
                   'title': 'Manager', 'client_name': client_name})
    

def place_order(request, item_id, client_id):
    '''Places an order for qty units of item_id from client_id. This
    should add the order to the DB, show the user a confirmation
    message and redirect them to the previous section they were
    browsing'''
    # TODO: orders should have an array of events. Validate all input.
    quantity = request.POST['quantity']
    comment = request.POST['comment']
    seat_id = request.session['seat_id']
    bill_n = request.session['bill_n']
    menu_id = request.session['menu_id']
    path = request.session['path']
    logger.info('item_id:%s, client_id:%s, quantity:%s', item_id, client_id, quantity)
    dao.add_order(item_id, quantity, comment, client_id, seat_id, menu_id, path, bill_n)
    item_name = dao.get_item(item_id)['name']
    message = '{} {} coming!. Seat back and relax.'.format(quantity, item_name)
    return render(request, 'index.html',
                  {'template':'confirmation.html', 'message':message})

def myorders(request):
    ''' Lists orders placed from this session as indicated by the
    session's seat_id and client_it. It will display orders that are
    in placed, prepared or served status.'''
    orders = customer_orders(request)
    sub_total = dao.orders_sub_total(orders)
    client_id = request.session['client_id']
    return render_orders(request, client_id, orders, customer_mods, sub_total=sub_total)

def customer_orders(request, statii = (dao.ORDER_PLACED, dao.ORDER_PREPARING,
                                       dao.ORDER_PREPARED, dao.ORDER_SERVED, dao.BILL_REQUESTED)):
    '''Helper function that returns a list of customer orders by
    extracting the seat and location id from the session in the input
    request. It defaults to orders in one of the following statii:
    dao.ORDER_PLACED, dao.ORDER_PREPARED, dao.ORDER_SERVED,
    dao.BILL_REQUESTED. The caller can use the optional param statii
    to get a different set.'''
    seat_id = request.session['seat_id']
    client_id = request.session['client_id']
    bill_n = request.session['bill_n']
    logger.info({'seat':seat_id, 'client':client_id})
    orders = dao.list_orders(client_id, query={'seat_id':seat_id, 'bill_number':bill_n, 'status':statii})
    return orders

def bill(request):
    '''requests the bill by updating the status of all active orders
    from this session to dao.BILL_REQUESTED'''
    message = 'bill coming!'
    orders = customer_orders(request)
    ids = [order['id'] for order in orders]
    dao.update_orders(ids, status=dao.BILL_REQUESTED)
    return render(request, 'index.html',
                  {'template':'confirmation.html', 'message':message})

def list_orders(request, client_id, query={}):
    '''Lists orders in the specified client's queue. It defaults to
    the pending orders. TODO: provide a way for the server or manager
    to filter by any combination of date, status and seat'''
    logger.debug({'client_id':client_id, 'query':query})
    if 'client_id' not in request.session:
        request.session['client_id'] = client_id
    # default to ORDER_PLACED for now
    if 'status' not in query:
        query['status'] = dao.ORDER_PLACED
    orders = dao.list_orders(client_id, query)
    logger.info({'orders': orders,'modifiers':server_mods})
    request.session['query'] = query
    return render_orders(request, client_id, orders, server_mods, is_screen=True)

def screen_refresh(request):
    client_id = request.session['client_id'] 
    query = request.session['query']
    orders = dao.list_orders_json(client_id, query=query)
    return HttpResponse(orders, content_type = "application/json")
    
def filter_orders(request):
    '''Allows the user to specify filters on the list of orders they want to see.'''
    logger.debug({'GET':request.GET})
    try:
        client_id = request.session['client_id']
    except KeyError as e:
        logger.error('Cannot filter orders with no client_id in the session')
        return HttpResponseBadRequest('Invalid session. Please scan QR code or login again.')
    # process filter and render orders
    if request.POST:
        query = {}
        statii = []
        for status in dao.ORDER_STATII:
            if status in request.POST:
                statii.append(status)
                query['status'] = statii
        if 'seats' in request.POST:
            query['seat_id'] = [str(i) for i in request.POST.getlist('seats')]
        if 'menus' in request.POST:
            query['menu_id'] = [str(i) for i in request.POST.getlist('menus')]
        if request.POST['bill_number'] <> '':
            query['bill_number'] = int(request.POST['bill_number'])
        if len(query) > 0:
            return list_orders(request, client_id, query=query)
    # Render form instead if there's no filter
    statii = []
    for status in dao.ORDER_STATII:
        st = {}
        st['id'] = status
        st['name'] = status.replace('_','').capitalize()
        statii.append(st)
    seats = dao.get_seats_ids(client_id)
    menus = dao.get_client_menus(client_id)
    logger.info({'statii':statii})
    return render(request, 'index.html', {'template':'filter_orders.html', 'client_id':client_id,
                                          'statii':statii, 'seats': seats, 'menus': menus})

def order(request, order_id): 
    '''Displays order details and allows a server to update the status
    of the order. It extracts the definition of valid statii from the dao'''
    order = dao.get_order(order_id)
    statii = []
    for status in dao.ORDER_STATII:
        statii.append({'name':status.replace('_','').capitalize(), 'value':status})
    return render(request, 'index.html', 
                  {'template':'order.html', 'order':order, 'statii':statii})

def update_order(request, order_id):
    '''Updates the specified order with the params in the request'''
    logger.info('order:%s', order_id)
    status = request.POST['status']
    res = dao.update_order(order_id, status)
    if res != status:
        # TODO: return a 503?
        return
    client_id = dao.get_client_id(order_id)
    return render(request, 'index.html',
                  {'template':'updated.html', 'client_id':client_id})

def cancel_order(request, order_id):
    '''Cancels the specified order if the order corresponds to the
    seat of the user sending this request. TODO: should this use
    update_order instead? if so, the html would need to contain a form
    per item in the list, which might not be a good idea.'''
    logger.debug({'order':order_id})
    try: 
        order = dao.get_order(order_id)
        sid = request.session['seat_id']
        if order['seat_id'] != sid:
            return HttpResponseForbidden('Only the user who placed the order can cancel it!')
        res = dao.update_order(order_id, dao.ORDER_CANCELED)
        if res != dao.ORDER_CANCELED:
            logger.error('error canceling order %s from seat %s', order_id, sid)
            return http.HttpResponseServerError('failed to update order status, please try again later')
    except KeyError as e:
        logger.error('sessions does not contain a seat ID - not canceling order %s'. order_id)
        return HttpResponseForbidden
    orders = customer_orders(request)
    return render_orders(request, orders, customer_mods)

####################
# Helper functions #
####################

def mongo2jstree(menu):
    '''Changes the structure of the menu that uses mongo
    to a way jstree can read it
    P.S: This function can go to infinite depth'''
    tree = {'data': []}
    tree['data'].append({'data': menu['title'], 'attr': {'id': str(menu['_id']), 'rel': 'root'}, 'state': 'open', 'children': []})
    explore_mongo(menu, tree = tree)
    return simplejson.dumps(tree)

def mongo2jstree_list(menus):
    '''handles multiple menus with the function above ( mongo2jstree() )'''
    js_menus = []
    for menu in menus:
        js_menus.append(mongo2jstree(menu))
    return js_menus 

def explore_mongo(data, name='', level = 0, path=[], tree = {'data': []}):
    '''Explores the menu in mongo with recursion'''
    if 'structure' in data:
        for child in data['structure']:
            explore_mongo(data['structure'][child], name=child, tree = tree)
    elif type(data) is dict:
        level += 1
        ##### SECTIONS #####
        path.insert(level-1, name)
        path = path[:level]
        eval(path_2_list(path, level)).insert(0, {'data': name, 'attr': {'rel': 'section'},'state': 'open','children':[]})
        for child in data:
            explore_mongo(data[child], name=child, level=level, path=path, tree=tree)
    elif type(data) is list:
        level += 1
        ##### SUBSECTIONS ######
        path.insert(level-1, name)
        path = path[:level]
        eval(path_2_list(path, level)).insert(0, {'data': name, 'attr': {'rel': 'subsection'}, 'state': 'open','children':[]})
        level += 1
        for child in reversed(data):
            ##### ITEMS #####
            item = dao.get_item(child)
            eval(path_2_list(path, level)).insert(0, {'data': item['name'], 'attr': {'id': child, 'rel': 'item', 'name': item['name'], 'price': item['price'], 'description': item['description']}})


def path_2_list(path, level):
    '''Help enters the path(string) in the structure(list)''' 
    string = "tree['data'][0]['children']"
    for branch in path[:level-1]:
        string += "[0]['children']"
    return string
  
def jstree2mongo(tree):
    '''Changes the structure of the menu that uses jstree
    to the original way that mongo uses.
    P.S: This function can go to infinite depth'''
    body = simplejson.loads(tree['tree'])
    structure = {}
    explore_jstree(body[0], structure = structure)
    return {unicode('structure'): structure, unicode('title'): body[0]['data'], unicode('id'): body[0]['attr']['id']}

def dictizeString(string, dictionary, item_id = unicode(), subsection = unicode(), section = unicode()):
    '''Help enters the path(string) in the structure(dictionary)''' 
    while string.startswith('/'):
        string = string[1:]
    parts = string.split('/', 1)
    if len(parts) > 1:
        branch = dictionary.setdefault(parts[0], {})
        dictizeString(parts[1], branch, item_id = item_id, subsection = subsection, section = section)
    else:
        if item_id:
            if dictionary.has_key(parts[0]):
                 dictionary[parts[0]].append(item_id)
            else:
                 dictionary[parts[0]] = [item_id]
        if subsection:
            if not dictionary.has_key(parts[0]):
                 dictionary[parts[0]] = []
        if section:
            if not dictionary.has_key(parts[0]):
                 dictionary[parts[0]] = {}
                               
def explore_jstree(data, path = '', structure = {}):
    '''Explores the menu in jstree with recursion'''
    if data['attr']['rel'] == 'root':
        if 'children' in data:
            for child in data['children']:
                explore_jstree(child, structure = structure)
            
    elif data['attr']['rel'] == 'section': 
        path += '/' + data['data']
        dictizeString(path, structure, section = data['data'])
        if 'children' in data:
            for child in data['children']:
                explore_jstree(child, path = path, structure = structure)
                
    elif data['attr']['rel'] == 'subsection':
        path += '/' + data['data']
        dictizeString(path, structure, subsection = data['data'])
        if 'children' in data:
            for child in data['children']:
                explore_jstree(child, path = path, structure = structure)
                
    elif data['attr']['rel'] == 'item':
        dictizeString(path, structure, item_id = data['attr']['id'])




