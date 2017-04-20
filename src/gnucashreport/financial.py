from datetime import date

import warnings
import math

# from gnucashreport.scipy import newton
from decimal import Decimal


# Newton-Raphson method
# From scipy. Use only secant method. Cuted function to secant method
# def newton(func, x0, fprime=None, args=(), tol=1.48e-8, maxiter=50, fprime2=None):
def newton(func, x0, args=(), tol=1.48e-8, maxiter=50):
    """
    Find a zero using the Newton-Raphson or secant method.

    Find a zero of the function `func` given a nearby starting point `x0`.
    The Newton-Raphson method is used if the derivative `fprime` of `func`
    is provided, otherwise the secant method is used.  If the second order
    derivate `fprime2` of `func` is provided, parabolic Halley's method
    is used.

    Parameters
    ----------
    func : function
        The function whose zero is wanted. It must be a function of a
        single variable of the form f(x,a,b,c...), where a,b,c... are extra
        arguments that can be passed in the `args` parameter.
    x0 : float
        An initial estimate of the zero that should be somewhere near the
        actual zero.
    fprime : function, optional
        The derivative of the function when available and convenient. If it
        is None (default), then the secant method is used.
    args : tuple, optional
        Extra arguments to be used in the function call.
    tol : float, optional
        The allowable error of the zero value.
    maxiter : int, optional
        Maximum number of iterations.
    fprime2 : function, optional
        The second order derivative of the function when available and
        convenient. If it is None (default), then the normal Newton-Raphson
        or the secant method is used. If it is given, parabolic Halley's
        method is used.

    Returns
    -------
    zero : float
        Estimated location where function is zero.

    See Also
    --------
    brentq, brenth, ridder, bisect
    fsolve : find zeroes in n dimensions.

    Notes
    -----
    The convergence rate of the Newton-Raphson method is quadratic,
    the Halley method is cubic, and the secant method is
    sub-quadratic.  This means that if the function is well behaved
    the actual error in the estimated zero is approximately the square
    (cube for Halley) of the requested tolerance up to roundoff
    error. However, the stopping criterion used here is the step size
    and there is no guarantee that a zero has been found. Consequently
    the result should be verified. Safer algorithms are brentq,
    brenth, ridder, and bisect, but they all require that the root
    first be bracketed in an interval where the function changes
    sign. The brentq algorithm is recommended for general use in one
    dimensional problems when such an interval has been found.

    """
    if tol <= 0:
        raise ValueError("tol too small (%g <= 0)" % tol)
    if maxiter < 1:
        raise ValueError("maxiter must be greater than 0")

    # Secant method
    p0 = x0
    if x0 >= 0:
        p1 = x0*(1 + 1e-4) + 1e-4
    else:
        p1 = x0*(1 + 1e-4) - 1e-4
    q0 = func(*((p0,) + args))
    q1 = func(*((p1,) + args))
    for iter in range(maxiter):
        if q1 == q0:
            if p1 != p0:
                msg = "Tolerance of %s reached" % (p1 - p0)
                warnings.warn(msg, RuntimeWarning)
            return (p1 + p0)/2.0
        else:
            p = p1 - q1*(p1 - p0)/(q1 - q0)
        if abs(p - p1) < tol:
            return p
        p0 = p1
        q0 = q1
        p1 = p
        q1 = func(*((p1,) + args))
    msg = "Failed to converge after %d iterations, value is %s" % (maxiter, p)
    raise RuntimeError(msg)



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

    chron_order = sorted(cashflows, key = lambda x: x[0])
    t0 = chron_order[0][0] #t0 is the date of the first cash flow

    return sum([cf/(1+rate)**((t-t0).days/365.0) for (t,cf) in chron_order])



