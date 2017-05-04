from datetime import date

import warnings
import math

# from gnucashreport.scipy import newton
from decimal import Decimal, ROUND_HALF_UP


def bisection(funct, args=(), left_x=-0.99999, right_x=100, tol=0.00001, maxiter=1000):
    """
    Find a zero using the bisection method
    :param funct: function
        The function whose zero is wanted. It must be a function of a
        single variable of the form f(x,a,b,c...), where a,b,c... are extra
        arguments that can be passed in the `args` parameter.
    :param left_x: 
    :param right_x: 
    :param args: tuple, optional
        Extra arguments to be used in the function call.
    :param tol: : float, optional
        The allowable error of the zero value.
    :param maxiter: int, optional
        Maximum number of iterations.
    :return: : float
        Estimated location where function is zero.
    """
    # Сбой пойдет если решение лежит за left или за right
    # Моя вставка
    func_left = funct(*((left_x,) + args))
    func_right = funct(*((right_x,) + args))
    # Если у результатов функции знак одинаковый, то это выход за пределы диапазона left_x - right_x
    # if func_left * func_right > 0:
    if (func_left > 0) and (func_right > 0) or (func_left < 0) and (func_right < 0):
        if func_left > 0:
            warnings.warn('exceeded upper threshold {}'.format(right_x))
            # print('exceeded upper threshold {}'.format(right_x))
            return right_x
        else:
            warnings.warn('exceeded the lower threshold {}'.format(left_x))
            # print('exceeded the lower threshold {}'.format(left_x))
            return left_x
    # Конец моей вставки
    # start_left_x = left_x
    # start_right_x = right_x
    mid_x = (left_x + right_x) / 2.0
    for iter in range(maxiter):
    # while (right_x - left_x) / 2.0 > tol and maxiter > 0:
    #     maxiter -= 1

        func_left = funct(*((left_x,) + args))
        # func_right = funct(*((right_x,) + args))
        func_mid = funct(*((mid_x,) + args))

        if func_mid == 0:
            return mid_x
        # elif func_left * func_mid < 0:
        # Проверка, что func_left и func_mid имеют разные знаки
        elif (func_left > 0) and (func_mid < 0) or (func_left < 0) and (func_mid > 0):
            right_x = mid_x
        else:
            left_x = mid_x
        mid_x = (left_x + right_x) / 2.0

        if (right_x - left_x) / 2.0 < tol:
            return mid_x
    print('Failed to converge after {} iterations'.format(maxiter))
    return mid_x


def xnpv(rate, cashflows):
    """
    Calculate the net present value of a series of cashflows at irregular intervals.

    Arguments
    ---------
    * rate: the discount rate to be applied to the cash flows
    * cashflows: a list object in which each element is a tuple of the form (date, amount), where date is a python datetime.date object and amount is an integer or floating point number. Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
    
    Returns
    -------
    * returns a single value which is the NPV of the given cash flows.

    Notes
    ---------------
    * The Net Present Value is the sum of each of cash flows discounted back to the date of the first cash flow. The discounted value of a given cash flow is A/(1+r)**(t-t0), where A is the amount, r is the discout rate, and (t-t0) is the time in years from the date of the first cash flow in the series (t0) to the date of the cash flow being added to the sum (t).  
    * This function is equivalent to the Microsoft Excel function of the same name. 

    """

    # chron_order = sorted(cashflows, key = lambda x: x[0])
    # optimization !?
    # chron_order = cashflows
    t0 = cashflows[0][0] #t0 is the date of the first cash flow

    # Иногда возвращает комплексное число
    return sum([cf/(1+rate)**((t-t0).days/365.0) for (t, cf) in cashflows])


def xirr(cashflows, for_decimal=True):
    """
    Right!
    Calculate the Internal Rate of Return of a series of cashflows at irregular intervals.

    Arguments
    ---------
    * cashflows: a list object in which each element is a tuple of the form (date, amount), where date is a python datetime.date object and amount is an integer or floating point number. Cash outflows (investments) are represented with negative amounts, and cash inflows (returns) are positive amounts.
    * guess: (optional, default = 0.1): a guess at the solution to be used as a starting point for the numerical solution.

    Returns
    --------
    * Returns the IRR as a single value
    
    Notes
    ----------------
    * The Internal Rate of Return (IRR) is the discount rate at which the Net Present Value (NPV) of a series of cash flows is equal to zero. The NPV of the series of cash flows is determined using the xnpv function in this module. The discount rate at which NPV equals zero is found using the secant method of numerical solution. 
    * This function is equivalent to the Microsoft Excel function of the same name.
    * For users that do not have the scipy module installed, there is an alternate version (commented out) that uses the secant_method function defined in the module rather than the scipy.optimize module's numerical solver. Both use the same method of calculation so there should be no difference in performance, but the secant_method function does not fail gracefully in cases where there is no solution, so the scipy.optimize.newton version is preferred.

    # >>> tas = [ (date(2010, 12, 29), -10000),\
    #     (date(2012, 1, 25), 20),\
    #     (date(2012, 3, 8), 10100)]
    # >>> xirr(tas)
    # 0.0100612651650822
    
    >>> tas_10 = [(date(2016, 1, 1), -10000.0),\
           (date(2016, 12, 31), 11000.0)]
    >>> round(xirr(tas_10, for_decimal=False), 4)
    0.1
    
    >>> tas = [ (date(2016, 1, 1), -10000.0),\
        (date(2016, 1, 1), 10000.0),\
        (date(2016, 12, 31), -11000.0),\
        (date(2016, 12, 31), 11000.0)]
    >>> xirr(tas, for_decimal=False)
    0.0
    
    >>> tas_6161 = [ (date(2016, 1, 1), -9900.0),\
        (date(2016, 1, 1), -100.0),\
        (date(2016, 6, 1), 500.0),\
        (date(2016, 12, 1), 15000.0),\
        (date(2016, 12, 1), -100.0)]
    >>> round(xirr(tas_6161, for_decimal=False), 4)
    0.6161
    
    # Example don't work
    >>> tas = [ (date(2009, 1, 1), Decimal('-274.4')),\
        (date(2011, 4, 12), Decimal('-6512.4')),\
        (date(2012, 9, 10), Decimal('4330'))]
    >>> round(xirr(tas), 4)
    Decimal('-0.2613')
    
    >>> tas_cred_real = [(date(2014, 4, 3), Decimal('66000')),\
                (date(2014, 4, 5), Decimal('-9934.9')),\
                (date(2014, 4, 5), Decimal('-65.1')),\
                (date(2014, 4, 24), Decimal('-497.67')),\
                (date(2014, 4, 24), Decimal('-44502.33')),\
                (date(2014, 5, 31), Decimal('-148.26')),\
                (date(2014, 5, 31), Decimal('-11562.77'))]
    >>> round(xirr(tas_cred_real), 4)
    Decimal('0.1724')

    """
    
    # Нулевая доходность
    s = sum([pair[1] for pair in cashflows])
    if s == 0:
        if for_decimal:
            return Decimal('0.0')
        else:
            return 0.0

    cashflows_sorted = sorted(cashflows, key=lambda x: x[0])
    if for_decimal:
        # decimal to float
        cashflows_sorted = list((date, float(value)) for date, value in cashflows_sorted )

    res = bisection(lambda r: xnpv(r, cashflows_sorted))
    if for_decimal:
        return Decimal(res)
    else:
        return res


