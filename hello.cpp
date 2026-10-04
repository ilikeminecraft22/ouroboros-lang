#include <ouroboros/io.hpp>
#include <ouroboros/rng.hpp>

int main(int argc, char** argv) {
    while (true) {
        io::println(rng::int_range(0, 70));
        io::getln();
    }
    return 0;
}
