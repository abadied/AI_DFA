/* Note:
 * Removed functions: list_yeds_edsm,
 *   list_status_rb, num_edsm_rb and num_edsm_state
 */

#ifndef EDSM_H_
#define EDSM_H_

#include "BlueFringe.hpp"

using namespace std;

namespace gi {
    /**
     * Class for EDSM inference algorithm,
     *   with all members and methods for start
     *   an inference process.
     */
    class EDSM : public BlueFringe {
    private:


        /**
         * Return a score for a dfa. It's
         *   calculated by heuristic
         *   emerged during Abbadingo
         *   Competition (1998).
         *
         * @param cur_dfa
         * @param positive
         * @param dim_positive
         * @param negative
         * @param dim_negative
         * @return A score for a DFA, greater is better.
         */
        int merge_heuristic_score(BlueRedDFA *cur_dfa,
                const vector < vector <Symbol> > &positive,
                const vector < vector <Symbol> > &negative,
                const vector<int> *wp,
                const vector<int> *wn) override;

        double merge_heuristic_score(
                double error_rate_before, double error_rate_after,
                int dim_strings, double alpha,
                int earn_states) override { return 0; };


    public:
        /**
         * Instance an object with all the members and
         *   methods for EDSM inference process.
         * @param path It's the path where find positive
         *   and negative samples
         */
        EDSM();

        /**
         * Destroy and EDSM object, freeing the memory.
         */
        ~EDSM() override;

        /**
         * Start an EDSM inference process.
         * @return Inferred DFA
         */
        DFA *run() override;
    };
}

#endif /* EDSM_H_ */
