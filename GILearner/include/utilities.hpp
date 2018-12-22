#ifndef UTILITIES_H_
#define UTILITIES_H_

#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <sys/stat.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstring>
#include <string>
#include <cctype>
#include <vector>
#include <algorithm>
#include <set>
#include <unordered_set>
#include <unordered_map>
#include <map>
#include <stdexcept>
#ifdef USE_OPEN_MP
#include "omp.h"
#endif

#define ND    std::numeric_limits<unsigned int>::max()
#define MINF  std::numeric_limits<int>::min()
#define DMAX  std::numeric_limits<double>::max()
#define DMINF std::numeric_limits<double>::min()

using namespace std;

bool create_directory(const string &path);

inline bool exists(const char *path)
{
    struct stat info{};
    return stat(path, &info) != 0;
}

inline bool exists(const string &path)
{
    return exists(path.c_str());
}

template<typename T>
vector<T> append_vectors(
    vector<T> *a, vector<T> *b)
{
    vector<T> res = *a;
    res.insert(res.end(),
               b->begin(),
               b->end());
    return res;

}

template<typename T, typename Iterator>
vector<T> prefix_vector(const vector<T> &a, Iterator pref_end)
{
    vector<T> res(a.begin(), pref_end);
    return res;
}

template<typename T>
ostream &operator<<(ostream &os, const vector<T> &obj)
{
    os << "[ ";
    for (auto i: obj) {
        os << i << " ";
    }
    os << "]";
    return os;
}

/**
 * Convert int to string.
 * @param a The number to convert.
 * @return The string representation.
 */
string int_to_str(int a);

/**
 * Convert string to number.
 * @param str The string to convert.
 * @return The number.
 */
int str_to_int(const string &str);

/**
 * Convert character to string.
 * @param c The character to convert.
 * @return The string representation.
 */
string to_string(char c);

/**
 * Convert string to a new string.
 * @param s The string to copy.
 * @return The new string.
 */
string to_string(const string& s);

/**
 * Given an alpha values for a Normal Gaussian Distribution N(0,1),
 *   return the value of U_alpha, that is Z-alpha for N(0,1).
 *   It define the bound value for accepting or
 *   rejecting an hypothesis, adopting the N(0,1).
 * @param alpha
 * @return  U-alpha value: the z-value for N(0,1),
 *            the bound value for accepting and rejecting area.
 */
double u_alpha_score(double alpha);

/**
 * Creates an inverse map with keys as values and values as keys.
 * @tparam Map The map type (map, unordered_map)
 * @tparam K The key type.
 * @tparam V The value type.
 * @param map The mpa instance.
 * @return The inverse map.
 */
template<template <typename...> class Map, typename K, typename V>
void swap_key_values(const Map<K, V>& map, Map<V, K>& result)
{
    for (const auto& p : map) {
        result.emplace(p.second, p.first);
    }
}

/**
 * Write a value to stream.
 * @tparam T The value type.
 * @param os The stream to write to.
 * @param value The value instance.
 * @return success indicator.
 */
template<typename T>
inline bool
write_value(ostream &os, const T &value)
{
    const char *buff = reinterpret_cast<const char *>(&value);
    for (int i = 0; os.good() && i < sizeof(value); ++i) {
        os.write(buff + i, 1);
    }
    return os.good();
}

/**
 * Write array of type to the stream.
 * @tparam T The type to write.
 * @param os The output stream.
 * @param value The value instance.
 * @param count The number of elements.
 * @return Success indicator.
 */
template<typename T>
inline bool
write_arr(ostream &os, const T *value, size_t count)
{
    const char *buff = reinterpret_cast<const char *>(value);
    for (unsigned int i = 0; os.good() && i < sizeof(*value) * count; ++i) {
        os.write(buff + i, 1);
    }
    return os.good();
}

/**
 * Write container like STL object.
 * @tparam Vec The container type (vector, set, unordered_set, ...)
 * @tparam V The value type.
 * @param os The output stream.
 * @param vec The vector instance to save.
 * @return Success indicator.
 */
template<template <typename...> class Vec, typename V>
bool
write_vec(ostream &os, const Vec<V> &vec)
{
    write_value(os, vec.size());
    for (auto a : vec) {
        write_value(os, a);
    }
    return os.good();
}

/**
 * Write map type to file.
 * @tparam T The map type.
 * @param os The output straem.
 * @param map The map instance.
 * @return success indicator.
 */
template<template <typename...> class Map, typename K, typename V>
inline bool
write_map(ostream &os, const Map<K, V> &map)
{
    write_value(os, map.size());
    for (auto a : map) {
        write_value(os, a.first);
        write_value(os, a.second);
    }
    return os.good();
}

/**
 * Read value from file.
 * @tparam T The value type.
 * @param is The input stream.
 * @param value The value to read.
 * @return success indicator.
 */
template<typename T>
inline bool
read_value(istream &is, T &value)
{
    char *buff = reinterpret_cast<char *>(&value);
    for (int i = 0; is.good() && i < sizeof(value); ++i) {
        is.read(buff + i, 1);
    }
    return is.good();
}

