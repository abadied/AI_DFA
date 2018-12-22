#include "DFA.hpp"

using namespace std;

/** Used for table filling algorithm. */
#define DFA_TF_STATE_N numeric_limits<Symbol>::max()
#define DFA_TF_STATE_X numeric_limits<Symbol>::max() - 1


gi::DFA::DFA(const map<Symbol, char> &alphabet): alphabet(alphabet)
 {
    num_states = 0;
    start_state = 0;
    ttable = nullptr;
}

gi::DFA::DFA(State n_state, const map<Symbol, char> &alphabet, State s_state):
    alphabet(alphabet)
{
    num_states = n_state;
    start_state = s_state;
    ttable = new State *[num_states];
    for (State i = 0; i < num_states; ++i) {
        // "+1" for Type
        ttable[i] = new Symbol[alphabet.size() + 1];
    }
    for (State i = 0; i < num_states; ++i) {
        for (Symbol j = 0; j < alphabet.size() + 1; ++j) {
            if (j >= alphabet.size()) {
                ttable[i][j] = 0;
                continue;
            }
            ttable[i][j] = ND;
        }
    }
}

gi::DFA::DFA(State n_state, const map<Symbol, char> &alphabet)
    : DFA(n_state, alphabet, 0)
{}

gi::DFA::DFA(State n_state,
             const map<Symbol, char> &alphabet,
             State s_state, const Matrix &tt_copy)
    : DFA(n_state, alphabet, s_state)
{
    for (State i = 0; i < n_state; ++i) {
        for (Symbol j = 0; j < alphabet.size() + 1; ++j) {
            ttable[i][j] = tt_copy[i][j];
        }
    }
}

// Constructor for copy
gi::DFA::DFA(const DFA &other)
    : DFA(other.num_states, other.alphabet,
          other.start_state, other.ttable)
{}

gi::DFA::~DFA()
{
    erase_ttable();
}

void gi::DFA::erase_ttable()
{
    if (ttable) {
        for (State i = 0; i < num_states; ++i) {
            if (ttable[i]) {
                delete[] ttable[i];
            }
        }
        delete[] ttable;
    }
    ttable = nullptr;
}

gi::DFA *gi::DFA::unionDFA(DFA *dfa_hp)
{
    // DFA UNION of dfa_hp e dfa_T
    State count_state = dfa_hp->num_states + num_states;
    //V cout << "Total number of states: " <<
    //          dfa_hp->num_state << " + " <<
    //          num_state << endl;

    auto dfa_unione = new DFA(count_state, alphabet);

    // fill the DFA UNION
    // The first states are of the target,
    // the remainder of the HP Automata target
    for (State j = 0; j < num_states; ++j) {
        for (Symbol k = 0; k < alphabet_count() + 1; ++k) {
            dfa_unione->ttable[j][k] = ttable[j][k];
        }
    }

    // Automata hypothesis
    for (State j = 0; j < dfa_hp->num_states; ++j) {
        // Start state of the DFA_hp in the
        //   DFA union equal to num_state of the target.
        for (Symbol k = 0; k < alphabet_count() + 1; ++k) {
            if (k != alphabet_count()) {
                dfa_unione->ttable[num_states + j][k] =
                    dfa_hp->ttable[j][k] + num_states;
            }
            else {
                dfa_unione->ttable[num_states + j][k] =
                    dfa_hp->ttable[j][k];
            }
        }
    }

    // Print DFA union
    // dfa_unione->print_dfa("*** DFA UNION ***");

    return dfa_unione;
}

/**
 * @returns: the list of equivalent states,
 *   if necessary it inserts the string
 *   against example into "witness"
 */
