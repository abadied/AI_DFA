#ifndef BLUEFRINGE_H_
#define BLUEFRINGE_H_

#include "BlueRedDFA.hpp"

using namespace std;

namespace gi {
    /**
     * Class for all the altgorithms which use
     *   a BlueFringe Framework.
     */
    class BlueFringe {
    protected:

        // EXAMPLES
        /* Path of example file (training data) */
        string path_samples;

        // ALPHABET
        /* Alphabet size (number of symbols) */
        Symbol dim_alphabet;

        map<SymbolType, Symbol> mapped_alphabet;
        map<Symbol, SymbolType > inverse_mapped_alphabet;
        vector < SymbolString > positive;
        vector < SymbolString > negative;
        vector<int> wp;
        vector<int> wn;

        // STATISTICS
        /* Number of merge actuated by EDSM */
        unsigned int num_actual_merge;
        /* Number of merge calculetd for
             evalution of heuristic by EDSM */
        unsigned int num_heuristic_merge_valued;
        /* Number of red (0) and blue (1) states*/
        vector<State> fringe_size[2];
        /* Iterations of EDSM */
        int while_count;
        /** Activate debug */
        bool debug;
        /** Verbose prints */
        bool verbose;

        void set_debug(bool val);
        void set_verbose(bool val);


        // TODO: Update the function for creating a PTA
        // BlueRedDFA* build_pta(string* positive, int dim_positive);

        /**
         * Build an APTA (Augmented Prefix Tree Acceptor) with
         *   positive and negative samples,
         *   extracted by read_samples().
         * @param positive
         * @param dim_positive
         * @param negative
         * @param dim_negative
         * @return A pointer to built APTA.
         */
        BlueRedDFA *build_apta(const vector < SymbolString > &positive,
                             const vector < SymbolString > &negative);


        /**
         * Perform a merge operation between state
         *   red_state and state blue_state, for DFA dfa1.
         * @param cur_dfa
         * @param red_state
         * @param blue_state
         */
        void merge(BlueRedDFA *cur_dfa,
                   State red_state,
                   State blue_state);

        /**
         * Perform a recursive operation of fold, starting from
         *   the states to merge, inside "originale" dfa.
         * @param originale
         * @param red_state
         * @param blue_state
         */
        void fold(BlueRedDFA *originale,
                  State red_state,
                  State blue_state);

        /**
         * Promote the state q, from blue to red state.
         *   Delete the state from the blue state list.
         * @param cur_dfa
         * @param q
         */
        void promote(BlueRedDFA *cur_dfa, State q);

        /**
         * Return a score for a dfa.
         * It's calculated by
         *   heuristic emerged during
         *   Abbadingo Competition (1998).
         *
         * @param cur_dfa
         * @param positive
         * @param negative
         * @param wp
         * @param wn
         * @return A score for a DFA,
         *   greater is better.
         */
        virtual int merge_heuristic_score(
            BlueRedDFA *cur_dfa,
            const vector < vector <Symbol> > &positive,
            const vector < vector <Symbol> > &negative,
            const vector<int> *wp,
            const vector<int> *wn) = 0;

        virtual double
        merge_heuristic_score(
                double error_rate_before,
                double error_rate_after,
                int dim_strings, double alpha,
                int earn_states) = 0;


        /**
         * Update the 'dfa1' adding new blue states.
         * Every state, that is achievable
         * from a red state is promoted to blue,
         * unless arrive state is already red.
         * @param cur_dfa
         */
        void new_blue(BlueRedDFA *cur_dfa);


        /**
         * Set the type state to 'DEL' for
         *   that states which are
         * unreachable from every
         *   other state: fanin=0.
         * @param cur_dfa
         */
        void delete_states(BlueRedDFA *cur_dfa);

        /**
         * Set a new record of values that are the
         *   fringe size of blue states, and
         * the number of red states. Every time
         *   the function is called a new
         * snapshot is taken.
         * @param r
         * @param b
         */
        void set_fringe_size(State r, State b);

        /**
         * Print all the snapshots taken,
         *   during EDSM process, about the fringe size.
         */
        void print_fringe_size();

    public:

        /**
         * Add a single input sample.
         * @param line The line of symbols.
         * @param len The number of symbols.
         * @param weight The weight for that line.
         * @param sign The sign of the semple. 1 for
         *          positive otherwise for negative.
         */
        void add(const char* line, unsigned int len,
                 int weight, int sign);

        /**
         * Instance an object with all the members
         *   and methods for EDSM inference process.
         * @param path It's the path where find
         *   positive and negative samples
         */
        BlueFringe();

        /**
         * Destroy and EDSM object, freeing the memory.
         */
        virtual ~BlueFringe();

        /**
         * Read positive and negative samples,
         *   and copy them inside
         *   'positive' and 'negative'
         *   vector in parameters.
         */
        void read_samples(const string &path_samples);

        /**
         * Start an EDSM inference process.
         * @return Inferred DFA
         */
        virtual DFA *run() = 0;

        /**
         * It's a function with statistical finality.
         * Return the number of merges already performed
         *   to the actual stage of EDSM process.
         * @return Number of merges already performed to
         *   the actual stage of EDSM process.
         */
        int get_actual_merge();

        /**
         * It's a function with statistical finality.
         *   Return the number of all simulated merges for
         *   heuristic evaluation, from first to actual stage.
         * @return Number of all simulated merges for
         *   heuristic evaluation to actual stage.
         */
        int get_heuristic_merge();

        /**
         * It's a function with statistical finality.
         * @return the number of iteration of EDSM:
         *   it's the number of times that EDSM finded that
         *   there was already blue states.
         */
        int get_while_count();

        unsigned int get_alphabet_count();
        unsigned int get_positive_count();
        unsigned int get_negative_count();
        string get_alphabet();
    };
}


#endif /* BLUEFRINGE_H_ */
