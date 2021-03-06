import logging
import os
import pymongo
import datetime
import time

import json
from bson import json_util
from django.conf import settings
from bson.objectid import ObjectId
from bootstrap import menus, items, clients
from orders import OrdersDAO
from mongoengine.django.auth import User

logger = logging.getLogger('orders.mongo')

class MongoOrdersDAO(OrdersDAO):
    '''This class defines the data access object to be used for data
    stored in MongoDB'''

    def __init__(self, bootstrap=False):
        self.db = settings._MONGODB
        if bootstrap:
            # load bootstrap data
            self.db.user.remove()
            User.create_user(username='c@0.com', email='c@0.com', password='c@0.com')
            self.db.menus.remove()
            self.db.menus.insert(menus)
            self.db.items.remove()
            self.db.items.insert(items)
            self.db.clients.remove()
            self.db.clients.insert(clients)
            self.db.orders.remove()
            self.db.django_session.remove()

    def create_client(self, name):
        new_user = self.db.clients.insert({
            'name': name,
            'menus': [],
            'seats': {},
            'bills': 0
        })
        self.db.items.insert({'photo': False, 'name': "my first item", 'price': 0, 'description': "this is my first item", 'client_id': new_user })
        return new_user

    def delete_user(self, username):
        self.db.user.remove({'username': username})

    def add_client_id_to_user(self, username, client_id):
        self.db.user.update({'username': username}, {'$set': {'client_id': client_id}})

    def get_client_id_from_username(self, username):
        return self.db.user.find_one({'username': username})['client_id']

    def get_client_from_username(self, username):
        return self.db.user.find_one({'username': username})

    def change_user_password(self, username, password):
        self.db.user.update({'username': username}, {'$set': {'password': password}})

    def get_screen_users(self, client_id):
        mongoid = get_mongo_id(client_id)
        return self.db.user.find({'client_id': mongoid, 'screen': True})

    def set_manager(self, username, value):
        self.db.user.update({'username': username}, {'$set': {'manager': value}})

    def set_screen(self, username, value):
        self.db.user.update({'username': username}, {'$set': {'screen': value}})

    def is_manager(self, username):
        'Checks if request.user has attr manager:True'
        return self.db.user.find_one({'username': username})['manager']

    def is_screen(self, username):
        'Checks if request.user has attr screen:True'
        return self.db.user.find_one({'username': username})['screen']

    def get_bills(self, client_id):
        mongoid = get_mongo_id(client_id)
        return self.db.clients.find_one({'_id': mongoid})['bills']

    def new_bill(self, client_id):
        mongoid = get_mongo_id(client_id)
        self.db.clients.update({'_id': mongoid}, {'$inc': {'bills': 1}})
        return self.db.bills.insert({
                'client_id': mongoid,
                'bill_number': self.get_bills(mongoid),
                'orders': [],
                'status': self.BILL_NOT_VERIFIED,
                'createdAt': datetime.datetime.utcnow()
                })

    def get_menu(self, menu_id):
        '''Gets the menu that matches the specified menu ID'''
        logger.debug('menu_id: %s', menu_id)
        mongoid = get_mongo_id(menu_id)
        menu = self.db.menus.find_one(mongoid)
        menu['id'] = str(menu['_id'])
        logger.info('menu:%s', menu)
        return menu

    def get_menu_paths(self, menu_id):
        mongoid = get_mongo_id(menu_id)
        menu = self.db.menus.find_one(mongoid)
        return paths(menu)

    def get_menus_paths(self, menus):
        paths = []
        for menu in menus:
            paths += self.get_menu_paths(menu['_id'])
        return paths

    def get_client_menus_list(self, client_id):
        '''Gets the list of menus from the client'''
        mongoid = get_mongo_id(client_id)
        return self.db.clients.find_one({'_id': mongoid})['menus']

    def get_client_menus(self, client_id):
        '''Gets all the content of all the menus of the client'''
        menus_list = self.get_client_menus_list(client_id)
        menus = []
        for menu in menus_list:
            mongoid = get_mongo_id(menu)
            menus.append(self.db.menus.find_one({'_id': mongoid}))
            menus[-1]['id'] = str(mongoid)
        return menus

    def get_item(self, item_id):
        '''Get the specified item from the DB'''
        logger.debug('item_id: %s',item_id)
        mongo_id = get_mongo_id(item_id)
        item = self.db.items.find_one({'_id':mongo_id})
        item['id'] = item['_id']
        logger.info('item %s',item)
        return item

    def get_items(self, ids):
        '''get a list of menu items that corresponds to the specified
        ids. If an id is invalid, it will be skipped silently so that
        other valid items can still be retrieved'''
        logger.debug('getting %d items: %s', len(ids), ids)
        mongoids = [get_mongo_id(i) for i in ids]
        logger.debug('fetching %d items from mongo %s',len(mongoids), mongoids)
        items  = self.db.items.find({'_id':{'$in':mongoids}})
        res = []
        for item in sorted(items, key=lambda k:k['name']):
            item['id'] = str(item['_id'])
            res.append(item)
        logger.info('got %d items %s', len(res), res)
        return res

    def toggle_item_availability(self, item_id):
        item_id = get_mongo_id(item_id)
        availability = self.db.items.find_one({'_id': item_id})['available']
        self.db.items.update({'_id': item_id}, {'$set': {'available': not availability}})

    def is_available(self, item_id):
        item_id = get_mongo_id(item_id)
        return self.db.items.find_one({'_id': item_id})['available']

    def get_seats(self, client_id):
        '''Gets the seat property of the client'''
        mongo_id = get_mongo_id(client_id)
        return self.db.clients.find_one({'_id': mongo_id})['seats']

    def get_seats_ids(self, client_id):
        '''Gets the list of seats of the client'''
        mongo_id = get_mongo_id(client_id)
        seats = self.db.clients.find_one({'_id': mongo_id})['seats']
        seats_ids = []
        for i, j in seats.items():
            for k in j['seats']:
                seats_ids.append(k)
        return seats_ids

    def set_seats_quantity(self, client_id, quantity):
        mongo_id = get_mongo_id(client_id)
        seats = ['s' + str(i) for i in xrange(int(quantity))]
        self.db.clients.update({'_id': mongo_id}, {'$set': {'seats': seats}})

    def get_client(self, client_id):
        '''Simply return the client that matches the specified id'''
        # TODO: should log an error if client id doens't exist.
        return self.db.clients.find_one(client_id)

    def get_client_id(self, order_id):
        'Return the client id the specified order belongs to'
        # TODO: what if order_id does not exist or it doesn't contain a client id?
        cid = self.db.orders.find_one(ObjectId(order_id))['client_id']
        return cid

    def get_client_id_by_bill(self, bill_id):
        'Return the client id the specified order belongs to'
        mongo_id = get_mongo_id(bill_id)
        cid = self.db.bills.find_one(mongo_id)['client_id']
        return cid

    def get_client_name(self, client_id):
        '''Get the client name'''
        client_id = get_mongo_id(client_id)
        return self.db.clients.find_one({'_id': client_id})['name']

    def set_client_name(self, client_id, name):
        mongo_id = get_mongo_id(client_id)
        self.db.clients.update({'_id': mongo_id}, {'$set': {'name': name}})

    def get_active_menu_id(self, client_id):
        '''gets the id of the active menu of the client'''
        mongoid = get_mongo_id(client_id)
        return self.db.clients.find_one({'_id': mongoid})['menu']

    def get_active_menu(self, client_id):
        '''Gets the active menu for the specified client ID.'''
        logger.debug('client_id: %s',client_id)
        mongoid = get_mongo_id(client_id)
        mid = self.db.clients.find_one(mongoid)['menu']
        menu = self.db.menus.find_one(mid)
        menu['id'] = str(menu['_id'])
        logger.info('menu:%s',menu)
        return menu

    def get_menu_of_seat(self, client_id, seat_id):
        '''Gets the menu of the room the seat is in'''
        mongoid = get_mongo_id(client_id)
        seats = self.get_client(mongoid)['seats']
        for room in seats:
            valid = seat_id in seats[room]['seats']
            if valid:
                return seats[room]['menu']

    def get_item_path(self, item_id, menu_id):
        item_id = str(item_id)
        menu_id = get_mongo_id(menu_id)
        menu = self.db.menus.find_one({'_id': menu_id})
        pathss = paths(menu)
        for path in pathss:
            section = menu['structure']
            ps = path.split('/')[1:]
            for j in ps:
                section = section[j]
                if item_id in section:
                    return path

    def get_client_items(self, client_id):
        items = list(self.db.items.find({'client_id': client_id}).sort('name'))
        for item in items:
            item['id'] = str(item['_id'])
        return items

    def add_item(self, client_id, name, price, description):
        self.db.items.insert({'client_id': client_id,
                              'name': name,
                              'price': price,
                              'description': description,
                              'photo': False,
                              'available': True})

    def add_menu(self, title, client_id):
        menu_id = self.db.menus.insert({'title': title, 'structure': {}})
        self.db.clients.update({'_id': client_id}, {'$addToSet': {'menus': str(menu_id)}})

    def delete_menu(self, client_id, menu_id):
        mongoid = get_mongo_id(menu_id)
        cmongoid = get_mongo_id(client_id)
        self.db.menus.remove({'_id': mongoid})
        self.db.clients.update({'_id': cmongoid}, {'$pull': {'menus': str(mongoid)}})

    def del_item(self, client_id, item_id):
        '''Deletes items from the db and the structures of menus'''
        client_id = get_mongo_id(client_id)
        item_id = get_mongo_id(item_id)
        self.remove_item_from_client_menus_structure(client_id, item_id)
        self.db.items.remove({'_id': item_id})

    def remove_item_from_client_menus_structure(self, client_id, item_id):
        '''Removes items from the structure of the menus of the client'''
        menus = self.get_client_menus(client_id)
        for menu in menus:
            menu_structure = str(menu['structure'])
            rcol = "u'%s'," % item_id
            lcol = ", u'%s'" % item_id
            last = "[u'%s']" % item_id
            if rcol in menu_structure:
                menu_structure = menu_structure.replace(rcol, '')
            if lcol in menu_structure:
                menu_structure = menu_structure.replace(lcol, '')
            if last in menu_structure:
                menu_structure = menu_structure.replace(last, '[]')
            menu_structure = eval(menu_structure)
            self.update_menu_structure(str(menu['_id']), menu_structure)

    def add_section(self, client_id, name, has_subsections, inside):
        '''adds a new section to the active menu of the client
        name(string) = name of the section to insert,
        has_subsection(boolean) = True if its going to have subsections inside,
                                  False if its going to have items inside,
        inside(string) = where inside the menu structure is going to add the section'''
        #TODO: make it work with any chosen menu, not only the active menu,
        #   find a generic way to set the 'path' of the item to be inserted
        menu_id = self.get_menu_id(client_id)
        if has_subsections:
            if inside:
                self.db.menus.update({'_id': menu_id}, {'$set': { "structure." + str(inside) + "." + str(name) : {} }})
            else:
                self.db.menus.update({'_id': menu_id}, {'$set': { "structure." + str(name) : {} }})
        else:
            if inside:
                self.db.menus.update({'_id': menu_id}, {'$set': { "structure." + str(inside) + "." + str(name) : [] }})
            else:
                self.db.menus.update({'_id': menu_id}, {'$set': { "structure." + str(name) : [] }})

    def del_section(self, client_id, name, inside):
        '''deletes a section from the menu structure
        name(string) = name of the section to be deleted,
        inside(string) = path of the section to be deleted'''
        #TODO: make it work with any chosen menu, not only the active menu,
        #   find a generic way to set the 'path' of the item to be inserted
        menu_id = self.get_menu_id(client_id)
        if inside:
            self.db.menus.update({'_id': menu_id}, {'$unset': { "structure." + str(inside) + "." + str(name): [] }})
        else:
            self.db.menus.update({'_id': menu_id}, {'$unset': { "structure." + str(name): [] }})

    def insert_item(self, client_id, item_id, section):
        '''puts a item inside a section in the menu structure
        item_id(string) = id of the item to be inserted
        section(string) = path of the section where the item is going to be inserted'''
        #TODO: make it work with any chosen menu, not only the active menu,
        #   find a generic way to set the 'path' of the item to be inserted
        menu_id = self.get_menu_id(client_id)
        self.db.menus.update({'_id': menu_id}, {'$addToSet': { "structure." + str(section) : item_id}})

    def remove_item(self, client_id, item_id, section):
        '''pulls a item from a section
        item_id(string) = id of the item to be pulled
        section(string) = path of the section where the item is going to be pulled from'''
        #TODO: make it work with any chosen menu, not only the active menu,
        #   find a generic way to set the 'path' of the item to be inserted
        menu_id = self.get_menu_id(client_id)
        self.db.menus.update({'_id': menu_id}, {'$pull': { "structure." + str(section): item_id}})

    def add_contact(self, contact):
        new_contact = {'name': contact['name'],'email': contact['email'],
                       'phone': contact['phone'],'msg': contact['msg']}
        self.db.contacts.insert(new_contact)

    def add_order(self, item_id, quantity, comment, client_id, seat_id, menu_id, path, bill_n):
        # TODO: Orders will need to have an array of events. Each
        # event will have a server_id, a timestamp and an action so
        # the order history can be traced and troubleshooted easily.
        logger.info({'item':item_id, 'qty':quantity, 'client':client_id, 'seat':seat_id})
        client_id = get_mongo_id(client_id)
        item_id = get_mongo_id(item_id)
        bill_status = self.get_bill_status_w_cid_bn(client_id, bill_n)
        order = {'client_id':client_id, 'seat_id':seat_id, 'item_id':item_id, 'quantity':quantity,
                 'status':self.ORDER_PLACED, 'menu_id': menu_id, 'path': path, 'bill_number': bill_n,
                 'comment': comment, 'bill_status': bill_status, 'createdAt': datetime.datetime.utcnow()}
        order_id = self.db.orders.insert(order)
        self.db.bills.update({'client_id': client_id, 'bill_number': bill_n}, {'$addToSet': {'orders': order_id}, '$set': {'seat': seat_id}})

    def get_bill_status(self, bill_id):
        return self.db.bills.find_one({'_id': bill_id})['status']

    def get_bill_status_w_cid_bn(self, client_id, bill_n):
        mongoid = get_mongo_id(client_id)
        return self.db.bills.find_one({'client_id': mongoid, 'bill_number': bill_n})['status']

    def get_bill(self, bill_id):
        mongoid = get_mongo_id(bill_id)
        bill = self.db.fills.find_one({'_id': mongoid})
        bill['id'] = bill['_id']
        return bill

    def request_bill(self, bill_id):
        mongoid = get_mongo_id(bill_id)
        self.db.bills.update({'_id': mongoid},{'$set':{'status': self.BILL_REQUESTED}})
        for order_id in self.db.bills.find_one({'_id': mongoid})['orders']:
            self.db.orders.update({'_id': order_id}, {'$set':{'bill_status': self.BILL_REQUESTED}})

    def update_bill(self, bill_id, new_status, comment):
        mongoid = get_mongo_id(bill_id)
        self.db.bills.update({'_id': mongoid},{'$set':{'status': new_status, 'comment': comment}})
        for order_id in self.db.bills.find_one({'_id': mongoid})['orders']:
            self.db.orders.update({'_id': order_id}, {'$set':{'bill_status': new_status}})

    def list_bills(self, client_id, query={}):
        query['client_id'] = get_mongo_id(client_id)
        if 'status' in query and type(query['status']) in (tuple, list):
            query['status'] = {'$in':query['status']}
        if 'seat' in query and type(query['seat']) in (tuple, list):
            query['seat'] = {'$in':query['seat']}
        bills = self.db.bills.find(query)
        res = []
        for bill in bills:
            bill['id'] = str(bill['_id'])
            res.append(bill)

        return res


    def list_orders(self, client_id, query={}):
        '''Lists orders for the specified client matched by the given
        query. If query is not given, all orders in _placed_ status
        for the given client will be returned'''
        logger.debug('client_id: %s, query: %s', client_id, query)
        # TODO: move all field names to variables so this won't have
        # to change so dramatically whenever there's a schema change
        query['client_id'] = get_mongo_id(client_id)
        if 'status' in query and type(query['status']) in (tuple, list):
            query['status'] = {'$in':query['status']}
        if 'bill_status' in query and type(query['bill_status']) in (tuple, list):
            query['bill_status'] = {'$in':query['bill_status']}
        if 'seat_id' in query and type(query['seat_id']) in (tuple, list):
            query['seat_id'] = {'$in':query['seat_id']}
        if 'path' in query and type(query['path']) in (tuple, list):
            query['path'] = {'$in':query['path']}
        if 'menu_id' in query and type(query['menu_id']) in (tuple, list):
            query['menu_id'] = {'$in':query['menu_id']}
        orders = self.db.orders.find(query)
        res = []
        names = {}
        prices = {}
        for order in orders:
            order['id'] = str(order['_id'])
            iid = order['item_id']
            if iid in names:
                order['item_name'] = names[iid]
            else:
                order['item_name'] = names[iid] = self.get_item_name(iid)
            if iid in prices:
                order['price'] = prices[iid]
            else:
                order['price'] = prices[iid] = self.get_item_price(iid)
            order['delay'] = compute_delay(order)
            res.append(order)
        logger.info('orders: %s',res)
        return res

    def orderid_sub_total(self, oids):
        statii = (self.ORDER_PLACED, self.ORDER_PREPARING, self.ORDER_PREPARED, self.ORDER_SERVED)
        price = {}
        stotal = 0
        for oid in oids:
            order = self.db.orders.find_one({'_id': oid})
            iid = get_mongo_id(order['item_id'])
            if iid in price:
                order['price'] = price[iid]
            else:
                order['price'] = price[iid] = self.db.items.find_one({'_id': iid})['price']
            if order['status'] in statii:
                stotal += (int(order['quantity']) * float(order['price']))
        return stotal

    def orders_sub_total(self, orders):
        sub_total = 0
        for order in orders:
            sub_total += (int(order['quantity']) * float(order['price']))
        return sub_total

    def list_order_json(self, client_id, query={}):
        orders = self.list_orders(client_id, query=query)
        json_list = {'orders': []}
        for order in orders:
            json_list['orders'].append(json.dumps(order, sort_keys=True, default=json_util.default))
        return json.dumps(json_list)

    def get_item_name(self, item_id):
        'Simply get the item name for the given item ID'
        logger.info('item_id: %s', item_id)
        ans = self.db.items.find_one(item_id)['name']
        logger.info('name: %s', ans)
        return ans

    def get_item_price(self, item_id):
        price = self.db.items.find_one(item_id)['price']
        return price

    def get_order(self, order_id):
        '''Returns the order object that matches the given id. Adds
        the name of the item in the order as well as its delay as
        these two are almost always needed'''
        oid = get_mongo_id(order_id)
        order = self.db.orders.find_one(oid)
        order['item_name'] = self.get_item_name(order['item_id'])
        order['delay'] = compute_delay(order)
        order['id'] = str(order['_id'])
        return order

    def get_bill(self, bill_id):
        mongoid = get_mongo_id(bill_id)
        bill = self.db.bills.find_one(mongoid)
        bill['id'] = bill['_id']
        return bill

    def update_order(self, order_id, update):
        'Updates the status of the specified order. Returns the new status of the order.'
        current_status = self.db.orders.find_one({'_id':ObjectId(order_id)})['status']
        if update['status'] != current_status:
            update['update'] = time.time()
        res = self.db.orders.find_and_modify({'_id':ObjectId(order_id)},{'$set': update}, new=True)
        return res['status']

    def update_orders(self, ids, status):
        '''Updates multiple orders by updating their attributes as specified in the input dictionary.
        Returns the IDs of the orders that failed to be updated if any.'''
        oids = [ObjectId(i) for i in ids]
        res = self.db.orders.update({'_id':{'$in':oids}},{'$set':{'status':status, 'update':time.time()}}, multi=True)
        logger.info('updated {} orders. Errors: {}.'.format(res['n'], res['err']))
        return res

    def is_valid_seat(self, client_id, seat_id):
        '''Returns whether the given seat id belongs the the given
        client id'''
        client_id = get_mongo_id(client_id)
        try:
            seats = self.get_client(client_id)['seats']
        except Exception as e:
            logger.exception('Error validating seat',e)
            return False
        for room in seats:
            valid = seat_id in seats[room]['seats']
            if valid:
                return valid
        return False

    def update_menu_structure(self, menu_id, structure):
        'Updates de structure of the menu'
        mongoid = get_mongo_id(menu_id)
        self.db.menus.update({'_id': mongoid}, {'$set': {'structure': structure}})

    def update_menu_title(self, menu_id, title):
        'Updates de title of the menu'
        logger.debug({'menu_id':menu_id,'title':title})
        mongoid = get_mongo_id(menu_id)
        self.db.menus.update({'_id': mongoid}, {'$set': {'title': title}})

    def update_active_menu(self, client_id, menu_id):
        'Sets the new active menu'
        self.db.clients.update({'_id': client_id}, {'$set': {'menu': menu_id}})

    def update_item(self, item_id, name = 'name', price = 'price', description = 'description'):
        'Updates the item properties'
        if len(item_id) > 10:
            #Mongo id
            self.db.items.update({'_id': ObjectId(item_id)}, {'$set': {'name': name, 'price': price, 'description': description}})
        else:
            #Bootstrapped id
            self.db.items.update({'_id': item_id}, {'$set': {'name': name, 'price': price, 'description': description}})

    def set_item_photo(self, item_id):
        i_id = get_mongo_id(item_id)
        self.db.items.update({'_id': i_id}, {'$set': {'photo': True}})

    def add_room(self, client_id, menu_id, room_name):
        'Add a new room to the client'
        clientid = get_mongo_id(client_id)
        menuid = get_mongo_id(menu_id)
        seats = self.db.clients.find_one({'_id': clientid})['seats']
        seats[room_name] = {'menu': menuid, 'seats': []}
        self.db.clients.update({'_id': clientid}, {'$set': {'seats': seats}})

    def del_room(self, client_id, room_name):
        'Removes a room from the client'
        clientid = get_mongo_id(client_id)
        seats = self.db.clients.find_one({'_id': clientid})['seats']
        del seats[room_name]
        self.db.clients.update({'_id': clientid}, {'$set': {'seats': seats}})

    def set_room_menu(self, client_id, menu_id, room_name):
        'Sets the menu of a room'
        clientid = get_mongo_id(client_id)
        menuid = get_mongo_id(menu_id)
        seats = self.db.clients.find_one({'_id': clientid})['seats']
        seats[room_name]['menu'] = menuid
        self.db.clients.update({'_id': clientid}, {'$set': {'seats': seats}})

    def add_seat(self, client_id, room_name, seat_name):
        'Adds a new seat to a room'
        clientid = get_mongo_id(client_id)
        seats = self.db.clients.find_one({'_id': clientid})['seats']
        seats[room_name]['seats'].append(seat_name)
        self.db.clients.update({'_id': clientid}, {'$set': {'seats': seats}})

    def del_seat(self, client_id, room_name, seat_name):
        'Deletes a seat from a room'
        clientid = get_mongo_id(client_id)
        seats = self.db.clients.find_one({'_id': clientid})['seats']
        seats[room_name]['seats'].remove(seat_name)
        self.db.clients.update({'_id': clientid}, {'$set': {'seats': seats}})

