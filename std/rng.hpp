#pragma once

#include <random>

namespace rng {
    inline int int_range(int min, int max) {
        static std::random_device rd;
        static std::mt19937 generator(rd());

        std::uniform_int_distribution<int> distribution(min, max);

        return distribution(generator);
    }

    inline double float_range(double min, double max) {
        static std::random_device rd;
        static std::mt19937 generator(rd());

        std::uniform_real_distribution<double> distribution(min, max);

        return distribution(generator);
    }
}