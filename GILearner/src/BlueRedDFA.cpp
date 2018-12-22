#include "BlueRedDFA.hpp"

gi::BlueRedDFA::BlueRedDFA(const map<Symbol, SymbolType> &alphabet)
    : DFA(alphabet) {}

gi::BlueRedDFA::BlueRedDFA(State n_state,
                     const map<Symbol, SymbolType> &alphabet,
                     State s_state)
    : DFA(n_state, alphabet, s_state)
{}

// Default start state to 0
gi::BlueRedDFA::BlueRedDFA(State n_state,
                     const map<Symbol, SymbolType> &alphabet)
    : BlueRedDFA(n_state, alphabet, 0)
{}

gi::BlueRedDFA::BlueRedDFA(const DFA &dfa)
    : DFA(dfa)
{}

gi::BlueRedDFA::BlueRedDFA(const BlueRedDFA &br_dfa)
    : DFA(br_dfa.num_states,
          br_dfa.alphabet, br_dfa.start_state,
          br_dfa.ttable)
{
    copy_blue(br_dfa.get_blue());
    copy_red(br_dfa.get_red());

}

gi::BlueRedDFA::~BlueRedDFA()
{
    blue_states.clear();
    red_states.clear();
}

gi::DFA *gi::BlueRedDFA::to_dfa() const
{
    return new DFA(num_states, alphabet,
                   start_state, ttable);
}

/**
 * Create BlueRedDFA from red states to canonical.
 * Clean the automata from unreachable states
 *   and update the transitions.
 * @return The created DFA.
 */
gi::BlueRedDFA *gi::BlueRedDFA::to_canonical()
{
    // Count the actual number of final states.
    State n_final_states = 0;
    for (State i = 0; i < state_count(); ++i) {
        if (in_red(i)) {
            ++n_final_states;
        }
    }

    //TODO: Add the copy of the red and
    //        blue states in the vectors.

    // Create a new automaton without
    //   unreachable states.
    State count = 0;
    auto final_dfa = new BlueRedDFA(n_final_states, alphabet);
    Matrix& f_ttable = final_dfa->get_ttable();
    unordered_map<State, State> updated_transition;

    for (State i = 0; i < num_states; ++i) {
        if (in_red(i)) {
            for (Symbol j = 0; j < alphabet_count() + 1; ++j) {
                // Add the status to the new automaton
                f_ttable[count][j] = ttable[i][j];
                updated_transition[i] = count;
            }
            ++count;
        }
    }
    updated_transition[ND] = ND;

//	if(updated_transition.size() <= 2){
//		cout << "There is only one or zero red state." <<
//              " Returned a copy of original DFA." << endl;
//		delete final_dfa;
//		return new BlueRedDFA(*this);
//	}

    bool accepting_state = false;
    // Update the transitions
    for (State i = 0; i < final_dfa->state_count(); ++i)
        for (Symbol j = 0; j < final_dfa->alphabet_count(); ++j) {
            if (final_dfa->get_ttable()[i][j] == ND) {
                accepting_state = true;
            }
            // Notice that there is no missing transition,
            //   so you need a well state.
            if (updated_transition.find(final_dfa->get_ttable()[i][j]) !=
                updated_transition.end()) {
                final_dfa->set_ttable_entry(
                    i, j, updated_transition[final_dfa->get_ttable()[i][j]]);
            }
            else {
                cerr << "Error: while updating the strings." << endl;
                exit(EXIT_FAILURE);
            }

        }
    // Print the automaton before applying the well and minimizing it.
    // final_dfa->print("FINAL AUTOMATA PREACCEPT");
    // final_dfa->write_dot("FINALEPREACCEPT", perprocess.c_str());

    // final_dfa->print_dfa_dot_mapped_alphabet("FINALE_PREACCEPT",
    //  (base_path + "clean_pre_accept.dot").c_str());

    //////////////////////////////////////////////////////////////
    // Control accept states.
    // - If there are undefined transitions,
    //     all imposed on the accepting state.
    if (accepting_state) {
        auto final_accept_dfa =
            new BlueRedDFA(final_dfa->state_count() + 1,
                        final_dfa->alphabet, 0);
        Matrix &table = final_accept_dfa->get_ttable();
        for (State i = 0; i < final_dfa->state_count(); ++i) {
            for (Symbol j = 0; j < final_dfa->alphabet_count() + 1; ++j) {
                if (final_dfa->get_ttable()[i][j] == ND) {
                    table[i][j] = final_dfa->state_count();
                }
                else {
                    table[i][j] = final_dfa->get_ttable()[i][j];
                }
            }
        }
        for (Symbol j = 0; j < final_dfa->alphabet_count(); ++j) {
            table[final_dfa->state_count()][j] =
                final_dfa->state_count();
        }
        delete final_dfa;
        final_dfa = final_accept_dfa;
    }
    return final_dfa;
}

