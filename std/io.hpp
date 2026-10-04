#pragma once

#include <iostream>
#include <string>

namespace io {

template<typename T>
inline void print(const T& value) {
    std::cout << value;
}

template<typename T>
inline void println(const T& value) {
    std::cout << value << std::endl;
}

inline std::string getln() {
    std::string value;
    std::getline(std::cin, value);
    return value;
}

}