# Helper methods. The functions below are not part of the 'interface'
# and need not be implemented by other OrdersDAO
# implementations. These are what would be 'private' and perhaps
# 'static' methods in other OO languages
def compute_delay(mongo_obj):
    '''Computes how long ago the given mongo document was stored
    in the DB. It extracts the timestamp from the object ID and
    compares with the current time to determine how many seconds
    ago the object was created. Returns a simple human readable
    string that shows how long ago in seconds, minutes, hours or
    days ago the object was created'''
    if str(mongo_obj['status']) == '_placed_':
        timestamp = int(str(mongo_obj['_id'])[:8],16)
        now = datetime.datetime.utcnow()
        delta = now - datetime.datetime.utcfromtimestamp(timestamp)
        secs = int(delta.total_seconds())
    else:
        secs = int(time.time() - mongo_obj['update'])
    units = ((24*60*60,' day'),(60*60,' hr'),(60,' min'),(1,' sec'))
    idx = 0
    while secs < units[idx][0]:
        idx += 1
        if idx == 4:
            idx -= 1
            break
    qty = secs // units[idx][0]
    ans = str(qty) + units[idx][1]
    if qty > 1:
        ans += 's'
    return ans + ' ago'

def get_mongo_id(iid):
    logger.debug('id: %s',iid)
    try:
        mongo_id = ObjectId(iid)
    except pymongo.errors.InvalidId:
        logger.warn('could not convert id %s to ObjectId',iid)
        mongo_id = iid
    logger.info('mongo_id: %s',mongo_id)
    return mongo_id

def paths(data, name='', path=[], parent=''):
    if 'structure' in data:
        paths_name = []
        for child in data['structure']:
            temp = paths(data['structure'][child], name=child)
            if type(temp) is list:
                paths_name += temp
            else:
                paths_name.append(temp)
        return paths_name
    elif type(data) is dict:
        if parent != '': path.append(parent)
        parent += '/' + name
        p = []
        for child in data:
            temp = paths(data[child], name=child, path=path, parent=parent)
            if type(temp) is list:
                p += temp
            else:
                p.append(temp)
        return p
    elif type(data) is list:
        return parent + '/' + name
