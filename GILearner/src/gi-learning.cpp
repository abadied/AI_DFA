#include <ctime>
#include <cstdio>
#include <iostream>
#include <cstring>
#include "DFA.hpp"
#include "BlueFringe.hpp"
#include "EDSM.hpp"
#include "BlueStar.hpp"
#include "LSTAR.hpp"

using namespace std;
using namespace gi;

/* The program options. */
struct prog_opt
{
    string alg_name;
    string sample_file;
    string dot_file;
} cur_prog_opt;

void
edsm_runner()
{
    EDSM edsm_solver;
    edsm_solver.read_samples(cur_prog_opt.sample_file);
    auto dfa = edsm_solver.run();
    dfa->print_dfa("EDSM-DFA");
    dfa->print_alpha_map("EDSM", cur_prog_opt.dot_file.c_str());
    cout << "dot_file: " << cur_prog_opt.dot_file << endl;
    dfa->save("dfa.dat");
    delete dfa;
}

void
blue_star()
{
    BlueStar bluestar_solver(0.05, 1000.0);
    bluestar_solver.read_samples(cur_prog_opt.sample_file);
    DFA *dfa = bluestar_solver.run();
	dfa->print_dfa("Blue*-DFA");
	dfa->print_alpha_map("Blue*", cur_prog_opt.dot_file.c_str());
    cout << "dot_file: " << cur_prog_opt.dot_file << endl;
	cout << "Error-rate: "<< bluestar_solver.get_error_rate_final_dfa() << endl;
    delete dfa;
}

void
lstar()
{
    DFA target_dfa;
    target_dfa.load("dfa.dat");
    target_dfa.print_dfa("L*-DFA");
    target_dfa.print_alpha_map("L*", cur_prog_opt.dot_file.c_str());
    cout << "dot_file: " << cur_prog_opt.dot_file << endl;

	LSTAR lstar_exe(target_dfa);
	DFA* dfa = lstar_exe.run();
    dfa->print_dfa("L*-DFA");
    dfa->print_alpha_map("L*", cur_prog_opt.dot_file.c_str());
    cout << "dot_file: " << cur_prog_opt.dot_file << endl;
    delete dfa;
}

int main(int argc, char *argv[])
{
    try {
        cur_prog_opt.alg_name = "lstar";
        cur_prog_opt.sample_file = "../examples/maor/robot_clean_before.txt";
        // cur_prog_opt.sample_file = "../examples/examples.txt";
        cur_prog_opt.dot_file = cur_prog_opt.alg_name + ".dot";

        clock_t t_start = clock();
        if (cur_prog_opt.alg_name == "edsm") {
            edsm_runner();
        } else if(cur_prog_opt.alg_name == "blue_star") {
            blue_star();
        } else if(cur_prog_opt.alg_name == "lstar") {
            /* TODO: Which DFA? */
            lstar();
        }
        cout << "Time taken: "
             << static_cast<double>((clock() - t_start) / CLOCKS_PER_SEC)
             << endl;
    }
    catch (std::exception &e) {
        cerr << "Unhandled Exception reached the top of main: "
             << e.what() << ", application will now exit" << endl;
        return 1;
    }
    return 0;
}