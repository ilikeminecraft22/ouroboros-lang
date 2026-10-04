#pragma once
#include <cstdlib>
#include <string>
#include <unistd.h>
#include <sys/wait.h>

namespace sys {
    inline void command(std::string s) {
        std::system(s.c_str());
    }

    inline int jump(const std::string& program, const char* args[])
    {
        pid_t pid = fork();

        if (pid == -1)
            return -1;

        if (pid == 0) {
            execvp(program.c_str(), const_cast<char* const*>(args));

            _exit(127);
        }

        int status;
        waitpid(pid, &status, 0);

        if (WIFEXITED(status))
            return WEXITSTATUS(status);

        if (WIFSIGNALED(status))
            return 128 + WTERMSIG(status);

        return -1;
    }
}