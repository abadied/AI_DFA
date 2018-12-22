#ifndef DFA_H_
#define DFA_H_

#include "utilities.hpp"

/** Represent a Symbol input for the Automata. */
typedef unsigned int Symbol;
/** The type of the input alphabet. */
typedef char SymbolType;
/** A string of symbols. */
typedef vector<Symbol> SymbolString;

/** A state in the Automata. */
typedef unsigned int State;
/** A table of States on the rows and Symbols on the columns.
 *    This table type uses for transition tables where
 *    the value is the next State.
 *  The last column stores for each State row the state type.
 * */
typedef State** Matrix;

/*----------------- Type of states -----------------*/
/** Rejecting state */
const State DFA_STATE_REJECT = 0;
/** Accepting state */
const State DFA_STATE_ACCEPT = 1;
/** Non accepting state */
const State DFA_STATE_NON_ACCEPTING = 2;
/** Unreachable state from other states.
     Usually is a state to be delete. */
const State DFA_STATE_UNREACHABLE = 3;
/** Usually adopted for a non initialized state. */
/*---------------------------------------------------*/

/** "gi" (grammatical inference) is the library namespace */
namespace gi {
    /**
     * Class for DFA representation.
     */
    class DFA {
    protected:
        /** Number of dfa states */
        State num_states{};
        /** Index of start state */
        State start_state{};
        /** Convert symbols into indices */
        map<SymbolType, Symbol> mapped_alphabet;

        /**
         * Set the transition table (ttable)
         *   reference to an extern transition
         *   table passed as argument
         * @param ext_ttab The given trans
         *                   table to use.
         */
        void set_ttable(Matrix &ext_ttab);


        /**
         * Set the number of states
         * @param n The value to set.
         */
        void set_num_state(State n);


        // TODO: Remove.
//        /**
//         * Set the alphabet of the DFA to alphabet
//         *   in input of size "d_alphabet".
//         * Also set "mapped_alphabet" with an index
//         *   for every symbol.
//         * @param alphabet The given alphabet.
//         * @param d_alphabet
//         */
//        void set_alphabet(const map<Symbol, SymbolType> &alphabet);

    public:
        /** Transition table */
        Matrix ttable{};

        /** Alphabet symbols. */
        map<Symbol, SymbolType> alphabet;

        /** Empty constructor.
         */
        DFA() = default;

        /**
         * Make an instance of null dfa
         * @param alphabet The given alphabet.
         */
        explicit DFA(const map<Symbol, SymbolType> &alphabet);

        /**
         * Make an instance of new dfa with default
         *   start state to 0.
         * @param n_state	Number of states
         * @param alphabet		Alphabet symbols
         */
        DFA(State n_state, const map<Symbol, SymbolType> &alphabet);

        /**
         * Make an instance of new dfa. Give possibility to
         *   set the start state.
         * @param n_state	Number of states
         * @param alphabet		Alphabet symbols
         * @param s_state	Start state
         */
        DFA(State n_state, const map<Symbol, SymbolType> &alphabet, State s_state);

        /**
         * Make an instance of new dfa.
         * Set tra transistion table making a copy of
         *   "tt_copy" passed as argument.
         * @param n_state	Number of states
         * @param alphabet		Alphabet symbols
         * @param s_state	Start state
         * @param tt_copy	Reference to extern transition
         *                    table to copy inside current dfa
         */
        DFA(State n_state, const map<Symbol, SymbolType> &alphabet,
            State s_state, const Matrix& tt_copy);

        /**
         * Constructor for make a copy of a dfa "d1"
         * @param other	Dfa to copy
         */
        DFA(const DFA &other);

        /**
         * Destroy a DFA object, freeing the memory.
         */
        virtual ~DFA();

        /**
         * Erase transition table.
         */
        void erase_ttable();

        /**
         * Return size of alphabet
         * @return Size of alphabet
         */
        Symbol alphabet_count();

        /**
         * Get number of states
         * @return Number of states
         */
        State state_count();

        /**
         * Get index of start state
         * @return Index of start state
         */
        State get_start_state();

