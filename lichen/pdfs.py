import numpy as np
import scipy as sp
import scipy.stats as stats
import scipy.integrate as integrate

################################################################################
# Exponential 
# The slope is interpreted a negative
################################################################################
def exp(x,slope,xlo,xhi,efficiency=None,num_int_points=100,subranges=None):

    xnorm = np.linspace(xlo,xhi,num_int_points)
    ynorm = np.exp(-slope*xnorm)

    if efficiency!=None:
        ynorm *= efficiency(xnorm)

    normalization = integrate.simps(ynorm,x=xnorm)

    # Subranges of the normalization.
    if subranges!=None:
        normalization = 0.0
        for sr in subranges:
            xnorm = np.linspace(sr[0],sr[1],num_int_points)
            ynorm = np.exp(-slope*xnorm)

            if efficiency!=None:
                ynorm *= efficiency(xnorm)

            normalization += integrate.simps(ynorm,x=xnorm)

    y = np.exp(-slope*x)/normalization

    '''
    if efficiency!=None:
        y *= efficiency(x)
    '''

    return y

################################################################################
# Cos term
################################################################################
def cos(x,frequency,phase,amplitude,offset,xlo,xhi,efficiency=None,num_int_points=100,subranges=None):

    xnorm = np.linspace(xlo,xhi,num_int_points)
    ynorm = offset + amplitude*np.cos(frequency*xnorm + phase)

    if efficiency!=None:
        ynorm *= efficiency(xnorm)

    normalization = integrate.simps(ynorm,x=xnorm)

    # Subranges of the normalization.
    if subranges!=None:
        normalization = 0.0
        for sr in subranges:
            xnorm = np.linspace(sr[0],sr[1],num_int_points)
            #ynorm = np.exp(-slope*xnorm)
            ynorm = offset + amplitude*np.cos(frequency*xnorm + phase)

            if efficiency!=None:
                ynorm *= efficiency(xnorm)

            normalization += integrate.simps(ynorm,x=xnorm)
            #print "building normalization: ", normalization

    #y = np.exp(-slope*x)/normalization
    y = offset + amplitude*np.cos(frequency*x + phase)

    if efficiency!=None:
        y *= efficiency(x)

    return y/normalization


################################################################################
# Gaussian
################################################################################
def gauss(x,mean,sigma,xlo,xhi,efficiency=None,num_int_points=100):

    gauss_func = stats.norm(loc=mean,scale=sigma)

    xnorm = np.linspace(xlo,xhi,num_int_points)
    ynorm = gauss_func.pdf(xnorm)

    if efficiency!=None:
        ynorm *= efficiency(xnorm)

    normalization = integrate.simps(ynorm,x=xnorm)
    
    y = gauss_func.pdf(x)/normalization

    if efficiency!=None:
        y *= efficiency(x)


    return y


################################################################################
# Polynomial
################################################################################
def poly(x,constants,xlo,xhi,efficiency=None,num_int_points=100,subranges=None):

    npts = len(x)

    poly = np.ones(npts)

    xnorm = np.linspace(xlo,xhi,num_int_points)
    ynorm = np.ones(num_int_points)

    for i,c in enumerate(constants):
        poly += c*np.pow(x,(i+1))
        ynorm += c*np.pow(xnorm,(i+1))

    if efficiency!=None:
        ynorm *= efficiency(xnorm)

    normalization = integrate.simps(ynorm,x=xnorm)
    
    # Subranges of the normalization.
    if subranges!=None:
        normalization = 0.0
        for sr in subranges:
            xnorm = np.linspace(sr[0],sr[1],num_int_points)
            ynorm = np.ones(num_int_points)

            for i,c in enumerate(constants):
                ynorm += c*np.pow(xnorm,(i+1))

            if efficiency!=None:
                ynorm *= efficiency(xnorm)

            normalization += integrate.simps(ynorm,x=xnorm)

    '''
    if efficiency!=None:
        poly *= efficiency(x)

    '''
    return poly/normalization




################################################################################
# Linear function
################################################################################
def pdf_linear():
    ret = lambda p, x: p[0]+p[1]*x
    return ret

################################################################################
# Gaussian (normal function)
################################################################################
def pdf_gaussian():
    ret = lambda p, x: (p[0]/p[2])*np.exp(-((x - p[1])**2)/(2.0*p[2]*p[2]))
    return ret

