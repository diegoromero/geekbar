from django import template

register = template.Library()

@register.filter
def four_digits(value):
    v = str(value)
    if len(v) < 4:
        try:
            return "%04d" % value
        except TypeError:
            return "%04d" % int(value)
    elif len(v) > 4:
        return v[-4:]
    else:
        return v
