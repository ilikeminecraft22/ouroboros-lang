#pragma once
#include <cstdint>
#include <string>

#define HASH_DEFAULT_SEED 0xFF22AA11EE33BB88

namespace alg_common_ {
    inline uint64_t sh64(const std::string &input, uint64_t seed) { // sh64 - small hash 64-bit
        uint64_t output = seed >> 4; //                         NOT cryptographically secure
        //                                                      I didnt test for any safety flaws so dont use it for security
        for (char c : input) {
            output ^= (seed >> 1) + static_cast<uint8_t>(c);
            output <<= 2;
            output >>= (static_cast<uint8_t>(c) & 0x07);
            output ^= output >> 32;
            output *= output;
        }
        output += seed;
        output ^= output >> 16;
        return output;
    }
}