#include <windows.h>
void mainCRTStartup(void) {
    DWORD written = 0;
    char text[] = "ACP=0000\r\n";
    unsigned cp = GetACP();
    HANDLE file;
    text[4] = '0' + cp / 1000 % 10;
    text[5] = '0' + cp / 100 % 10;
    text[6] = '0' + cp / 10 % 10;
    text[7] = '0' + cp % 10;
    file = CreateFileA("native-probe.txt", GENERIC_WRITE, FILE_SHARE_READ, 0, CREATE_ALWAYS, 0, 0);
    if (file == INVALID_HANDLE_VALUE) ExitProcess(1);
    if (!WriteFile(file, text, 10, &written, 0) || written != 10) ExitProcess(2);
    CloseHandle(file);
    ExitProcess(0);
}
