#ifndef BLUESTAR_H_
#define BLUESTAR_H_

#include "BlueFringe.hpp"

using namespace std;

namespace gi {
    /** Class for Blue* inference algorithm, with all
     * members and methods for start an inference process.
     */
    class BlueStar : public BlueFringe {
    private:
        double alpha = 0.01;
        double delta = 1000;

        // STATISTICS
        /*!< Error rate for the dfa inferred respect to samples*/
        double error_rate_final_dfa;

        /**
         * Return a score for a dfa.
         * It's calculated by statistical heuristic of Blue*,
         *   minimimazing the ratio between second
         *   type error and earn states.
         *
         * @param dfa1
         * @param positive
         * @param dim_positive
         * @param negative
         * @param dim_negative
         * @return A score for a DFA, greater is better.
         *   "MINF" value if the merge is not acceptable.
         */
        double merge_heuristic_score(
                double error_rate_before, double error_rate_after,
                int dim_strings, double alpha, int earn_states) override;


        int merge_heuristic_score(
                BlueRedDFA *cur_dfa,
                const vector < vector <Symbol> > &positive,
                const vector < vector <Symbol> > &negative,
                const vector<int> *wp,
                const vector<int> *wn) override
        { return 0; };

        /**
         * Return the number of strings, of the Training Set,
         *   not recognized from final automaton.
         * Note, that is not a generalization index
         *   but an error index, because it's calculated on the
         * training set rather than test set.
         * @param dfa1
         * @param positive
         * @param negative
         * @param wp
         * @param wn
         * @param tot_wp_w
         * @param tot_wn_w
         * @return
         */
        static double error_rate(BlueRedDFA *dfa1,
                                 const vector < SymbolString > &positive,
                                 const vector < SymbolString > &negative,
                                 const vector<int> &wp, const vector<int> &wn,
                                 int tot_wp_w, int tot_wn_w);

        /**
         * Return a score for a dfa. It's calculated by
         *   heuristic emerged during Abbadingo Competition (1998).
         *
         * @param dfa1
         * @param positive
         * @param dim_positive
         * @param negative
         * @param dim_negative
         * @return A score for a DFA, greater is better.
         */
        //int  promotion_heuristic_score(BlueRedDFA* dfa1, SymbolString* positive,
        //     int dim_positive, SymbolString* negative, int dim_negative);


    public:

        /**
         * Instance an object with all the members and
         *   methods for Blue* inference process.
         */
        BlueStar(double alpha_value, double delta_value);

        /**
         * Destroy and Blue* object, freeing the memory.
         */
        ~BlueStar() override;


        /**
         * Start an Blue* inference process.
         * @return Inferred DFA
         */
        DFA *run() override;

        double get_error_rate_final_dfa();
    };

}


#endif /* BLUESTAR_H_ */