def xirr(cashflows, guess=0.00001):
    """
    Rigth!
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
    
    >>> tas_10 = [(date(2016, 1, 1), -10000),\
           (date(2016, 12, 31), 11000)]
    >>> xirr(tas_10)
    0.1
    
    >>> tas = [ (date(2016, 1, 1), -10000),\
        (date(2016, 1, 1), 10000),\
        (date(2016, 12, 31), -11000),\
        (date(2016, 12, 31), 11000)]
    >>> xirr(tas)
    0

    """
    
    # return secant_method(0.0001, lambda r: xnpv(r, cashflows), guess)
    # return newton(lambda r: xnpv(r,cashflows), guess)

    # Нулевая доходность
    s = sum([pair[1] for pair in cashflows])
    if s == 0:
        return 0

    res = newton(lambda r: xnpv(r, cashflows), guess)

    return round(res, 4)


    # version from http://stackoverflow.com/questions/8919718/financial-python-library-that-has-xirr-and-xnpv-function
    # try:
    #     return optimize.newton(lambda r: xnpv(r, cashflows), 0.0)
    # except RuntimeError:  # Failed to converge?
    #     return optimize.brentq(lambda r: xnpv(r, cashflows), -1.0, 1e10)

# http://stackoverflow.com/questions/8919718/financial-python-library-that-has-xirr-and-xnpv-function
def xirr_simple(transactions, guess=0.00001):
    """
    WRONG!
    Calculate the Internal Rate of Return of a series of cashflows at irregular intervals.
    Like excel xirr function

    :param transactions: a list object in which each element is a tuple of the form (date, amount),
           where date is a python datetime.date object and amount is an integer or floating point number.
           Cash outflows (investments) are represented with negative amounts,
           and cash inflows (returns) are positive amounts.
    :param guess: (optional, default = 0.1):
           a guess at the solution to be used as a starting point for the numerical solution.
    :return: Returns the IRR as a single value

    # >>> tas = [ (date(2010, 12, 29), -10000),\
    #     (date(2012, 1, 25), 20),\
    #     (date(2012, 3, 8), 10100)]
    # >>> xirr_simple(tas)
    # Decimal('0.010061264038085993569663582')
    
    # >>> tas = [ (date(2016, 1, 1), -10000),\
    #     (date(2016, 1, 1), 10000),\
    #     (date(2016, 12, 31), -11000),\
    #     (date(2016, 12, 31), 11000)]
    # >>> xirr_simple(tas)
    # Decimal('0')

    """
    years = [Decimal((ta[0] - transactions[0][0]).days / 365.0) for ta in transactions]
    residual = 1
    step = Decimal(0.05)
    # guess = 0.05
    guess = Decimal(guess)
    epsilon = Decimal(0.0001)
    limit = 10000
    while abs(residual) > epsilon and limit > 0:
        limit -= 1
        residual = Decimal(0.0)
        for i, ta in enumerate(transactions):
            residual += ta[1] / pow(guess, years[i])
        if abs(residual) > epsilon:
            if residual > 0:
                guess += step
            else:
                guess -= step
                step /= Decimal(2.0)
    return guess-1



def xirr_float(transactions):
    """
    
    # >>> tas = [ (date(2010, 12, 29), -10000),\
    #     (date(2012, 1, 25), 20),\
    #     (date(2012, 3, 8), 10100)]
    # >>> xirr_float(tas)
    # 0.010061264038086382
    
    # >>> tas = [ (date(2016, 1, 1), -10000),\
    #     (date(2016, 1, 1), 10000),\
    #     (date(2016, 12, 31), -11000),\
    #     (date(2016, 12, 31), 11000)]
    # >>> xirr_float(tas)
    # 0

    
    :param transactions: 
    :return: 
    """


    years = [(ta[0] - transactions[0][0]).days / 365.0 for ta in transactions]
    residual = 1
    step = 0.005
    guess = 0.0001
    epsilon = 0.000001
    limit = 100000
    while abs(residual) > epsilon and limit > 0:
        limit -= 1
        residual = 0.0
        for i, ta in enumerate(transactions):
            residual += ta[1] / pow(guess, years[i])
        if abs(residual) > epsilon:
            if residual > 0:
                guess += step
            else:
                guess -= step
                # step /= 2.0
    return guess-1