Symbol *gi::DFA::table_filling()
{
    // The Table considered is only the upper triangular matrix,
    // that can be saved in a linear array of size n(n-1)/2
    // Conversion of index form matrix to array are:
    //
    // From linear index k, to (i,j) for tha matrix (i row, j column)
    // i = n - 2 - floor(sqrt(-8*k + 4*n*(n-1)-7)/2.0 - 0.5)
    // j = k + i + 1 - n*(n-1)/2 + (n-i)*((n-i)-1)/2
    //
    // From (i,j) to k
    // Order such that i < j, then:
    // k = (n*(n-1)/2) - (n-i)*((n-i)-1)/2 + j - i - 1
    //
    // Refer to:
    // http://stackoverflow.com/questions/27086195/
    //        linear-index-upper-triangular-matrix)

    // *** TABLE-FILLING ALGORITHM with witness ***
    State n = num_states;
    State tf_l = (num_states * (num_states - 1)) / 2;
    // Table of distinct state pairs.
    auto distint = new Symbol[tf_l];

    // Initialization
    // for (k = 0; k < tf_l; ++k)
    // distint[k] = tableFillingState::TF_STATE_N;

    // Distinction between accepting and non-accepting
    for (State i = 0; i < (num_states - 1); ++i)
        for (State j = i + 1; j < num_states; ++j) {
            // If one is accepting while the other is not.
            State k = (n * (n - 1) / 2) - (n - i) * ((n - i) - 1) / 2 + j - i - 1;
            if (state_type(i) != state_type(j)) {
                distint[k] = DFA_TF_STATE_X;
            }
            else {
                distint[k] = DFA_TF_STATE_N;
            }
        }


    // Loop  minimizer
    // Indicate whether the table was changed during the last cycle.
    bool is_modified = true;
    while (is_modified) {
        is_modified = false;
        State arriving_state_1;
        State arriving_state_2;

        for (State i = 0; i < (num_states - 1); ++i) {
            for (State j = i + 1; j < num_states; ++j) {
                State k = (n * (n - 1) / 2) - (n - i) *
                    ((n - i) - 1) / 2 + j - i - 1;
                // V cout << endl << "SP1: "<< i << ", SP2: " << j;
                if (distint[k] == DFA_TF_STATE_N) {

                    for (Symbol w = 0; w < alphabet_count(); ++w) {
                        arriving_state_1 = ttable[i][w];
                        arriving_state_2 = ttable[j][w];

                        // The arrival status read in the DFA could
                        //   be a pair of the type (2,2)
                        if (arriving_state_1 == arriving_state_2) {
                            continue;
                        }

                        // By making the table of visited states
                        //   couples known that always j > i then
                        //   the pairs must always have the i < j
                        if (arriving_state_2 < arriving_state_1) {
                            State tmp = arriving_state_1;
                            arriving_state_1 = arriving_state_2;
                            arriving_state_2 = tmp;
                        }

                        // If already finished - go to the next iteration.
                        if (arriving_state_1 == i && arriving_state_2 == j) {
                            continue;
                        }

                        // V cout << endl <<"SA1: "<<arriving_state_1 <<
                        // ", SA2: "<<arriving_state_2 << " --> " <<
                        // distint[arriving_state_1][arriving_state_2] << endl;
                        // If the arrival torque is distinct, it is also the original one
                        State i1 = arriving_state_1, j1 = arriving_state_2;
                        State k1 = (n * (n - 1) / 2) - (n - i1) *
                            ((n - i1) - 1) / 2 + j1 - i1 - 1;

                        if (distint[k1] != DFA_TF_STATE_N) {
                            // TODO: Is it correct?
                            // writes the index (in char) of the letter of the
                            //   alphabet for which the two states differ
                            // distint[k1] = w + '0';
                            // distint[k] = tableFillingState::TF_STATE_O;
                            distint[k] = w;
                            is_modified = true;
                            // Note the break here is needed!
                            break;
                        }
                    }
                }
            }
        }
    }

    // print the table of distinct states
#ifdef DEBUG_2
    cout << "--------------------------" << endl
         << " Table of Distinct States " << endl
         << "--------------------------" << endl;
    for(i = 0; i < (num_states - 1); ++i) {
        for(j = i + 1; j < num_states; ++j) {
            k = (n * (n - 1) / 2) - (n - i) * ((n - i) - 1) / 2 + j - i - 1;
            char toprint = (distint[k] == DFA_TF_STATE_X)? 'X':
                    (distint[k]==DFA_TF_STATE_N)? '@':
                        static_cast<char>(distint[k] + 48);
            cout << "(" << i << "," << j << "):" << toprint << "  ";
        }
        cout << endl;
    }
    cout << "--------------------------" << endl;
#endif
    return distint;
}