/**
 * Read value from file.
 * @tparam T The value type.
 * @param is The input stream.
 * @param value The value to read.
 * @return success indicator.
 */
template<typename T>
inline bool
read_arr(istream &is, T *value, size_t count)
{
    char *buff = reinterpret_cast<char *>(value);
    for (unsigned int i = 0; is.good() && i < sizeof(*value) * count; ++i) {
        is.read(buff + i, 1);
    }
    return is.good();
}

/**
 * Read container like STL object.
 * @tparam Vec The container type (vector, set, unordered_set, ...)
 * @tparam V The value type.
 * @param is The input stream.
 * @param vec The vector instance to fill.
 * @return Success indicator.
 */
template<template <typename...> class Vec, typename V>
bool
read_vec(istream &is, Vec<V> &vec)
{
    size_t vec_size;
    read_value(is, vec_size);
    for (size_t i = 0 ; is.good() && i < vec_size; ++i) {
        V v;
        read_value(is, v);
        if (is.good()) {
            vec.push_back(v);
        }
    }
    return is.good();
}

/**
 * Write map type to file.
 * @tparam T The map type.
 * @param os The output straem.
 * @param map The map instance.
 * @return success indicator.
 */
template<template <typename...> class Map, typename K, typename V>
inline bool
read_map(istream &is, Map<K, V> &map)
{
    size_t map_size;
    read_value(is, map_size);
    for (unsigned int i = 0; i < map_size; ++i) {
        K key;
        V value;
        read_value(is, key);
        read_value(is, value);
        map.emplace(key, value);
    }
    return is.good();
}

/**
 * Compute the Z-alpha value for a two proportions test,
 *   for two populations, and two samples having the same size.
 *   It's a one tailed test.
 * Z-alpha bound value for accepting and rejecting hypothesis,
 * given an alpha value.
 * An upper value of alpha correspond to a bigger area
 *   of rejecting state: the process will reject more merge,
 *   reducing the Type II error and increasing the Type I error.
 *   Type I error means here is: probability to reject a
 *   useful merge respect to the error introduced. It's alpha.
 *   Type II error means here is: probability to accept a
 *   dangerous merge, with respect to the error introduced.
 * If you want an accurate final DFA you would increase the
 *   value of alpha.
 * If you want a smaller DFA you wold decrease the
 *   value of alpha.
 * @param prop1
 * @param prop2
 * @param sample_size
 * @param alpha
 * @param dev_std_h0
 * @return Z-alpha value for two proportions
 *           test with 2 populations
 */
double u2z_alpha_test(double prop1, double prop2,
                      int sample_size, double alpha,
                      double *dev_std_h0);

/**
 * Doesn't have the dev. std. as parameter. See the other
 *   "u2z_alpha_test" function.
 * @param prop1
 * @param prop2
 * @param sample_size
 * @param alpha
 * @return Z-alpha value for two proportions
 *           test with 2 populations
 */
double u2z_alpha_test(double prop1, double prop2,
                      int sample_size, double alpha);

/**
 * Approximation conditions from binomial to
 *   gaussian distribution.
 * @param p_est
 * @param q_est
 * @param sample_size
 * @return
 */
bool aprx_cond_bin2gauss_distr(double p_est, double q_est,
                               int sample_size);

/**
 * Get random poisson integral number.
 * @param lambda The poison param.
 * @return The integral of iteration took
 *   for random numbers to covering e^(-lambda).
 */
int get_poisson(double lambda);

/**
 * Normalized Compression Distance (NCD)
 * @param x The first value.
 * @param y The second value.
 * @param xy Calculated distance.
 * @return The normalized distance.
 */
inline double ncd(double x, double y, double xy)
{
    return (xy - fmin(x, y)) / fmax(x, y);
}

/**
 * Remove postfix spaces and tabs.
 * @param str The string to trim.
 * @return The new copy trimmed string.
 */
string rtrim_copy(const string &str);

/**
 * Remove prefix spaces and tabs.
 * @param str The string to trim.
 * @return The new copy trimmed string.
 */
string ltrim_copy(const string &str);

/**
 * Remove prefix and postfix spaces and tabs.
 * @param str The string to trim.
 * @return The new copy trimmed string.
 */
string trim_copy(const string &str);

/**
 * trim from start.
 * @param s The string to trim.
 * @return The trimmed string.
 */
static inline string &ltrim(string &s) {
	s.erase(s.begin(),
		find_if(s.begin(), s.end(),
		[](int c) {return !isspace(c); }));
	return s;
}

/**
 * trim from end.
 * @param s The string to trim.
 * @return The trimmed string.
 */
static inline string &rtrim(string &s) {
	s.erase(find_if(s.rbegin(), s.rend(),
		[](int c) {return !std::isspace(c); }).base(),
		s.end());

	return s;
}

/**
 * trim from both ends
 * @param s The string to trim.
 * @return The trimmed string.
 */
inline string &trim(string &s)
{
    return ltrim(rtrim(s));
}

#endif /* UTILITIES_H_ */
