def date(target):
    return target.strftime("%d %B %Y, %H:%M")

def number(target):
	if type(target) is not int:
		target = int(target)
	returned =  "{:,}".format(target)
	return str(returned)

def is_owner(ctx):
	return ctx.author.id == 170107897366315009

def is_number(target):
	try:
		float(target)
		return True
	except ValueError:
		return False