unordered_set<State> gi::BlueRedDFA::reachables()
{
    unordered_set<State> reacheable_states;
    for (State i = 0; i < num_states; ++i) {
        for (Symbol j = 0; j < alphabet_count(); ++j) {
            if (ttable[i][j] != i && ttable[i][j] != ND) {
                reacheable_states.insert(ttable[i][j]);
            }
        }
    }

    // Include the start state,
    //   not reacheable from every
    //   state by definition.
    reacheable_states.insert(start_state);
    return reacheable_states;
}

// TODO: gi::BlueRedDFA* gi::BlueRedDFA::remove_unreachable_states(){}
// TODO: void gi::BlueRedDFA::add_sink_state(){}


void gi::BlueRedDFA::add_blue(State blue_state_index)
{
    // If is not already inside, insert the new blue state
    if (!in_blue(blue_state_index)) {
        blue_states.push_back(blue_state_index);
    }
}

void gi::BlueRedDFA::add_red(State red_state_index)
{
    // If is not already inside, insert the new blue state
    if (!in_red(red_state_index)) {
        red_states.push_back(red_state_index);
    }

    // Reorder the red states list.
    // Actually there is no reason
    //   to maintain the input order.
    sort(red_states.begin(), red_states.end());
}

void gi::BlueRedDFA::remove_blue(State blue_state_index)
{
    // If blue state is inside vector, remove it
    if (in_blue(blue_state_index)) {
        blue_states.erase(remove(blue_states.begin(),
                                  blue_states.end(),
                                  blue_state_index));
    }
}

void gi::BlueRedDFA::remove_red(State red_state_index)
{
    // If red state is inside vector, remove it
    if (in_red(red_state_index))
        red_states.erase(remove(red_states.begin(),
                                 red_states.end(),
                                 red_state_index));
}

vector<State> &gi::BlueRedDFA::get_blue()
{
    return blue_states;
}

vector<State> &gi::BlueRedDFA::get_red()
{
    return red_states;
}

const vector<State> &gi::BlueRedDFA::get_blue() const
{
    return blue_states;
}

const vector<State> &gi::BlueRedDFA::get_red() const
{
    return red_states;
}

State gi::BlueRedDFA::blue_count()
{
    return static_cast<State>(blue_states.size());
}

State gi::BlueRedDFA::red_count()
{
    return  static_cast<State>(red_states.size());
}

bool gi::BlueRedDFA::in_blue(
    State blue_state_index)
{
    return find(blue_states.begin(), blue_states.end(),
                blue_state_index)
        != blue_states.end();
}

bool gi::BlueRedDFA::in_red(
    State red_state_index)
{
    return find(red_states.begin(), red_states.end(),
                red_state_index)
        != red_states.end();
}

void gi::BlueRedDFA::copy_blue(
    const vector<State> &new_blue_vector)
{
    blue_states.clear();
    blue_states = new_blue_vector;
}

void gi::BlueRedDFA::copy_red(
    const vector<State> &new_red_vector)
{
    red_states.clear();
    red_states = new_red_vector;
}

/**
 * Print the DFA with color
 * The column number includes the final
 *   column of accepting or not (accepting -> 1)
 * @param title
 */