        /**
         * Get index of arrive state for dfa_string argument
         * @param dfa_string String executed on dfa
         * @return Index of arrive state for "dfa_string"
         */
        State get_arrive_state(const SymbolString &dfa_string);

        /**
         * Return a reference to ttable()
         * @return Pointer to ttable
         */
        Matrix& get_ttable();

        /**
         * Get value of ttable for index "i", "j"
         * @param i The current state index.
         * @param j The symbol.
         * @return The next state.
         */
        State get_ttable(State i, Symbol j);

        /**
         * Set a single value "v" for ttable entry for "i","j"
         * @param i First coordinate
         * @param j	Second coordinate
         * @param v	Value to set
         */
        void set_ttable_entry(State i, Symbol j, State v);

        /**
         * Set state to be rejected state.
         * @param state The state to update.
         */
        void set_accept(State state)
        {
            set_state_type(state, DFA_STATE_ACCEPT);
        }

        /**
         * Set state to be rejected state.
         * @param state The state to update.
         */
        void set_reject(State state)
        {
            set_state_type(state, DFA_STATE_REJECT);
        }

        /**
         * Set state to be normal state.
         * @param state The state to update.
         */
        void set_normal(State state)
        {
            set_state_type(state, DFA_STATE_NON_ACCEPTING);
        }

        /**
         * Set state to be normal state.
         * @param state The state to update.
         */
        void set_unreachable(State state)
        {
            set_state_type(state, DFA_STATE_UNREACHABLE);
        }

        /**
         * Get the state type of s
         * @param s The state to check.
         * @return The state type number.
         */
        State state_type(State s)
        {
            return ttable[s][alphabet_count()];
        }

        /**
         * Set the state type of s.
         * @param s The state to update.
         * @param type The new type.
         */
        void set_state_type(State s, State type)
        {
            ttable[s][alphabet_count()] = type;
        }

        /**
         * Check if state s is accepting state.
         * @param s The state to check.
         * @return Boolean indicator.
         */
        bool is_accept(State s)
        {
            return DFA_STATE_ACCEPT == state_type(s);
        }

        /**
         * Check if state s is rejecting state.
         * @param s The state to check.
         * @return Boolean indicator.
         */
        bool is_reject(State s)
        {
            return DFA_STATE_REJECT == state_type(s);
        }

        /**
         * Check if state s is non accepting state (normal state).
         * @param s The state to check.
         * @return Boolean indicator.
         */
        bool is_non_accept(State s)
        {
            return DFA_STATE_NON_ACCEPTING == state_type(s);
        }

        /**
         * Check if state s is unreachable state.
         * @param s The state to check.
         * @return Boolean indicator.
         */
        bool is_unreachable(State s)
        {
            return DFA_STATE_UNREACHABLE == state_type(s);
        }

        /**
         * Make a new dfa from the union of
         *   current dfa and "dfa_hp".
         * The first states are from current dfa,
         *   last states from "dfa_hp".
         *   The total number of states are sum of the
         *     number of states for the 2 dfa.
         * @param dfa_hp Dfa to add to the current dfa
         * @return Pointer to the union dfa of two dfa
         */
        DFA *unionDFA(DFA *dfa_hp);

        /**
         * Minimizes the current dfa
         * Note: Minimization using
         *   Table-filing algorithmm.
         * @return Pointer to a new
         *   instance of dfa, that
         *   is the minimized current dfa
         */
        DFA *minimize_TF();


        /** Return a measures of complexity for current DFA.
         *
         * @return Default value is the number of states.
         */
        double get_complexity();

        /**
         * Print the transition table of current dfa.
         *   Before the transition
         *   table print the title passse as parameter.
         * @param title Title printed before the
         *   transition table
         */
        void print_dfa(const string &title);

        /**
         * The transition table of current dfa as string.
         *   Before the transition
         *   table print the title passse as parameter.
         * @param title Title printed before the
         *   transition table
         */
        string dfa();

        /**
         * Print the transition table using the alphabet symbols.
         *   Before the transition table print the "title".
         * @param title Title printed before the transition table
         */
        void print_alph_dfa(const string &title);

