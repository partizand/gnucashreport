

# Internalization test

import  gettext
# gettext.bindtextdomain('messages', '/path/to/my/language/directory')
import locale
current_locale, encoding = locale.getdefaultlocale()
# gettext.install('messages', 'c:\\Temp\\andrey\\prog\\gcreports\\locale')
# lang1 = gettext.translation('messages', localedir='c:\\Temp\\andrey\\prog\\gcreports\\locale', languages=[current_locale])
lang1 = gettext.translation('messages', localedir='./gcreports/locale', languages=[current_locale])
lang1.install()
# _ = gettext.gettext

# loc = locale.getdefaultlocale()

# print(loc)

TOTAL_NAME = _("Total")
animal = _("lamb")

print((_('{} had a little {}').format(TOTAL_NAME, animal)))