def secant_method(tol, f, x0):
    """
    Wrong?!
    Solve for x where f(x)=0, given starting x0 and tolerance.

    Arguments
    ----------
    tol: tolerance as percentage of final result. If two subsequent x values are with tol percent, the function will return.
    f: a function of a single variable
    x0: a starting value of x to begin the solver

    Notes
    ------
    The secant method for finding the zero value of a function uses the following formula to find subsequent values of x. 

    x(n+1) = x(n) - f(x(n))*(x(n)-x(n-1))/(f(x(n))-f(x(n-1)))

    Warning 
    --------
    This implementation is simple and does not handle cases where there is no solution. Users requiring a more robust version should use scipy package optimize.newton.

    """

    x1 = x0 * 1.1
    while (abs(x1 - x0) / abs(x1) > tol):
        x0, x1 = x1, x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
    return x1

def xirr_ruby(cashflow):
    # Wrong!!!


    # data = cashflow.zip(dates)

    # Bisection method finding the rate to zero nfv

    left = -0.99/365
    right = 9.99/365
    epsilon = 1e-8
    while math.fabs(right-left) > 2 * epsilon:

        midpoint = (right+left)/2

        # if xnpv(left, cashflow) * xnpv(midpoint, cashflow) > 0:
        if xnpv(left, cashflow) * xnpv(right, cashflow) > 0:

            left = midpoint

        else:

            right = midpoint





    # Irr for daily cashflow (not in percentage format)
    irr = (right+left) / 2
    # Irr for daily cashflow multiplied by 365 to get yearly return
    irr = irr * 365
    # Annualized yield (return) reflecting compounding effect of daily returns

    # irr = (1 + irr / 365) ^ 365 – 1
    # irr = (1 + irr / 365) ^ 365 – 1
    irr = math.pow(1 + irr / 365, 365) - 1

    return irr


# Ruby XIRR
#https://puneinvestor.wordpress.com/2013/10/01/calculate-xirr-in-ruby-bisection-method/

# def xirr(cashflow, dates)
#
    # if cashflow.length != dates.length
    #
        # abort(“length(cashflow) not equal to length(dates)”)
    #
    # else
    #
        # nil
    #
    # end
    #
    # data = cashflow.zip(dates)
    #
    # # Bisection method finding the rate to zero nfv
    #
    # left = -0.99/365
    # right = 9.99/365
    # epsilon = 1e-8
    # while ((right-left).abs > 2*epsilon) do
    #
        # midpoint = (right+left)/2
        #
        # if (nfv(data, left) * nfv(data, midpoint) > 0)
        #
            # left = midpoint
        #
        # else
        #
            # right = midpoint
        #
        # end
    #
    # end
    #
    # # Irr for daily cashflow (not in percentage format)
    # irr = (right+left) / 2
    # # Irr for daily cashflow multiplied by 365 to get yearly return
    # irr = irr * 365
    # # Annualized yield (return) reflecting compounding effect of daily returns
    # irr = (1 + irr / 365) ** 365 – 1
    #
    # return irr

# end Ruby XIRR


if __name__ == "__main__":
    # Example
    tas = [(date(2016, 1, 1), -10000),
               (date(2016, 1, 1), 10000),
               (date(2016, 12, 31), -11000),
               (date(2016, 12, 31), 11000)]

    tas_10 = [(date(2016, 1, 1), -10000),
           (date(2016, 12, 31), 11000)]

    # x_ruby = xirr_ruby(tas_10)
    x_simple = xirr_simple(tas, guess=0.00001)
    x = Decimal(xirr(tas_10, guess=0.00001))
    # print(x_ruby)
    # print(x_simple)
    print(round(x, 4))

    # print(xirr(tas)) #0.0100612651650822
    # print(xirr_simple(tas)) #0.010061264038086382