void gi::BlueRedDFA::print(const string &title)
{
    cout << title << endl;
    ostringstream os_header;
    for (Symbol i = 0; i < alphabet_count(); ++i) {
        os_header << " | " << i;
    }
    os_header << " - A  - C";
    cout << "    " << os_header.str() << endl;
    for (State i = 0; i < num_states; ++i) {
        cout << "S" << i << "  ";
        for (Symbol j = 0; j < alphabet_count() + 1; ++j) {
            if (j < alphabet_count() && ttable[i][j] == ND) {
                cout << " N ";
            }
            else if (j < alphabet_count()) {
                cout << " " << ttable[i][j] << " ";
            }
            else if (j == alphabet_count()) // Accepting state or not.
            {
                if (is_non_accept(i)) {
                    cout << "  / ";
                }
                else if (is_accept(i)) {
                    cout << " Ac ";
                }
                else if (is_reject(i)) {
                    cout << " Rj ";
                }
                else {
                    cout << "  X ";
                }
            }
        }

        if (!in_blue(i) &&
            !in_red(i)) {
            cout << " W ";
        }
        else if (in_blue(i)) {
            cout << " B";
        }
        else {
            cout << " R";
        }

        cout << endl;
    }
}

/**
 * Print the DFA
 * The column number includes the final
 *   column of accepting or not (accepting -> 1)
 * @param title
 */
void gi::BlueRedDFA::print_alpha_map_color(
    const string &title)
{
    cout << title << endl;
    stringstream os_header;
    for (auto it : alphabet) {
        os_header << " | " << it.second;
    }
    os_header << " - A  - C";
    cout << "    " << os_header.str() << endl;
    for (State i = 0; i < num_states; ++i) {
        cout << "S" << i << "  ";
        for (Symbol j = 0; j < alphabet_count() + 1; ++j) {
            // Values of transitions, or ND or value/
            if (j < alphabet_count() && ttable[i][j] == ND) {
                cout << " N ";
            }
            else if (j < alphabet_count()) {

                auto find_it = alphabet.find(ttable[i][j]);
                if (find_it != alphabet.end()) {
                    cout << " " << find_it->second << " ";
                } else {
                    cout << " BUG ";
                }
            }
            else if (j == alphabet_count()) { // Type of state: accepting or not
                if (is_non_accept(i)) {
                    cout << "  / ";
                }
                else if (is_accept(i)) {
                    cout << " Ac ";
                }
                else if (is_reject(i)) {
                    cout << " Rj ";
                }
                else {
                    cout << "  X ";
                }
            }
        }

        if (!in_blue(i) && !in_red(i)) {
            cout << " W ";
        }
        else if (in_blue(i)) {
            cout << " B";
        }
        else {
            cout << " R";
        }
        cout << endl;
    }
}

ostream& gi::BlueRedDFA::write_dot(const string &title, ostream& os)
{
    string header = "digraph " + title + " {\n";
    string start_state = "__start0 [label=\"\" shape=\"none\"];\n\n";
    start_state = start_state + "rankdir=LR;\nsize=\"8,5\";\n\n";

    //States
    ostringstream os_states;
    string shape;
    string style;
    string color;
    for (State i = 0; i < num_states; ++i) {
        if (is_unreachable(i)) {
            continue;
        }

        if (is_accept(i)) {
            shape = "doublecircle";
            style = "rounded,filled";
            /*} else if (is_reject(i)) {
                shape = "circle";
                style = "filled";*/
        }
        else {
            shape = "circle";
            style = "filled";
        }

        if (in_red(i)) {
            color = "#ff817b";
        }
        else if (in_blue(i)) {
            color = "powderblue";
        }
        else {
            color = "white";
        }

        os_states << "s" << i
                  << " [style=\""
                  << style
                  << R"(", color="black", fillcolor=")"
                  << color
                  << "\" shape=\""
                  << shape
                  << "\", label=\""
                  << i << "\"];\n";
    }

    // Transitions
    ostringstream os_transitions;
    for (State i = 0; i < num_states; ++i) {
        for (Symbol j = 0; j < alphabet_count(); ++j) {
            State arrive_state = ttable[i][j];
            if (arrive_state == ND) {
                continue;
            }
            os_transitions
                << "s" << i
                << " -> s"
                << arrive_state
                << " [label=\"" << j
                << "\"];\n";
        }
    }
    string end = "__start0 -> 0;";
    string footer = "\n}";
    os << header << start_state << os_states.str()
           << os_transitions.str() /*<< end*/<< footer;
    return os;
}