gi::DFA *gi::DFA::minimize_TF()
{
    // Matrix distinct: table for record distinct states
    auto distinct = new bool*[num_states - 1];
    // EX: For 6 states: 5 rows and 6 columns (of these 6
    //       only 5 actually used, but needed)
    for (State i = 0; i < num_states - 1; ++i) {
        distinct[i] = new bool[num_states];
    }

    // Initialization of distinct table
    for (State i = 0; i < num_states - 1; ++i) {
        for (State j = 0; j < num_states; ++j) {
            distinct[i][j] = false;
        }
    }

    // Distinction between accepting and non-accepting
    // EX: 0 <= i <= 4, j = i + 1 (1 <= j <= 5 for the first iteration)
    for (State i = 0; i < (num_states - 1); ++i) {
        for (State j = i + 1; j < num_states; ++j) {
            // If one is accepting while the other is not.
            if (state_type(i) != state_type(j)) {
                distinct[i][j] = true;
            }
        }
    }

    // Loop  minimizer
    bool is_modified = true;
    while (is_modified) {
        is_modified = false;
        for (State i = 0; i < (num_states - 1); ++i) {
            for (State j = i + 1; j < num_states; ++j) {
                if (!distinct[i][j]) {
                    for (Symbol k = 0; k < alphabet_count(); ++k) {
                        State arriving_state_1 = ttable[i][k];
                        State arriving_state_2 = ttable[j][k];
                        if (arriving_state_1 == arriving_state_2) {
                            continue;
                        }

                        // Making the table of visited states
                        //   couples known that always j > i
                        if (arriving_state_2 < arriving_state_1) {
                            State tmp = arriving_state_1;
                            arriving_state_1 = arriving_state_2;
                            arriving_state_2 = tmp;
                        }

                        // If the arrival torque is distinct,
                        //   it is also the original one.
                        if (distinct[arriving_state_1][arriving_state_2]) {
                            distinct[i][j] = true;
                            is_modified = true;
                        }
                    }
                }
            }
        }
    }

    // Prepare to build the minimized automaton, create a list
    //   to have a list of pairs of equivalent states more
    //   directly accessible, if it is ND then
    //   it does not have an equivalent.
    auto eq_state = new State[num_states];
    for (State i = 0; i < num_states; ++i) {
        eq_state[i] = ND;
    }

    // count the number of final states,
    //   and assign to each state
    //   its possible equivalent status
    //   (must also check in the
    //   case of (0,4) (0,5) that when meet (4,5)
    //   do not count it as a further state in less)
    State final_state = num_states;
    for (State i = 0; i < (num_states - 1); ++i) {
        for (State j = i + 1; j < num_states; ++j) {
            if (!distinct[i][j] &&
                eq_state[i] == ND &&
                eq_state[j] == ND) {
                eq_state[j] = i;
                --final_state;
            }
        }
    }

    // Print information about equivalent states found or not
    /*//V cout << "N of final states: " << final_state << endl;
    cout << "Equivalent states: " << endl;
    for(State i = 0; i < num_state; ++i) {
        if(eq_state[i] != ND) {
            cout << "S:" << i << " --> "
                 << eq_state[i] << endl;
        } else {
            cout << "S:" << i << endl;
        }
    */

    // Print the old DFA
#ifdef DEBUG_2
    this->print_dfa("DFA BEFORE MINIMIZATION");
#endif

    // Instantiate the new minimized DFA.
    auto *dfa_min = new DFA(final_state,
                            alphabet, 0);
    Matrix &ttable_min = dfa_min->get_ttable();
    State count = 0;
    for (State i = 0; i < num_states; ++i) {
        if (eq_state[i] == ND) {
            for (Symbol j = 0; j < alphabet_count() + 1; ++j) {
                ttable_min[count][j] = ttable[i][j];
            }
            ++count;
        }
    }

    // Update the transitions
    //   to states now disappeared
    //   because replaced with
    //   equivalents.
    State post_equivalences = 0;
    for (State i = 0; i < num_states; ++i) {
        if (eq_state[i] != ND) {
            for (State k = 0; k < final_state; ++k) {
                for (Symbol t = 0;
                     t < alphabet_count(); ++t) {
                    // Replace the transition
                    //   to the "i" state with
                    //   the equivalent status
                    //   "eq_state [i]"
                    if (ttable_min[k][t] == i) {
                        ttable_min[k][t] = eq_state[i];
                    }
                }
            }
        }
    }

    // Update the label, because if for example:
    //   collapsed 2 states before state 6, now the
    //   state 6 is in line 4, but the transitions
    //   are left towards 6 and must be placed.
    for (State i = 0; i < num_states; ++i) {
        if (eq_state[i] != ND) {
            ++post_equivalences;
        }

        if (post_equivalences != 0) {
            State new_label = i - post_equivalences;
            for (State k = 0; k < final_state; ++k) {
                for (Symbol t = 0; t < alphabet_count(); ++t) {
                    if (ttable_min[k][t] == i) {
                        ttable_min[k][t] = new_label;
                    }
                }
            }
        }
    }

    // Print the minimized DFA.
#ifdef DEBUG_2
    dfa_min->print_dfa("MINIMIZED DFA");
#endif

    // Free allocations.
    for (State i = 0; i < num_states - 1; ++i) {
        delete[] distinct[i];
    }

    delete[] eq_state;
    delete[] distinct;

    return dfa_min;
}

