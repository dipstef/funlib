# coding=utf-8
from unicoder import encoded, decoded
from funlib import Lambda
from funlib.util import call_string


def main():

    print call_string('test', 1, z='a', b=2)

    def _test_fun(fun):
        try:
            print fun()
        except Exception, e:
            print 'Error', e
        finally:
            print fun
            print str(fun)
            print unicode(fun)

    func = Lambda(encoded,  u'Документ Microsoft Word.doc')
    _test_fun(func)
    _test_fun(Lambda(decoded, func()))

if __name__ == '__main__':
    main()