        /**
         * Print a dot file for the current dfa, with title "title",
         *   in the path "file_path".
         * @param title	Title printed before the transition table
         * @param file_path Path where make a dot file
         */
        void save_dot(const string &title, const char *file_path);

        /** Write the content of the dfa as binary content.
         * @param os The stream to write to.
         * @return the stream.
         */
        virtual ostream& write_binary(ostream& os);

        /**
         * Read the DFA from a stream.
         * @param is The stream to read from.
         * @return The stream.
         */
        virtual istream& read_binary(istream& is);

        /**
         * Save the DFA to a file.
         * @param file_path The file path.
         * @return Success indicator.
         */
        bool save(const char *file_path);

        /**
         * Load the DFA from a file.
         * @param file_path The file path.
         * @return Success indicator.
         */
        bool load(const char *file_path);

        /**
         * Save the DFA to a file.
         * @return The DFA as a string.
         */
        string save_to_string();

        /**
         * Load the DFA from a file.
         * @param dfa_buffer The string contains the DFA.
         * @return Success indicator.
         */
        bool loadfrom_string(const char *dfa_buffer);

        virtual ostream& write_dot(const string &title, ostream& os);

        /**
         * Print a dot file for the current dfa using the alphabet symbols,
         *   with title "title", in the path "file_path".
         * @param title	Title printed before the transition table
         * @param file_path Path where make a dot file
         */
        void print_alpha_map(const string &title, const char *file_path);

        /**
         * A dot file string for the current dfa using the alphabet symbols,
         *   with title "title", in the path "file_path".
         * @param title	Title printed before the transition table
         * @param file_path Path where make a dot file
         */
        string dot();

        virtual ostream& write_alpha_map(const string &title, ostream& os);

        /**
         * Make a membership query to dfa with the "str"
         *   string. Return "true"
         *   if the arrive state for "str" is acceptor, else "false".
         * @param str A string to make a membership query.
         * @return "True" o "false" depending on the arrive state:
         *   "true" if acceptor, else if not.
         */
        bool membership_query(const SymbolString &str);

        /**
         * Make an equivalence query, that return an empty
         *   witness if the current dfa
         *   is equivalent to dfa "dfa_hp" (Hypothesis DFA),
         *   argument of the function.
         * Otherwise return a witness, that is a counterexample
         *   that distinguishes the two dfa.
         * @param dfa_hp Pointer to dfa to compare for equivalence.
         * @return A conterexample, empty if the two dfa are equivalent.
         */
        SymbolString equivalence_query(DFA *dfa_hp);

        /**
         * Fills a table with the "Table Filling Algorithm", useful for
         *   find the equivalent/distinct states, and
         *   also for generate a witness.
         * The Table considered is only the upper triangular matrix,
         *   that can be saved in a linear array.
         * @return A table saved in a linear array.
         */
        Symbol *table_filling();

        /**
         * Create a list of states and
         *   corresponding equivalent states.
         * @param distincts A table build with the
         *   Table Filling Algorithm
         * @return A pointer to the first vector<State>.
         *   Every vector is a list of
         *   equivalent state for the state
         *   associate to that vector.
         */
        vector<State> *table_eq_states(const Symbol *distincts);

        /**
         * Make a conterexample from a table build with Table Filling
         *   Algorithm using the union DFA of those two DFA to compare.
         * @param distinct Table build with Table Filling Algorithm
         * @param start_state_dfa_hp Index of the first state of
         *   dfa_hp inside the union DFA.
         * @return A witness that distinguishes the two dfa.
         */
        SymbolString witness_from_table(const Symbol *distinct,
                                        State start_state_dfa_hp);
    };

}

/**
 * Compare two vectors of symbols.
 */
struct vector_int_size_less {
    bool operator()(const SymbolString &l,
                    const SymbolString &r) const {
        if (l.size() < r.size()) {
            return true;
        }
        if (l.size() > r.size()) {
            return false;
        }
        for (auto i = l.begin(), j = r.begin();
             i < l.end() && j < r.end(); ++i, ++j) {
            if (*i != *j) {
                return (*i) < (*j);
            }
        }
        return false;
    };
};

#endif /* DFA_H_ */