/** Print the DFA
 *  The column number includes the final column of
 *    accepting status or not (accept -> 1)
 * @param title The title of the dfa.
 */
void gi::DFA::print_dfa(const string &title)
{
    cout << title << endl;
    ostringstream os_header;
    for (Symbol i = 0;
         i < alphabet_count(); ++i) {
        os_header << " | " << i;
    }
    os_header << " - A";
    cout << "  " << os_header.str() << endl;
    for (State i = 0; i < num_states; ++i) {
        cout << "S" << i << "  ";
        for (Symbol j = 0; j < alphabet_count() + 1; ++j) {
            // Values of transitions, or ND or value.
            if (j < alphabet_count() && ttable[i][j] == ND) {
                cout << " N ";
            }
            else if (j < alphabet_count()) {
                cout << " " << ttable[i][j] << "  ";
                // Status type: accept/reject
            }
            else if (j == alphabet_count()) {
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
        cout << endl;
    }
}

/** The DFA string.
 *  The column number includes the final column of
 *    accepting status or not (accept -> 1)
 * @param title The title of the dfa.
 */
string gi::DFA::dfa()
{
    ostringstream os_header;
    os_header << "  ";
    for (Symbol i = 0; i < alphabet_count(); ++i) {
        os_header << " | " << i;
    }
    os_header << " - A";
    os_header << endl;
    for (State i = 0; i < num_states; ++i) {
        os_header << "S" << i << "  ";
        for (Symbol j = 0; j < alphabet_count() + 1; ++j) {
            // Values of transitions, or ND or value.
            if (j < alphabet_count() && ttable[i][j] == ND) {
                os_header << " N ";
            }
            else if (j < alphabet_count()) {
                os_header << " " << ttable[i][j] << "  ";
                // Status type: accept/reject
            }
            else if (j == alphabet_count()) {
                if (is_non_accept(i)) {
                    os_header << "  / ";
                }
                else if (is_accept(i)) {
                    os_header << " Ac ";
                }
                else if (is_reject(i)) {
                    os_header << " Rj ";
                }
                else {
                    os_header << "  X ";
                }
            }
        }
        os_header << endl;
    }
    return os_header.str();
}

/**
 * Print the DFA
 * The column number includes the final column
 *   of status acceptor or not (acceptor -> 1)
 *   Use the original alphabet
 * @param title The DFA title.
 */
void gi::DFA::print_alph_dfa(const string &title)
{
    /*
    cout << "Correct reverse mappings? " << endl;
    for (map<SymbolType, Symbol>::const_iterator p1 =
         inverse_mapped_alphabet.begin();
         p1 != inverse_mapped_alphabet.end(); ++p1) {
        cout << (*p1).first << "; "
             << (*p1).second << endl;
    }
    cout << "FINE" << endl;
    */

    ostringstream os_header;
    for (auto it : alphabet) {
        os_header << " | " << it.second;
    }
    os_header << " - A";
    cout << "  " << os_header.str() << endl;

    for (State i = 0; i < num_states; ++i) {
        cout << "S" << i << "  ";
        for (Symbol j = 0; j < alphabet_count() + 1; ++j) {
            // Values of transitions, or ND or value.
            if (j < alphabet_count() &&
                ttable[i][j] == ND) {
                cout << " N ";
            }
            else if (j < alphabet_count()) {
                auto find_it = alphabet.find(ttable[i][j]);
                if (find_it != alphabet.end()) {
                    cout << " " << find_it->second << "  ";
                } else {
                    cout << " BUG  ";
                }

            }
            else if (j == alphabet_count()) {
                // Status type: accept/reject
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
        cout << endl;
    }
}

/**
* A dot file string for the current dfa using the alphabet symbols,
*   with title "title", in the path "file_path".
* @param title	Title printed before the transition table
* @param file_path Path where make a dot file
*/
string gi::DFA::dot()
{
    ostringstream os;
    write_alpha_map("DFA", os);
    return os.str();
}

void gi::DFA::set_ttable(Matrix &ext_ttable)
{
    ttable = ext_ttable;
}

Matrix &gi::DFA::get_ttable()
{
    return ttable;
}

State gi::DFA::get_ttable(State i, Symbol j)
{
    if (i < num_states && j < alphabet_count() + 1) {
        return ttable[i][j];
    }
    else {
        cerr << "DFA::get_ttable: out of bound" << endl;
        exit(EXIT_FAILURE);
    }
}

void gi::DFA::set_ttable_entry(State i, Symbol j, State v)
{
    if (i < num_states && j < alphabet_count() + 1) {
        ttable[i][j] = v;
    }
    else {
        cerr << "DFA::set_ttable: out of bound" << endl;
        exit(EXIT_FAILURE);
    }
}

Symbol gi::DFA::alphabet_count()
{
    return static_cast<Symbol>(alphabet.size());
}

State gi::DFA::state_count()
{
    return num_states;
}

State gi::DFA::get_start_state()
{
    return start_state;
}

void gi::DFA::save_dot(const string &title, const char *file_path)
{
    ofstream myfile;
    myfile.open(file_path);
    write_dot(title, myfile);
    myfile.close();
}

ostream& gi::DFA::write_binary(ostream& os)
{
    write_value(os, num_states);
    write_value(os, start_state);
    write_map(os, alphabet);
    for (State i = 0; i < num_states; ++i) {
        write_arr(os, ttable[i], alphabet_count() + 1);
    }
    return os;
}

istream& gi::DFA::read_binary(istream& is)
{
    read_value(is, num_states);
    read_value(is, start_state);
    read_map(is, alphabet);
    swap_key_values(alphabet, mapped_alphabet);
    erase_ttable();
    try {
        ttable = new State*[num_states];
        /* First we initialize all the pointer to null in
         *   case of memory errors. */
        for (State i = 0; i < num_states; ++i) {
            ttable[i] = nullptr;
        }
        for (State i = 0; i < num_states; ++i) {
            ttable[i] = new Symbol[alphabet_count() + 1];
            read_arr(is, ttable[i], alphabet_count() + 1);
        }
    } catch (bad_alloc& ba) {
        cerr << "Failed to allocate memory for alphabet.:"
             << ba.what() << endl;
        erase_ttable();
    }
    return is;
}

bool gi::DFA::save(const char *file_path)
{
    bool success = true;

    ofstream dfa_file;
    dfa_file.open(file_path, ios::out | ios::binary);
    write_binary(dfa_file);
    success &= dfa_file.good();
    dfa_file.close();

    return success;
}


bool gi::DFA::load(const char *file_path)
{
    bool success = true;

    ifstream dfa_file;
    dfa_file.open(file_path, ios::in | ios::binary);
    read_binary(dfa_file);
    success &= dfa_file.good();
    dfa_file.close();

    return success;
}

string gi::DFA::save_to_string()
{
    ostringstream dfa_ss;
    write_binary(dfa_ss);
    return dfa_ss.str();
}


bool gi::DFA::loadfrom_string(const char *dfa_buffer)
{
    bool success = true;
    istringstream dfa_ss(dfa_buffer);
    read_binary(dfa_ss);
    success &= dfa_ss.good();
    return success;
}

ostream& gi::DFA::write_dot(const string &title, ostream& os)
{
    string header = "digraph " + title + " {\n";
    string start_state = "__start0 [label=\"\" shape=\"none\"];\n\n";
    start_state = start_state + "rankdir=LR;\nsize=\"8,5\";\n\n";

    // States
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

        color = "white";
        os_states << "s" << i << " [style=\""
                  << style << R"(", color="black", fillcolor=")"
                  << color << "\" shape=\""
                  << shape << "\", label=\""
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
                << " [label=\""
                << j << "\"];\n";
        }
    }
    string end = "__start0 -> 0;";
    string footer = "\n}";
    os << header
       << start_state
       << os_states.str()
       << os_transitions.str()
       /* << end */
       << footer;
    return os;
}


void gi::DFA::print_alpha_map(const string &title, const char *file_path)
{
    ofstream myfile;
    myfile.open(file_path);
    write_alpha_map(title, myfile);
    myfile.close();
}


ostream& gi::DFA::write_alpha_map(const string &title, ostream& os)
{
    string state_name_prefix = "q";
    string header = "digraph " + title + " {\n";
    string start_state = "__start0 [style = invis, shape = none, "
        "label = \"\", width = 0, height = 0];\n\n";
    start_state = start_state + "rankdir=LR;\nsize=\"8,5\";\n\n";
    string start_arrow;
    start_arrow = "subgraph cluster_main { \n\tgraph [pad=\".75\", "
        "ranksep=\"0.15\", nodesep=\"0.15\"];\n\t style=invis; \n"
        "\t__start0 -> s0 [penwidth=2];\n}\n";

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
            // Uncomment for different reject style
            /* } else if (is_reject(i)) {
                shape = "circle";
                style = "filled";
              */
        }
        else {
            shape = "circle";
            style = "filled";
        }

        color = "white";
        os_states << "s" << i
                  << " [style=\""
                  << style
                  << R"(", color="black", fillcolor=")"
                  << color
                  << "\" shape=\""
                  << shape
                  << "\", label=\""
                  << state_name_prefix
                  << i << "\"];\n";
    }

    // Transitions
    ostringstream os_translations;
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

            if (label_for_transiction[i][arrive_state].empty()) {
                label_for_transiction[i][arrive_state] =
                    label_for_transiction[i][arrive_state]
                        + transition_symbol;
                // Inserts every 7 symbols a carriage return in the label
            }
            else if (label_for_transiction[i][arrive_state].length() % 9 == 0) {
                label_for_transiction[i][arrive_state] =
                    label_for_transiction[i][arrive_state] +
                        "\\n" + transition_symbol;
            }
            else {
                label_for_transiction[i][arrive_state] =
                    label_for_transiction[i][arrive_state] +
                        "," + transition_symbol;
            }

            // ORIGINAL a character - a transition
            // ostringstream os_transitions;
            //   os_transitions << "s"
            //     << i << " -> s"
            //     << arrive_state
            //     << " [label=\"" +
            //     << inverse_mapped_alphabet[alphabet_symbols[j]]
            //     << "\"];\n";
        }
    }

    for (State i = 0; i < num_states; ++i) {
        for (State j = 0; j < num_states; ++j) {
            if (!label_for_transiction[i][j].empty()) {
                os_translations
                    << "s" << i
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
       << os_translations.str() /*<< end*/
       << footer;
    return os;
}

void gi::DFA::set_num_state(State n)
{
    num_states = n;
}

/* TODO: Alphabet is fixed and should not get copied each time. */
//void gi::DFA::set_alphabet(const map<Symbol, char> &alphabet)
//{
//    // Erase the existing alphabet
//    alphabet.clear();
//
//    // Instance for new alphabet
//    alphabet = alphabet;
//
//    // Copy alphabet in input to
//    //   alphabet for current DFA
//    //   inside mapped_alphabet
//    //   for every symbol
//    //   there is the associated
//    //   index.
//    for (Symbol i = 0;
//         i < alphabet_count(); ++i) {
//        alphabet[i] = alphabet[i];
//        mapped_alphabet[alphabet[i]] = i;
//    }
//
//}
//

State gi::DFA::get_arrive_state(
    const SymbolString &dfa_string)
{
    State state = 0;
    State next_state;
    for (Symbol i : dfa_string) {
        next_state = ttable[state][i];
        if (next_state == ND) {
            state = ND;
            break;
        }
        state = next_state;
    }

    // Returns ND if the string is
    //   not compatible, otherwise it
    //   returns the state where
    //   the string ends.
    return state;
}

SymbolString gi::DFA::equivalence_query(DFA *dfa_hp)
{
    SymbolString witness;

#ifdef DEBUG_2
    cout << endl << "--------------------------" << endl;
    cout << "EQUIVALENCE QUERY" << endl;
    cout << "--------------------------" << endl;
#endif
    // Build union DFA of target DFA (this-one) and dfa_hp
    DFA *dfa_union = this->unionDFA(dfa_hp);
#ifdef DEBUG_2
    dfa_union->print_dfa("DFA UNION");
#endif


    // Table-filling algorithm on union DFA
    Symbol *distincts_table = dfa_union->table_filling();

    // Extract list of equivalent states
    //   from table of distinct states,
    //   every vector contain a list of
    //   equivalent states for the state
    //   that correspond to the vector.
    vector<State> *equivalent_states_list =
        dfa_union->table_eq_states(distincts_table);

    // Verify if start states of DFA's are equivalent:
    // Check if among the states equivalent
    //   to state 0 (initial state of the
    //   current automaton)
    //   there is the initial state of the
    //   hypothesis hypothesis identified
    //   by the "num_state" index.
    // In case it is present, not in the if and only if,
    //   and return an empty vector as a counterexample.
    // If this were not the case (this is the case
    //   of the "end ()"), hence generates a counterexample.
    if (equivalent_states_list[0].end() ==
        find(equivalent_states_list[0].begin(),
             equivalent_states_list[0].end(), num_states)) {
        witness = dfa_union->witness_from_table(
            distincts_table, num_states);
    }

    // Free allocated memory.
    delete[] distincts_table;
    delete[] equivalent_states_list;
    delete dfa_union;
    return witness;
}

bool gi::DFA::membership_query(const SymbolString &str)
{
    // Check if arrive_state is ND
    //   (for DFA without sink state)
    State arrive_state = get_arrive_state(str);
    return arrive_state != ND && is_accept(arrive_state);
}

/**
 * Call it in a DFA union
 * @param distinct
 * @param start_state_dfa_hp
 * @return
 */
SymbolString gi::DFA::witness_from_table(
    const Symbol *distinct,
    State start_state_dfa_hp)
{
    // If non-equivalent automata, create witness.
    SymbolString wit;
    State i_couple = 0;
    State j_couple = start_state_dfa_hp;
    Symbol input;

#ifdef DEBUG_2
    cout << "--- Create the counter example --- "
         << endl;
#endif

    while (true) {
        //V cout << "Couples: " << i_couple
        //       << "," << j_couple
        //       << "; vale: "
        //       << distinct[i_couple][j_couple]
        //       << endl;
        State n = num_states;
        State k = (n * (n - 1) / 2) -
            (n - i_couple) * ((n - i_couple) - 1) / 2 +
            j_couple - i_couple - 1;

        if (distinct[k] == DFA_TF_STATE_N) {
            cout << "PROBLEM! Counter-example request"
                " with equivalent automata";
        }

        input = distinct[k];
        // Case in which the start state of 2,
        //   one is accept and the other is not.
        if (input == DFA_TF_STATE_X) {
            break;
        }

        //V cout << "partial hesitation: " << wit <<
        //          " + " << input << endl;
        // TODO: is pushing rather than
        //   concatenation correct?
        //   old: wit = wit + input;
        wit.push_back(input);
        //V cout << "Vale: "<< input << ", ascii: "<<
        // static_cast<Symbol>(input) << ", diff_i:" <<
        // static_cast<Symbol>(input) - 48 << endl;

        i_couple = ttable[i_couple][input];
        j_couple = ttable[j_couple][input];

        if (distinct[k] == DFA_TF_STATE_X) {
            //V cout << "Fin string" << endl;
            break;
        }
    }

#ifdef DEBUG_2
    cout << "Counter example is: "<< wit << endl;
#endif
    return wit;
}

vector<State> *gi::DFA::table_eq_states(
    const Symbol *distincts)
{
#ifdef DEBUG_2
    cout << endl
         << "--------------------------" << endl;
         << "List of equivalent states:" << endl;
         << "--------------------------" << endl;
#endif
    auto *eq_states = new vector<State>[num_states];
    State n = num_states;
    for (State i = 0; i < (num_states - 1); ++i) {
        for (State j = i + 1; j < num_states; ++j) {
            State k = (n * (n - 1) / 2) - (n - i) *
                ((n - i) - 1) / 2 + j - i - 1;
            if (distincts[k] == DFA_TF_STATE_N) {
                eq_states[i].push_back(j);
            }
        }
    }

#ifdef DEBUG_2
    cout << "N The final states: " <<
            num_states << endl;
    for (State i = 0; i < num_states; ++i) {
        cout << "S[" << i << "] --> "
             << eq_states[i] << endl;
    }
    cout << "--------------------------" << endl;
#endif
    return eq_states;
}

double gi::DFA::get_complexity()
{
    return num_states;
}