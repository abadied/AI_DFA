#include "DFA.hpp"

namespace gi {
    /**
     * A DFA with blue red colored states.
     */
    class BlueRedDFA : public DFA {
    private:
        /** Blue states */
        vector<State> blue_states;
        /** Red states */
        vector<State> red_states;
    public:
        /**
         * Make an instance of new DFA,
         *   with all members initialized to null.
         */
        explicit BlueRedDFA(const map<Symbol, SymbolType> &alphabet);

        /**
         * Make an instance of BlueRedDFA from an object dfa.
         * @param dfa Object dfa used for make the blue red DFA object.
         */
        explicit BlueRedDFA(const DFA &dfa);

        /**
         * Constructor for make a copy of a BlueRedDFA "d1"
         * @param br_dfa The blue red DFA to copy.
         */
        BlueRedDFA(const BlueRedDFA &br_dfa);

        /**
         * Make an instance of new blue red DFA. Give
         *   possibility to set the start state.
         * @param n_state	Number of states.
         * @param alphabet		Alphabet symbols.
         */
        BlueRedDFA(State n_state, const map<Symbol, SymbolType> &alphabet);

        /**
         * Make an instance of new blue red DFA. Give
         *   possibility to set the start state.
         * @param n_state	Number of states.
         * @param alphabet		Alphabet symbols.
         * @param s_state	Start state.
         */
        BlueRedDFA(State n_state,const map<Symbol, SymbolType> &alphabet, State s_state);

        /**
         * Destroy a DFA object, freeing the memory.
         */
        ~BlueRedDFA() override;

        /**
         * Make an instance of dfa from the current BlueRedDFA object.
         * @return A pointer to the new dfa.
         */
        DFA *to_dfa() const;

        /**
         * Differently from "to_dfa()" function; it return a BlueRedDFA,
         *   without unreachable states,  adding if necessary a sink state.
         * It adoperate the information about the red states for select the
         *   state for final dfa (use the "deleteStates"
         *    for delete pure unreacheable states).
         * @return A pointer to new dfa.
         */
        BlueRedDFA *to_canonical();


        unordered_set<State> reachables();


//EDSM

        /**
         * Get a pointer to the vector of blue states.
         * @return Pointer to the vector of blue states.
         */
        vector<State> &get_blue();
        const vector<State> &get_blue() const;

        /**
         * Get a pointer to the vector of red states.
         * @return Pointer to the vector of red states.
         */
        vector<State> &get_red();
        const vector<State> &get_red() const;

        /**
         * Add a blue state to the Vector of blue state
         * @param blue_state_index Index of the new blue state.
         */
        void add_blue(State blue_state_index);

        /**
         * Add a red state to the Vector of blue state
         * @param red_state_index Index of the new red state.
         */
        void add_red(State red_state_index);

        /**
         * Remove a state from the blue states.
         * @param blue_state_index Index of
         *   the blue state to remove.
         */
        void remove_blue(State blue_state_index);

        /**
         * Remove a state from the red states.
         * @param red_state_index Index of the
         *   red state to remove.
         */
        void remove_red(State red_state_index);

        /**
         * Get the number of blue states.
         * @return Number of blue states.
         */
        State blue_count();

        /**
         * Get the number of red states.
         * @return Number of red states.
         */
        State red_count();

        /**
         * Return true if blue_state_index is inside the Vector of blue states
         * @param blue_state_index Index of blue state to find between the blue states.
         * @return True if blue_state_index is inside the Vector of blue states.
         */
        bool in_blue(State blue_state_index);

        /**
         * Return true if red_state_index is inside the Vector of red states
         * @param red_state_index Index of red state to find between the red states.
         * @return True if red_state_index is inside the Vector of red states.
         */
        bool in_red(State red_state_index);

        /**
         * Copy in the member vector the blue
         *   states from an extern vector
         * @param new_blue_vector Extern vector of blue states.
         */
        void copy_blue(const vector<State> &new_blue_vector);

        /**
         * Copy in the member vector the red
         *   states from an extern vector
         * @param new_red_states Extern vector of red states.
         */
        void copy_red(const vector<State> &new_red_states);

        /**
         * Print the transition table with the color of the states.
         *   Before it, print the "title"
         * @param title Title printed before the transition table.
         */
        void print(const string &title);

        /**
         * Print the transition table with the color of
         *   the states, using the alphabet symbol. Before it, print the "title"
         * @param title Title printed before the transition table.
         */
        void print_alpha_map_color(const string &title);

        /**
         * Print a dot file for the current dfa,
         *   with title "title", in the path "file_path", coloring the states.
         * @param title	Title printed before the transition table.
         * @param file_path Path where make a dot file.
         */
        ostream& write_dot(const string &title, ostream& os) override;

        /**
         * Print a dot file for the current dfa using the alphabet symbols,
         *   with title "title", in the path "file_path", coloring the states.
         * @param title	Title printed before the transition table.
         * @param file_path Path where make a dot file.
         */
        ostream& write_alpha_map(const string &title, ostream& os) override;


        /** Write the content of the dfa as binary content.
         * @param os The stream to write to.
         * @return the stream.
         */
        ostream& write_binary(ostream& os) override;

        /**
         * Read the DFA from a stream.
         * @param is The stream to read from.
         * @return The stream.
         */
        istream& read_binary(istream& is) override;
    };
}