ostream& gi::BlueRedDFA::write_alpha_map(const string &title, ostream& os)
{
    string state_name_prefix = "q";
    string header = "digraph " + title + " {\n";
    string start_state = "__start0 [style = invis, shape = none, "
        "label = \"\", width = 0, height = 0];\n\n";
    start_state = start_state + "rankdir=LR;\nsize=\"8,5\";\n\n";
    string start_arrow;
    start_arrow = "subgraph cluster_main { \n\tgraph [pad=\".75\", "
        "ranksep=\"0.15\", nodesep=\"0.15\"];\n\t style=invis; "
        "\n\t__start0 -> s0 [penwidth=2];\n}\n";

    //States
    stringstream os_states;
    string shape;
    string style;
    string color;
    for (State i = 0; i < num_states; ++i) {
        if (is_unreachable(i)) {
            continue;
        }
        if (is_accept(i)) {
            shape = "doublecircle";
            style = "rounded,filled";
            /*} else if (is_reject(i)) {
                shape = "circle";
                style = "filled";*/
        }
        else {
            shape = "circle";
            style = "filled";
        }
        if (in_red(i)) {
            color = "#ff817b";
        }
        else if (in_blue(i)) {
            color = "powderblue";
        }
        else {
            color = "white";
        }

        os_states << "s" << i << " [style=\""
                  << style << R"(", color="black", fillcolor=")"
                  << color << "\" shape=\"" << shape << "\", label=\""
                  << state_name_prefix << i << "\"];\n";
    }

    // Transition
    stringstream os_transitions;
    // The key identifies a pair of states between
    //   which there may be a transition
    // map<string, string> label_for_transiction;
    // The value is the label to be printed, containing all
    //   the symbols for which that transition takes place

    vector<vector<string>> label_for_transiction(
        num_states, vector<string>(num_states));

    for (State i = 0; i < num_states; ++i) {
        for (Symbol j = 0; j < alphabet_count(); ++j) {
            State arrive_state = ttable[i][j];
            if (arrive_state == ND) {
                continue;
            }
            string transition_symbol = "BUG";
            auto find_it = alphabet.find(j);
            if (find_it != alphabet.end()) {
                transition_symbol = ::to_string(find_it->second);
            }

            // Inserts every 7 symbols a carriage return in the label
            if (label_for_transiction[i][arrive_state].length() == 0) {
                label_for_transiction[i][arrive_state] =
                    label_for_transiction[i][arrive_state]
                        + transition_symbol;
            }
            else if (
                label_for_transiction[i][arrive_state].length() % 9 == 0) {
                label_for_transiction[i][arrive_state] =
                    label_for_transiction[i][arrive_state]
                        + "\\n" + transition_symbol;
            }
            else {
                label_for_transiction[i][arrive_state] =
                    label_for_transiction[i][arrive_state]
                        + "," + transition_symbol;
            }

            // ORIGINAL a character - a transition
            // ostringstream os_transitions;
            //   os_transitions << "s" << i << " -> s"
            //     << arrive_state
            //     << " [label=\""
            //     << inverse_mapped_alphabet[alphabet_symbols[j]]
            //     << "\"];\n";
        }
    }

    for (State i = 0; i < num_states; ++i) {
        for (State j = 0; j < num_states; ++j) {
            if (!label_for_transiction[i][j].empty()) {
                os_transitions << "s" << i
                    << " -> s" << j
                    << " [label=\""
                    << label_for_transiction[i][j]
                    << "\"];\n";
            }
        }
    }

    string end = "__start0 -> 0;";
    string footer = "\n}";
    os << header
       << start_state
       << os_states.str()
       << start_arrow
       << os_transitions.str() /*<< end*/
       << footer;
    return os;
}

ostream& gi::BlueRedDFA::write_binary(ostream& os)
{
    DFA::write_binary(os);
    write_vec(os, blue_states);
    write_vec(os, red_states);
    return os;
}

istream& gi::BlueRedDFA::read_binary(istream& is)
{
    DFA::read_binary(is);
    read_vec(is, blue_states);
    read_vec(is, red_states);
    return is;
}
