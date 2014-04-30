from django import template

register = template.Library()

@register.filter(name='four_digits')
def four_digits(value):
    v = str(value)
    if len(v) < 4:
        return "%04d" % value
    elif len(v) > 4:
        return v[-4:]
    else:
        return v