################################################################################
# Adding two PDFs
################################################################################
def pdf_addition(lambda_func_0,lambda_func_1):
    #norm = np.sqrt(p[0]*p[0]+p[1]*p[1])
    ret = lambda p, x: (p[0]**2/np.sqrt(p[0]*p[0]+p[1]*p[1]))*lambda_func_0(p[2:4],x) + (p[1]**2/np.sqrt(p[0]*p[0]+p[1]*p[1]))*lambda_func_1(p[4:7],x)
    return ret

################################################################################
# Chi^2 minimization function.
################################################################################
def chi2_function(fit_function):
    ret = lambda p, x, y: fit_function(p, x)-y
    return ret

################################################################################
# Define function to calculate reduced chi-squared
################################################################################
def red_chi_sq(func, x, y, dy, params):
    resids = y - func(x, *params)
    chisq = ((resids/dy)**2).sum()
    return chisq/float(x.size-params.size)

################################################################################
# Part of a poisson term.
################################################################################
def pois(mu, k):
    ret = -mu + k*np.log(mu)
    return ret


################################################################################
# Extended maximum likelihood function
################################################################################
def extended_maximum_likelihood_function(p, x, y):

    ret = 0

    charges = [[+1,+1], [-1,-1], [+1,-1], [-1,+1]]

    for i in range(0,4):
        q1 = charges[i][0]
        q2 = charges[i][1]

        pars = list(p[0:4])
        pars += [q1,q2]

        #print "Printing pars:"
        #print pars

        norm_func = (pdf_bmixing(y[i],pars)).sum()/len(y)

        #print "norm_func: %f" % (norm_func)

        num = p[4+i] # Number of events in fit

        #print "here"
        #print pars
        #print x[i]
        #print -np.log(pdf_bmixing(x[i],pars))
        #print (-np.log(pdf_bmixing(x[i],pars) / norm_func).sum()) 
        #print pois(num,len(x[i]))

        ret += (-np.log(pdf_bmixing(x[i],pars) / norm_func).sum()) - pois(num,len(x[i]))

        #print "%f  %f" % (ret, norm_func)
    return ret

################################################################################
# Extended maximum likelihood function for minuit
################################################################################
def extended_maximum_likelihood_function_minuit(p):

    x = data[0]
    y = data[1]

    ret = 0

    charges = [[+1,+1], [-1,-1], [+1,-1], [-1,+1]]

    for i in range(0,4):
        q1 = charges[i][0]
        q2 = charges[i][1]

        pars = list(p[0:4])
        pars += [q1,q2]

        #print "Printing pars:"
        #print pars

        norm_func = (pdf_bmixing(y[i],pars)).sum()/len(y)

        #print "norm_func: %f" % (norm_func)

        num = p[4+i] # Number of events in fit

        #print "here"
        #print pars
        #print x[i]
        #print -np.log(pdf_bmixing(x[i],pars))
        #print (-np.log(pdf_bmixing(x[i],pars) / norm_func).sum()) 
        #print pois(num,len(x[i]))

        ret += (-np.log(pdf_bmixing(x[i],pars) / norm_func).sum()) - pois(num,len(x[i]))

        #print "%f  %f" % (ret, norm_func)
    return ret



################################################################################
# Linear function
################################################################################
def pdf_bmixing(deltat,pars):
    
    gamma = pars[0]
    p_over_q = pars[1]
    deltaM = pars[2]
    deltaG = pars[3]
    q1 = pars[4]
    q2 = pars[5]

    qq = q1*q2

    A =  (1/2.0)*(1+qq)*(p_over_q**(2*q1)) + (1/2.0)*(1-qq) # coefficient of cosh term
    B = -(1/2.0)*(1+qq)*(p_over_q**(2*q1)) + (1/2.0)*(1-qq) # coefficient of cos  term
    C = 0.0 # coefficient of sinh term
    D = 0.0 # coefficient of sin  term

    #print "%d %f %f %f %f" % (qq,A,B,C,D)
    
    N = (1.0/4.0)*np.exp(-gamma*np.abs(deltat))*(
            A*np.cosh(deltaG*deltat/2.0)+B*np.cos(deltaM*deltat) +
            C*np.sinh(deltaG*deltat/2.0)+D*np.sin(deltaM*deltat) )

    return N

