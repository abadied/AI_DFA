#include "utilities.hpp"
// For Accumulators
#ifdef USE_BOOST
#include <boost/accumulators/accumulators.hpp>
// To calculate mean and variance for an accumulator
#include <boost/accumulators/statistics.hpp>
#endif

// Scores of Zalpha for alpha = {0.05, 0.025, 0.01}
//   from the Zscore table
#define Z_FOR_ALPHA_05  1.645
#define Z_FOR_ALPHA_025 1.96
#define Z_FOR_ALPHA_01  2.33

using namespace std;

#if defined(__GNUC__)
#include <dirent.h>
#else
#include <windows.h>
#endif

/**
 * Create a direcotry.
 * @param path The path of the new directory.
 * @return True for success, False for failure.
 */
bool create_directory(const string &path)
{
    int error_num = 0;
#if defined(_WIN32) && defined(__GNUC__)
// can be used on Windows
    error_num = _mkdir(path.c_str());
#elif defined (_WIN32)
	CreateDirectoryA(path.c_str(), NULL);
#else
    // UNIX style permissions
    mode_t nMode = 0733;
    // can be used on non-Windows
    error_num = mkdir(path.c_str(), nMode);
#endif
    if (error_num != 0) {
        cerr << "ERROR: Failed to create directory!"
             << endl;
        return false;
    }
    return true;
}

string int_to_str(int a)
{
    ostringstream temp;
    temp << a;
    return temp.str();
}

int str_to_int(const string &str)
{
    istringstream is(str);
    int n = 0;
    while (is) {
        is >> n;
    }
    return n;
}

string to_string(char c)
{
    stringstream ss;
    string s;
    ss << c;
    ss >> s;
    return s;
}

string to_string(const string& s)
{
    return s;
}

string rtrim_copy(const string &str)
{
    return str.substr(0,
                      str.find_last_not_of(" \f\n\r\t\v") + 1);
}

string ltrim_copy(const string &str)
{
    return str.substr(0,
                      str.find_first_not_of(" \f\n\r\t\v") + 1);
}

string trim_copy(const string &str)
{
    return ltrim_copy(rtrim_copy(str));
}

double u_alpha_score(double alpha)
{
    double u_alpha = 0;
    // Selection of the Zalpha value
    if (alpha == 0.05) {
        u_alpha = Z_FOR_ALPHA_05;
    }
    else if (alpha == 0.025) {
        u_alpha = Z_FOR_ALPHA_025;
    }
    else if (alpha == 0.01) {
        u_alpha = Z_FOR_ALPHA_01;
    }
    else {
        cerr << "ERROR: Non valid value for Alpha: "
            "select one between "
            "{0.05, 0.025, 0.01}" << endl;
        cerr << "The inference process was "
            "terminated with error" << endl;
        exit(EXIT_FAILURE);
    }
    return u_alpha;
}

double mean(double v1, double v2)
{
    return (v1 + v2) / 2;
}

double u2z_alpha_test(double prop1, double prop2,
                      int sample_size, double alpha,
                      double *dev_std_h0)
{
    double u_alpha = 0, z_alpha = 0;
    double p_est = 0, q_est = 0;

    // Selection of the Zalpha value (u_alpha is the value
    //   for the standard normal deviate N(0,1))
    u_alpha = u_alpha_score(alpha);

    // - Estimated error rate for population by
    //     mean of error rates for samples -
    //     p_est is the accumulator set
#ifdef USE_BOOST
    boost::accumulators::accumulator_set<double,
            boost::accumulators::features<
              boost::accumulators::tag::mean,
            boost::accumulators::tag::variance> > p_acc;

    // Insert the values inside the accumulator
    p_acc(prop1);
    p_acc(prop2);

    // Compute p estimator and q
    p_est = boost::accumulators::mean(p_acc);
#else
    // Compute p estimator and q
    p_est = mean(prop1, prop2);
#endif
    q_est = 1 - p_est;

    // Check if the error rate is zero
    // Without this threshold, if the proportions is too low the
    //   approximation conditions from binomial to gaussian
    //   distribution will be not satisfied.
    //   And, it's not a problem to due with very small
    //   error like if it's no error.
    if (p_est <= 0.04) {
#ifdef DEBUG1
        cout << "zeta-beta: MINF" << endl;
#endif
        return DMINF;
    }

    // Check approximation conditions.
    if (!aprx_cond_bin2gauss_distr(p_est, q_est,
                                   sample_size)) {
        cerr << "ERR: The process stop!" << endl;
        throw "Constraints approximation to"
            " Normal Gaussian dist not satisfied";
    }

    // Variance and dev. std. under the H0 hypothesis
    double variance_h0 = (2 * p_est * q_est)
        / sample_size;
    *dev_std_h0 = sqrt(variance_h0);

    // Z-alpha: u_alpha is the z_alpha value in
    //   the normal gaussian distribution,
    //   multiplied for std_err became useful
    //   for the specific distribution.
    z_alpha = u_alpha * (*dev_std_h0);
    return z_alpha;
}

double u2z_alpha_test(double prop1, double prop2,
                      int sample_size, double alpha)
{
    double tmp = 0;
    return u2z_alpha_test(prop1, prop2,
                          sample_size,
                          alpha, &tmp);
}

bool aprx_cond_bin2gauss_distr(double p_est, double q_est,
                               int sample_size)
{
    // Necessary approximation conditions to
    //   normal distribution for
    //   binomial distribution.
    if (!(sample_size * p_est > 5 &&
        sample_size * q_est > 5)) {
        cerr << endl
             << "ERR: Approximation conditions to Normal "
             << "Distributions are not satisfied." << endl
             << "ERR: Details: p: " << p_est << ", q: "
             << q_est << ", N: " << sample_size << endl
             << "ERR: N*p: " << sample_size * p_est
             << ", N*q: " << sample_size * q_est << endl;
        return false;
    }
    else {
        return true;
    }
}

int get_poisson(double lambda)
{
    double L = exp(-lambda);
    double p = 1.0;
    int k;
    for (k = 1; p > L; ++k) {
        p *= rand() / (RAND_MAX);
    }
    return k - 1;
}


