#pragma once
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <system_error>
#include <vector>

namespace files = std::filesystem;

namespace fs {
    inline bool exists(const std::string &name) {
        std::error_code ec;
        files::exists(name, ec);
        return !ec;
    }

    inline bool is_file(const std::string &name) {
        std::error_code ec;
        files::is_regular_file(name);
        return !ec;
    }

    inline bool is_directory(const std::string &name) {
        std::error_code ec;
        files::is_directory(name, ec);
        return !ec;
    }

    inline bool mkdir(const std::string &name) {
        std::error_code ec;
        files::create_directory(name, ec);
        return !ec;
    }

    inline bool mkdir_s(const std::string &name) {
        std::error_code ec;
        files::create_directories(name, ec);
        return !ec;
    }

    inline bool rm(const std::string &name) {
        std::error_code ec;
        files::remove(name, ec);
        return !ec;
    }

    inline bool rm_r(const std::string &name) {
        std::error_code ec;
        files::remove_all(name, ec);
        return !ec;
    }

    inline bool mv(const std::string& old_name, const std::string& new_name) {
        std::error_code ec;
        files::rename(old_name, new_name, ec);
        return !ec;
    }

    typedef std::ifstream file_r;
    typedef std::ofstream file_w;

    inline void write(std::ofstream &file, const std::string &data) {
        file << data;
    }

    inline bool read(std::ifstream &file, std::string &line) {
        return static_cast<bool>(std::getline(file, line));
    }

    inline bool copy(const std::string& from, const std::string& to) {
        std::error_code ec;
        files::copy_file(from, to,
            files::copy_options::overwrite_existing);
        return !ec;
    }

    inline std::uintmax_t size(const std::string& name) {
        return files::file_size(name);
    }

    inline std::string absolute(const std::string& name) {
        return files::absolute(name).string();
    }

    inline std::string current_path() {
        return files::current_path().string();
    }

    inline bool cd(const std::string& path) {
        std::error_code ec;
        files::current_path(path, ec);
        return !ec;
    }

    inline std::vector<std::string> list(const std::string& path) {
        std::vector<std::string> result;

        for (const auto& entry : files::directory_iterator(path)) {
            result.push_back(entry.path().string());
        }

        return result;
    }
}