class OrdersDAO:
    # order statii
    ORDER_PLACED = '_placed_'
    ORDER_CANCELED = '_canceled_'
    ORDER_PREPARING = '_preparing_'
    ORDER_PREPARED = '_prepared_'
    ORDER_SERVED = '_served_'
    ORDER_RETURNED = '_returned_'

    ORDER_STATII = (ORDER_PLACED,
                    ORDER_CANCELED,
                    ORDER_PREPARING,
                    ORDER_PREPARED,
                    ORDER_SERVED,
                    ORDER_RETURNED)

    # bill statii
    BILL_NOT_VERIFIED = '_not verified_'
    BILL_VERIFIED = '_verified_'
    BILL_IGNORED = '_ignored_'
    BILL_REQUESTED = '_bill requested_'
    BILL_PAID = '_paid_'

    BILL_STATII = (BILL_NOT_VERIFIED,
                   BILL_VERIFIED,
                   BILL_IGNORED,
                   BILL_REQUESTED,
                   BILL_PAID)
