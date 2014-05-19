from django.shortcuts import render

from orders.settings import dao

DEFAULT_TEMPLATES = {'top_template':'bill_list_filters.html',
                     'item_template':'default_bill_item.html',
                     'bottom_template':'screen_navbar.html'}

#RENDERER
def render_bills(request, client_id, bills):
    template_params = DEFAULT_TEMPLATES.copy()
    template_params['template'] = 'bills.html'
    template_params['searchable'] = True
    template_params['bills'] = bills
    client_name = dao.get_client_name(client_id)
    template_params['client_name'] = client_name
    for bill in bills:
        bill['status'] = bill['status'].replace('_','').capitalize()
        last_order = dao.get_order(bill['orders'][-1])
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        print last_order
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        bill['seat'] = last_order['seat']
        bill['sub_total'] = dao.orderid_sub_total(bill['orders'])
    
    return render(request, 'index_screen_bills.html', template_params)
