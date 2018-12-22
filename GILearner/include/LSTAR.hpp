#ifndef LSTAR_H_
#define LSTAR_H_

#include "DFA.hpp"

/**
 * The types of observation table states.
 * Red: stable state that are already part of the final automata.
 * Blue: Candidate states to be added to the obt or merged
 *         within one of the red states.
 */
enum class OBTState {
    OBT_STATE_RED  = 1,
    OBT_STATE_BLUE = 0
};


namespace gi {
    /**
     * Class for LSTAR inference algorithm,
     *   with all members and methods for
     *   start an inference process
     *   through Learner and Teacher.
     */
    class LSTAR {
    private:
        // 3 Structures: - prefixes with associated type, -
        //   result of the square meters, - list of experiments
        /* Columns of Observation Table */
        vector<SymbolString> experiments;
        /* Local values of results for membership
         *   query already asked to Teacher */
        map<SymbolString, bool> mq;
        /* Blue and red prefixes of Observation Tables */
        map<SymbolString, OBTState, vector_int_size_less> pref;
        /* Alphabet size */
        Symbol dim_alphabet;
        /* Alphabet */
        vector<Symbol> *alphabet;
        /* Target DFA of inference process. Used from Teacher. */
        DFA *target;

    public:

        /**
         * Instance an object with all the members and
         *   methods for LSTAR inference process.
         * @param path It's the target DFA for the
         *   inference process, used from Teacher.
         */
        explicit LSTAR(const DFA &target_dfa);

        /**
         * Destroy an LSTAR object, freeing the memory.
         */
        ~LSTAR();

        /**
         * Start an LSTAR inference process.
         * @param approximate If it's true, set an
         *   LSTAR inference process using an
         *   approximation of target DFA.
         * @param samples_test_path Samples
         *   approximating target DFA.
         * @return The inferred DFA.
         */ // TODO: Implement approximate version
        DFA *run(bool approximate = false,
                 const string *samples_test_path = nullptr);


        /**
         * Return a whole "row" of Observation
         *   Table for a prefix.
         * @param prefix Unique prefix labeling a row.
         * @return Row of observation table
         */
        vector<OBTState> get_row(const vector<Symbol>& prefix);


        /**
         * For a non closed table, fix one or more problems
         *   (not necessary all) which keep not closed the table.
         * @return Return 'true' if the table was modified
         *   (DOESEN'T mean table is closed!).
         *   Otherwise return 'false', that is:
         * table was not modified, it was already closed.
         */
        bool close_obt();

        /**
         * For a non consistent table, fix one or more problems
         *   (not necessary all) which keep not consistent the table.
         * @return Return 'true' if the table was modified
         *   (DOESEN'T mean table is consistent!).
         *   Otherwise return 'false', that is:
         * table was not modified, it was already consistent.
         */
        bool make_obt_consistent();

        /**
         * Update the table using the witness.
         *   (Update the OB from the counterexample)
         * @param witness Witness is the
         *   counterexample coming from Teacher.
         */
        void update_from_counterexample(
                const vector <Symbol>& witness);


        /**
         * Build a DFA from Observation Table.
         * @return Pointer to builded DFA.
         */
        DFA *obt_to_dfa();


        /**
         * Print the Observation table.
         */
        void print_obt();
    };
}

#endif /* LSTAR_H_ */
